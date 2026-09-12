"""
Persistencia estruturada no PostgreSQL (RF06).
Aplica sql/criar_tabelas.sql, filtra os tratados e faz upsert transacional.
"""
from datetime import datetime
from decimal import Decimal

import pandas as pd
from sqlalchemy import create_engine, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, sessionmaker

from src.config import RAIZ_PROJETO, load_config, postgres_url
from src.logger import get_logger
from src.models import Categoria, Conteudo, Interacao, Recomendacao, Usuario
from src.validacao import (
    CATEGORIAS_VALIDAS,
    NIVEIS_VALIDOS,
    TIPOS_INTERACAO_VALIDOS,
    TIPOS_VALIDOS,
)

CAMINHO_DDL = RAIZ_PROJETO / "sql" / "criar_tabelas.sql"

CAMPOS_CATALOGO_OBRIGATORIOS = [
    "conteudo_id",
    "titulo",
    "tipo",
    "categoria",
    "nivel",
    "carga_horaria_min",
    "data_publicacao",
]

CAMPOS_INTERACAO_OBRIGATORIOS = [
    "usuario_id",
    "conteudo_id",
    "tipo_interacao",
    "data_hora",
    "tempo_consumido",
    "percentual_conclusao",
]


def _eh_nulo(valor):
    if valor is None:
        return True
    try:
        resultado = pd.isna(valor)
    except (ValueError, TypeError):
        return False
    return bool(resultado) if not hasattr(resultado, "__len__") else False


def _como_int(valor):
    if _eh_nulo(valor):
        return None
    return int(valor)


def _como_texto(valor):
    if _eh_nulo(valor):
        return None
    texto = str(valor).strip()
    return texto if texto else None


