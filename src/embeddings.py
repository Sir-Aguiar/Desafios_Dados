"""
Geracao e armazenamento de embeddings (RF08).

Monta o texto a partir do titulo e da descricao de cada conteudo
valido, gera o vetor com sentence-transformers, associa ao
conteudo_id e grava em PostgreSQL/pgvector.
"""
import re
from datetime import datetime
from pathlib import Path
import logging

import pandas as pd
from sqlalchemy import create_engine, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

from src.config import RAIZ_PROJETO, load_config, postgres_url
from src.logger import get_logger
from src.models import Conteudo, EmbeddingConteudo

CAMINHO_DDL = RAIZ_PROJETO / "sql" / "criar_embeddings.sql"


def _eh_nulo(valor):
    if valor is None:
        return True
    try:
        resultado = pd.isna(valor)
    except (ValueError, TypeError):
        return False
    return bool(resultado) if not hasattr(resultado, "__len__") else False


def _como_texto(valor):
    if _eh_nulo(valor):
        return None
    texto = str(valor).strip()
    return texto if texto else None


def representar_texto(titulo, descricao=None):
    """Concatena titulo e descricao na representacao textual do conteudo."""
    partes = []
    titulo_limpo = _como_texto(titulo)
    if titulo_limpo:
        partes.append(titulo_limpo)
    descricao_limpa = _como_texto(descricao)
    if descricao_limpa:
        partes.append(descricao_limpa)
    return "\n\n".join(partes)


class GeradorEmbeddings:
    """Gera embeddings dos conteudos persistidos e grava em embedding_conteudo."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = load_config()
        pg = self.config["postgres"]
        if not pg.get("user") or not pg.get("dbname"):
            raise RuntimeError(
                "Credenciais PostgreSQL ausentes no .env "
                "(POSTGRES_USER / POSTGRES_DB)."
            )

        emb = self.config["embeddings"]
        self.modelo_nome = emb["modelo"]
        self.dimensao = int(emb["dimensao"])
        cache = emb.get("diretorio_cache") or "./.cache/embeddings"
        caminho_cache = Path(cache)
        if not caminho_cache.is_absolute():
            caminho_cache = RAIZ_PROJETO / caminho_cache
        self.diretorio_cache = caminho_cache
        self._modelo = None

        self.engine = create_engine(postgres_url(self.config), pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def gerar(self):
        """Gera (ou reaproveita) um embedding por conteudo valido e persiste."""
        self.logger.info(
            "Modelo de embeddings: " + self.modelo_nome + " (dimensao=" + str(self.dimensao) + ")"
        )
        try:
            self._testar_conexao()
        except Exception:
            self.logger.exception("Falha de conexao com o PostgreSQL na geracao de embeddings")
            raise

        try:
            self._aplicar_ddl()
        except Exception:
            self.logger.exception(
                "Falha na geracao de embeddings ao aplicar o DDL em " + str(CAMINHO_DDL)
            )
            raise

        session = self.SessionLocal()
        try:
            conteudos = session.execute(
                select(Conteudo.conteudo_id, Conteudo.titulo, Conteudo.descricao).order_by(
                    Conteudo.conteudo_id
                )
            ).all()
            if not conteudos:
                self.logger.warning(
                    "Nenhum conteudo valido no PostgreSQL; embeddings nao gerados."
                )
                return {
                    "modelo": self.modelo_nome,
                    "dimensao": self.dimensao,
                    "conteudos_validos": 0,
                    "gerados": 0,
                    "reaproveitados": 0,
                    "ignorados_sem_texto": 0,
                }

            existentes = {
                row.conteudo_id: (row.modelo, row.texto_origem)
                for row in session.execute(
                    select(
                        EmbeddingConteudo.conteudo_id,
                        EmbeddingConteudo.modelo,
                        EmbeddingConteudo.texto_origem,
                    )
                ).all()
            }

            pendentes = []
            reaproveitados = 0
            ignorados = 0
            for cid, titulo, descricao in conteudos:
                texto = representar_texto(titulo, descricao)
                if not texto:
                    ignorados += 1
                    self.logger.warning(
                        "Conteudo " + str(cid) + " sem titulo/descricao; embedding ignorado"
                    )
                    continue
                atual = existentes.get(cid)
                if atual and atual[0] == self.modelo_nome and atual[1] == texto:
                    reaproveitados += 1
                    continue
                pendentes.append({"conteudo_id": int(cid), "texto_origem": texto})

            self.logger.info(
                "Conteudos validos="
                + str(len(conteudos))
                + ", pendentes="
                + str(len(pendentes))
                + ", reaproveitados="
                + str(reaproveitados)
                + ", ignorados_sem_texto="
                + str(ignorados)
            )

            if pendentes:
                dim_antes = self.dimensao
                self._carregar_modelo()
                if self.dimensao != dim_antes:
                    session.rollback()
                    self._aplicar_ddl()
                    pendentes = []
                    reaproveitados = 0
                    for cid, titulo, descricao in conteudos:
                        texto = representar_texto(titulo, descricao)
                        if not texto:
                            continue
                        pendentes.append(
                            {"conteudo_id": int(cid), "texto_origem": texto}
                        )
                    self.logger.info(
                        "Tabela recriada na dimensao "
                        + str(self.dimensao)
                        + "; regenerando "
                        + str(len(pendentes))
                        + " embeddings"
                    )

                vetores = self._encode([item["texto_origem"] for item in pendentes])
                agora = datetime.now()
                linhas = []
                for item, vetor in zip(pendentes, vetores):
                    linhas.append(
                        {
                            "conteudo_id": item["conteudo_id"],
                            "texto_origem": item["texto_origem"],
                            "modelo": self.modelo_nome,
                            "vetor": [float(x) for x in vetor],
                            "gerado_em": agora,
                        }
                    )
                self._upsert(session, linhas)
                session.commit()
            else:
                self.logger.info(
                    "Nenhum embedding novo a gerar; todos ja estavam associados."
                )

            relatorio = {
                "modelo": self.modelo_nome,
                "dimensao": self.dimensao,
                "conteudos_validos": len(conteudos),
                "gerados": len(pendentes),
                "reaproveitados": reaproveitados,
                "ignorados_sem_texto": ignorados,
            }
            self._consultar(session, relatorio)
            return relatorio
        except Exception:
            session.rollback()
            self.logger.exception("Falha na geracao de embeddings")
            raise
        finally:
            session.close()

    def _testar_conexao(self):
        with self.engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")

    def _aplicar_ddl(self):
        if not CAMINHO_DDL.exists():
            raise FileNotFoundError("Script SQL nao encontrado: " + str(CAMINHO_DDL))
        sql = CAMINHO_DDL.read_text(encoding="utf-8").replace(
            "__DIMENSAO__", str(self.dimensao)
        )
        raw = self.engine.raw_connection()
        try:
            with raw.cursor() as cur:
                dim_atual = self._dimensao_tabela(cur)
                if dim_atual is not None and dim_atual != self.dimensao:
                    self.logger.warning(
                        "Dimensao da tabela embedding_conteudo ("
                        + str(dim_atual)
                        + ") difere da configurada ("
                        + str(self.dimensao)
                        + "). Recriando a tabela."
                    )
                    cur.execute("DROP TABLE IF EXISTS embedding_conteudo CASCADE")
                cur.execute(sql)
            raw.commit()
            self.logger.info(
                "DDL vetorial aplicado: "
                + CAMINHO_DDL.name
                + " (vector("
                + str(self.dimensao)
                + "))"
            )
        except Exception:
            raw.rollback()
            raise
        finally:
            raw.close()

    @staticmethod
    def _dimensao_tabela(cur):
        cur.execute("SELECT to_regclass('public.embedding_conteudo')")
        if cur.fetchone()[0] is None:
            return None
        cur.execute(
            """
            SELECT format_type(a.atttypid, a.atttypmod)
            FROM pg_attribute a
            WHERE a.attrelid = 'public.embedding_conteudo'::regclass
              AND a.attname = 'vetor'
              AND NOT attisdropped
            """
        )
        tipo = cur.fetchone()
        if not tipo or not tipo[0]:
            return None
        encontrado = re.search(r"vector\((\d+)\)", tipo[0])
        return int(encontrado.group(1)) if encontrado else None

    def _carregar_modelo(self):
        if self._modelo is not None:
            return self._modelo
        self.diretorio_cache.mkdir(parents=True, exist_ok=True)
        self.logger.info("Carregando modelo de embeddings: " + self.modelo_nome)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
        try:
            from sentence_transformers import SentenceTransformer

            self._modelo = SentenceTransformer(
                self.modelo_nome,
                cache_folder=str(self.diretorio_cache),
            )
        except Exception:
            self.logger.exception(
                "Falha na geracao de embeddings ao carregar o modelo " + self.modelo_nome
            )
            raise
        dim_real = (
            self._modelo.get_embedding_dimension()
            if hasattr(self._modelo, "get_embedding_dimension")
            else self._modelo.get_sentence_embedding_dimension()
        )
        if dim_real != self.dimensao:
            self.logger.warning(
                "Dimensao configurada ("
                + str(self.dimensao)
                + ") difere da do modelo ("
                + str(dim_real)
                + "). Usando "
                + str(dim_real)
                + "."
            )
            self.dimensao = dim_real
        return self._modelo

    def _encode(self, textos):
        modelo = self._carregar_modelo()
        self.logger.info("Gerando " + str(len(textos)) + " embeddings")
        try:
            return modelo.encode(
                textos,
                batch_size=32,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
        except Exception:
            self.logger.exception(
                "Falha na geracao de embeddings (modelo=" + self.modelo_nome + ")"
            )
            raise

    def _upsert(self, session, linhas):
        stmt = insert(EmbeddingConteudo).values(linhas)
        stmt = stmt.on_conflict_do_update(
            index_elements=["conteudo_id"],
            set_={
                "texto_origem": stmt.excluded.texto_origem,
                "modelo": stmt.excluded.modelo,
                "vetor": stmt.excluded.vetor,
                "gerado_em": stmt.excluded.gerado_em,
            },
        )
        session.execute(stmt)

    def _consultar(self, session, relatorio):
        total = session.scalar(select(func.count()).select_from(EmbeddingConteudo))
        por_modelo = session.execute(
            select(EmbeddingConteudo.modelo, func.count())
            .group_by(EmbeddingConteudo.modelo)
            .order_by(EmbeddingConteudo.modelo)
        ).all()
        self.logger.info(
            "Consulta embeddings (COUNT)="
            + str(total)
            + " | "
            + ", ".join(nome + "=" + str(qtd) for nome, qtd in por_modelo)
        )
        amostra = session.execute(
            select(
                EmbeddingConteudo.conteudo_id,
                Conteudo.titulo,
                EmbeddingConteudo.modelo,
                func.vector_dims(EmbeddingConteudo.vetor),
            )
            .join(Conteudo, Conteudo.conteudo_id == EmbeddingConteudo.conteudo_id)
            .order_by(EmbeddingConteudo.conteudo_id)
            .limit(3)
        ).all()
        for cid, titulo, modelo, dim in amostra:
            self.logger.info(
                "  amostra embedding "
                + str(cid)
                + " | dim="
                + str(dim)
                + " | modelo="
                + modelo
                + " | "
                + titulo
            )
        relatorio["armazenados"] = int(total or 0)