class PersistenciaPostgres:
    """Cria as tabelas (via SQL) e carrega usuario, conteudo e interacao."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = load_config()
        pg = self.config["postgres"]
        if not pg.get("user") or not pg.get("dbname"):
            raise RuntimeError(
                "Credenciais PostgreSQL ausentes no .env "
                "(POSTGRES_USER / POSTGRES_DB)."
            )
        self.engine = create_engine(postgres_url(self.config), pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def carregar(self, df_catalogo, df_interacoes):
        """Filtra, faz upsert e devolve a quantidade de registros enviados."""
        pg = self.config["postgres"]
        destino = (
            str(pg["user"])
            + "@"
            + str(pg["host"])
            + ":"
            + str(pg["port"])
            + "/"
            + str(pg["dbname"])
        )
        self.logger.info("Persistindo no PostgreSQL: " + destino)

        try:
            self._testar_conexao()
        except Exception:
            self.logger.exception(
                "Falha de conexao com o PostgreSQL em " + destino
            )
            raise

        try:
            self._aplicar_ddl()
        except Exception:
            self.logger.exception(
                "Falha de persistencia ao criar tabelas a partir de "
                + str(CAMINHO_DDL)
            )
            raise

        df_conteudos = self._filtrar_catalogo(df_catalogo)
        ids_conteudos = (
            {int(cid) for cid in df_conteudos["conteudo_id"].tolist()}
            if len(df_conteudos)
            else set()
        )
        df_inter = self._filtrar_interacoes(df_interacoes, ids_conteudos)
        usuarios = []
        if len(df_inter):
            usuarios = sorted(
                {int(uid) for uid in df_inter["usuario_id"].tolist() if not _eh_nulo(uid)}
            )

        n_enviados = len(usuarios) + len(df_conteudos) + len(df_inter)
        self.logger.info(
            "Registros validos para carga: "
            + str(len(usuarios))
            + " usuarios, "
            + str(len(df_conteudos))
            + " conteudos, "
            + str(len(df_inter))
            + " interacoes"
        )

        session = self.SessionLocal()
        try:
            mapa_categorias = self._mapa_categorias(session)
            self._upsert_usuarios(session, usuarios)
            self._upsert_conteudos(session, df_conteudos, mapa_categorias)
            self._upsert_interacoes(session, df_inter)
            session.commit()
        except Exception:
            session.rollback()
            self.logger.exception("Falha de persistencia durante o upsert")
            raise
        finally:
            session.close()

        self._consultar()
        return n_enviados

    def _testar_conexao(self):
        with self.engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")

    def _aplicar_ddl(self):
        if not CAMINHO_DDL.exists():
            raise FileNotFoundError("Script SQL nao encontrado: " + str(CAMINHO_DDL))
        sql = CAMINHO_DDL.read_text(encoding="utf-8")
        raw = self.engine.raw_connection()
        try:
            with raw.cursor() as cur:
                cur.execute(sql)
            raw.commit()
            self.logger.info("DDL aplicado: " + CAMINHO_DDL.name)
        except Exception:
            raw.rollback()
            raise
        finally:
            raw.close()

    def _filtrar_catalogo(self, df):
        if df is None or df.empty:
            return pd.DataFrame(columns=CAMPOS_CATALOGO_OBRIGATORIOS)

        aceitos = []
        for _, row in df.iterrows():
            if any(_eh_nulo(row.get(c)) for c in CAMPOS_CATALOGO_OBRIGATORIOS):
                continue
            if row["tipo"] not in TIPOS_VALIDOS:
                continue
            if row["categoria"] not in CATEGORIAS_VALIDAS:
                continue
            if row["nivel"] not in NIVEIS_VALIDOS:
                continue
            try:
                carga = int(row["carga_horaria_min"])
                if carga < 0:
                    continue
            except (ValueError, TypeError):
                continue
            if not self._data_valida(row["data_publicacao"], "%Y-%m-%d"):
                continue
            try:
                int(row["conteudo_id"])
            except (ValueError, TypeError):
                continue
            aceitos.append(row)

        if not aceitos:
            return df.iloc[0:0].copy()
        return pd.DataFrame(aceitos)

    def _filtrar_interacoes(self, df, ids_conteudos):
        if df is None or df.empty:
            return pd.DataFrame(columns=CAMPOS_INTERACAO_OBRIGATORIOS)

        aceitos = []
        for _, row in df.iterrows():
            if any(_eh_nulo(row.get(c)) for c in CAMPOS_INTERACAO_OBRIGATORIOS):
                continue
            if row["tipo_interacao"] not in TIPOS_INTERACAO_VALIDOS:
                continue
            try:
                cid = int(row["conteudo_id"])
                int(row["usuario_id"])
            except (ValueError, TypeError):
                continue
            if cid not in ids_conteudos:
                continue
            try:
                tempo = int(row["tempo_consumido"])
                if tempo < 0:
                    continue
            except (ValueError, TypeError):
                continue
            try:
                perc = float(row["percentual_conclusao"])
                if perc < 0 or perc > 100:
                    continue
            except (ValueError, TypeError):
                continue
            aval = row.get("avaliacao_atribuida")
            if not _eh_nulo(aval):
                try:
                    nota = int(aval)
                    if nota < 1 or nota > 5:
                        continue
                except (ValueError, TypeError):
                    continue
            if not self._data_valida(row["data_hora"], "%Y-%m-%dT%H:%M:%S"):
                continue
            aceitos.append(row)

        if not aceitos:
            return df.iloc[0:0].copy()
        return pd.DataFrame(aceitos)

    @staticmethod
    def _para_date(valor):
        if isinstance(valor, datetime):
            return valor.date()
        if hasattr(valor, "date") and not isinstance(valor, str):
            try:
                return valor.date()
            except TypeError:
                pass
        return datetime.strptime(str(valor).strip()[:10], "%Y-%m-%d").date()

    @staticmethod
    def _para_datetime(valor):
        if isinstance(valor, datetime):
            return valor.replace(tzinfo=None)
        if hasattr(valor, "to_pydatetime"):
            return valor.to_pydatetime().replace(tzinfo=None)
        texto = str(valor).strip()
        if "T" in texto:
            return datetime.strptime(texto[:19], "%Y-%m-%dT%H:%M:%S")
        return datetime.strptime(texto[:19], "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _data_valida(valor, formato):
        if _eh_nulo(valor):
            return False
        if isinstance(valor, datetime):
            return True
        if hasattr(valor, "to_pydatetime") or (
            hasattr(valor, "date") and not isinstance(valor, str)
        ):
            return True
        texto = str(valor).strip()
        if not texto or texto.lower() == "nan":
            return False
        try:
            datetime.strptime(texto, formato)
            return True
        except (ValueError, TypeError):
            try:
                datetime.strptime(texto[:19], "%Y-%m-%d %H:%M:%S")
                return True
            except (ValueError, TypeError):
                return False

    def _mapa_categorias(self, session: Session):
        pares = session.execute(select(Categoria.nome, Categoria.categoria_id)).all()
        mapa = {nome: cid for nome, cid in pares}
        if not mapa:
            raise RuntimeError(
                "Tabela categoria vazia apos o DDL; o seed do script SQL falhou."
            )
        return mapa

    def _upsert_usuarios(self, session: Session, usuarios):
        if not usuarios:
            return
        stmt = insert(Usuario).values([{"usuario_id": uid} for uid in usuarios])
        stmt = stmt.on_conflict_do_nothing(index_elements=["usuario_id"])
        session.execute(stmt)

    def _upsert_conteudos(self, session: Session, df, mapa_categorias):
        if df is None or df.empty:
            return
        linhas = []
        for _, row in df.iterrows():
            nome_cat = _como_texto(row.get("categoria"))
            categoria_id = mapa_categorias.get(nome_cat)
            if categoria_id is None:
                self.logger.warning(
                    "Categoria sem id, conteudo ignorado: " + str(nome_cat)
                )
                continue
            linhas.append(
                {
                    "conteudo_id": int(row["conteudo_id"]),
                    "titulo": str(row["titulo"]).strip(),
                    "tipo": str(row["tipo"]),
                    "categoria_id": categoria_id,
                    "nivel": str(row["nivel"]),
                    "carga_horaria_min": int(row["carga_horaria_min"]),
                    "data_publicacao": self._para_date(row["data_publicacao"]),
                    "descricao": _como_texto(row.get("descricao")),
                    "autor": _como_texto(row.get("autor")),
                }
            )
        if not linhas:
            return
        stmt = insert(Conteudo).values(linhas)
        stmt = stmt.on_conflict_do_update(
            index_elements=["conteudo_id"],
            set_={
                "titulo": stmt.excluded.titulo,
                "tipo": stmt.excluded.tipo,
                "categoria_id": stmt.excluded.categoria_id,
                "nivel": stmt.excluded.nivel,
                "carga_horaria_min": stmt.excluded.carga_horaria_min,
                "data_publicacao": stmt.excluded.data_publicacao,
                "descricao": stmt.excluded.descricao,
                "autor": stmt.excluded.autor,
            },
        )
        session.execute(stmt)

    def _upsert_interacoes(self, session: Session, df):
        if df is None or df.empty:
            return
        linhas = []
        for _, row in df.iterrows():
            aval = _como_int(row.get("avaliacao_atribuida"))
            linhas.append(
                {
                    "usuario_id": int(row["usuario_id"]),
                    "conteudo_id": int(row["conteudo_id"]),
                    "tipo_interacao": str(row["tipo_interacao"]),
                    "data_hora": self._para_datetime(row["data_hora"]),
                    "tempo_consumido": int(row["tempo_consumido"]),
                    "percentual_conclusao": Decimal(
                        str(round(float(row["percentual_conclusao"]), 2))
                    ),
                    "avaliacao_atribuida": aval,
                }
            )
        stmt = insert(Interacao).values(linhas)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_interacao_usuario_conteudo_data",
            set_={
                "tipo_interacao": stmt.excluded.tipo_interacao,
                "tempo_consumido": stmt.excluded.tempo_consumido,
                "percentual_conclusao": stmt.excluded.percentual_conclusao,
                "avaliacao_atribuida": stmt.excluded.avaliacao_atribuida,
            },
        )
        session.execute(stmt)

    def _consultar(self):
        session = self.SessionLocal()
        try:
            contagens = {
                "usuario": session.scalar(select(func.count()).select_from(Usuario)),
                "categoria": session.scalar(select(func.count()).select_from(Categoria)),
                "conteudo": session.scalar(select(func.count()).select_from(Conteudo)),
                "interacao": session.scalar(select(func.count()).select_from(Interacao)),
                "recomendacao": session.scalar(
                    select(func.count()).select_from(Recomendacao)
                ),
            }
            self.logger.info(
                "Consulta PostgreSQL (COUNT): "
                + ", ".join(nome + "=" + str(qtd) for nome, qtd in contagens.items())
            )
            amostra = session.execute(
                select(Conteudo.conteudo_id, Conteudo.titulo, Categoria.nome)
                .join(Categoria, Conteudo.categoria_id == Categoria.categoria_id)
                .order_by(Conteudo.conteudo_id)
                .limit(3)
            ).all()
            for cid, titulo, categoria in amostra:
                self.logger.info(
                    "  amostra conteudo "
                    + str(cid)
                    + " | "
                    + categoria
                    + " | "
                    + titulo
                )
        finally:
            session.close()
