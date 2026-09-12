"""
Geracao de recomendacoes de conteudos (RF10) e persistencia (RF11).

Pontuacao = ((Ivis + Icur) / 2) * 100 * Iconc

Ivis: afinidade tematica com o que o usuario visualiza (cosseno no
      pgvector; fallback pela proporcao de tempo na categoria).
Icur: interesse explicito (curtidas e avaliacoes >= nota minima).
Iconc: 0 se o usuario ja concluiu o conteudo, 1 caso contrario.
"""
import json
import sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

import numpy as np
from sqlalchemy import create_engine, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

from src.config import RAIZ_PROJETO, load_config, postgres_url
from src.logger import get_logger
from src.models import (
    Categoria,
    Conteudo,
    EmbeddingConteudo,
    Interacao,
    Recomendacao,
    Usuario,
)

CAMINHO_SAIDA = RAIZ_PROJETO / "dados" / "processados" / "recomendacoes.json"

TIPOS_CONSUMO = frozenset({"visualização", "início", "conclusão"})
TIPO_CURTIDA = "curtida"
TIPO_CONCLUSAO = "conclusão"

FORMULA = "Pontuação = ((Ivis + Icur) / 2) * 100 * Iconc"


def _clip01(valor):
    return float(max(0.0, min(1.0, valor)))


def _como_float(valor):
    if valor is None:
        return 0.0
    if isinstance(valor, Decimal):
        return float(valor)
    return float(valor)


def calcular_pontuacao(ivis, icur, iconc):
    """Aplica a formula oficial do RF10. Resultado em [0, 100], duas casas."""
    vis = _clip01(ivis)
    cur = _clip01(icur)
    conc = 0.0 if int(iconc) == 0 else 1.0
    return round(((vis + cur) / 2.0) * 100.0 * conc, 2)


def classificar_recomendacao(pontuacao, iconc):
    """
    Positivo: pontuacao >= 70
    Estavel:  40 < pontuacao < 70  (intervalo intermediario; o enunciado
              escreve "40 > pontuacao < 70", lido como a faixa aberta)
    Negativo: pontuacao <= 40 ou Iconc = 0
    """
    if int(iconc) == 0 or pontuacao <= 40:
        return "Negativo"
    if pontuacao >= 70:
        return "Positivo"
    return "Estável"


def _normalizar(vetor):
    arr = np.asarray(vetor, dtype=np.float64).reshape(-1)
    norma = np.linalg.norm(arr)
    if norma <= 0:
        return None
    return arr / norma


def _centroide(pares_peso_vetor):
    """Media ponderada de vetores ja normalizados; devolve centroide unitario."""
    if not pares_peso_vetor:
        return None
    acc = None
    peso_total = 0.0
    for peso, vetor in pares_peso_vetor:
        w = max(_como_float(peso), 1.0)
        if acc is None:
            acc = vetor * w
        else:
            acc = acc + vetor * w
        peso_total += w
    if acc is None or peso_total <= 0:
        return None
    return _normalizar(acc / peso_total)


class GeradorRecomendacoes:
    """Gera o ranking de recomendacoes por usuario a partir do PostgreSQL."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = load_config()
        pg = self.config["postgres"]
        if not pg.get("user") or not pg.get("dbname"):
            raise RuntimeError(
                "Credenciais PostgreSQL ausentes no .env "
                "(POSTGRES_USER / POSTGRES_DB)."
            )

        rec = self.config.get("recomendacao") or {}
        self.top_n = int(rec.get("top_n_por_usuario") or 5)
        self.nota_minima = int(rec.get("nota_minima_avaliacao_positiva") or 4)
        self.peso_ivis = float(rec.get("peso_ivis") if rec.get("peso_ivis") is not None else 0.5)
        self.peso_icur = float(rec.get("peso_icur") if rec.get("peso_icur") is not None else 0.5)
        self.modelo_nome = self.config["embeddings"]["modelo"]

        self.engine = create_engine(postgres_url(self.config), pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def gerar(self, usuario_id=None, top_n=None):
        """Gera recomendacoes, persiste no PostgreSQL (RF11) e grava o JSON."""
        n = self._top_n(top_n)
        gerado_em = datetime.now().replace(microsecond=0)
        self.logger.info(
            "Gerando recomendacoes (top_n="
            + str(n)
            + ", nota_minima="
            + str(self.nota_minima)
            + ", modelo="
            + self.modelo_nome
            + ", formula="
            + FORMULA
            + ")"
        )
        if abs(self.peso_ivis - 0.5) > 1e-9 or abs(self.peso_icur - 0.5) > 1e-9:
            self.logger.warning(
                "peso_ivis/peso_icur no config.yaml diferem de 0.5; "
                "o RF10 usa media simples e ignora esses pesos."
            )

        session = self.SessionLocal()
        try:
            contexto = self._carregar_contexto(session, usuario_id)
            recomendacoes, resumo = self._gerar_todas(contexto, n, gerado_em)
        except Exception:
            self.logger.exception("Falha na geracao de recomendacoes")
            raise
        finally:
            session.close()

        persistidas = self.persistir(recomendacoes, gerado_em)
        resumo["persistidas"] = persistidas

        relatorio = {
            "formula": FORMULA,
            "modelo_embeddings": self.modelo_nome,
            "top_n_por_usuario": n,
            "nota_minima_avaliacao_positiva": self.nota_minima,
            "gerado_em": gerado_em.isoformat(timespec="seconds"),
            "resumo": resumo,
            "recomendacoes": recomendacoes,
        }
        self._gravar(relatorio)
        self._logar_resumo(resumo, recomendacoes, n)
        return relatorio

    def _carregar_contexto(self, session, usuario_id):
        filtro_usuario = []
        if usuario_id is not None:
            filtro_usuario.append(Usuario.usuario_id == int(usuario_id))

        usuarios = [
            int(uid)
            for (uid,) in session.execute(
                select(Usuario.usuario_id)
                .where(*filtro_usuario)
                .order_by(Usuario.usuario_id)
            ).all()
        ]
        if usuario_id is not None and not usuarios:
            raise ValueError("Usuario " + str(usuario_id) + " nao encontrado no PostgreSQL.")

        conteudos = session.execute(
            select(
                Conteudo.conteudo_id,
                Conteudo.titulo,
                Conteudo.tipo,
                Conteudo.categoria_id,
                Categoria.nome,
            )
            .join(Categoria, Categoria.categoria_id == Conteudo.categoria_id)
            .order_by(Conteudo.conteudo_id)
        ).all()

        embeddings = {}
        for row in session.execute(
            select(EmbeddingConteudo.conteudo_id, EmbeddingConteudo.vetor).where(
                EmbeddingConteudo.modelo == self.modelo_nome
            )
        ).all():
            vetor = _normalizar(list(row.vetor))
            if vetor is not None:
                embeddings[int(row.conteudo_id)] = vetor

        filtro_inter = []
        if usuario_id is not None:
            filtro_inter.append(Interacao.usuario_id == int(usuario_id))
        interacoes = session.execute(
            select(
                Interacao.usuario_id,
                Interacao.conteudo_id,
                Interacao.tipo_interacao,
                Interacao.tempo_consumido,
                Interacao.percentual_conclusao,
                Interacao.avaliacao_atribuida,
            ).where(*filtro_inter)
        ).all()

        self.logger.info(
            "Contexto: usuarios="
            + str(len(usuarios))
            + ", conteudos="
            + str(len(conteudos))
            + ", embeddings="
            + str(len(embeddings))
            + ", interacoes="
            + str(len(interacoes))
        )
        if conteudos and not embeddings:
            self.logger.warning(
                "Nenhum embedding do modelo "
                + self.modelo_nome
                + "; Ivis/Icur usarao o fallback por categoria."
            )

        return {
            "usuarios": usuarios,
            "conteudos": conteudos,
            "embeddings": embeddings,
            "interacoes": interacoes,
        }

    def _gerar_todas(self, contexto, top_n, gerado_em):
        por_usuario = defaultdict(list)
        for row in contexto["interacoes"]:
            por_usuario[int(row.usuario_id)].append(row)

        cat_por_conteudo = {
            int(c.conteudo_id): int(c.categoria_id) for c in contexto["conteudos"]
        }
        ids_emb = [
            int(c.conteudo_id)
            for c in contexto["conteudos"]
            if int(c.conteudo_id) in contexto["embeddings"]
        ]
        matriz = None
        if ids_emb:
            matriz = np.vstack([contexto["embeddings"][cid] for cid in ids_emb])

        recomendacoes = []
        resumo = {
            "usuarios_processados": len(contexto["usuarios"]),
            "usuarios_sem_recomendacao": 0,
            "total": 0,
            "positivas": 0,
            "estaveis": 0,
            "negativas_descartadas": 0,
            "negativas_por_conclusao": 0,
            "persistidas": 0,
        }
        gerado_iso = gerado_em.isoformat(timespec="seconds")

        for uid in contexto["usuarios"]:
            itens, n_neg, n_conc = self._recomendar_usuario(
                uid,
                por_usuario.get(uid, []),
                contexto["conteudos"],
                contexto["embeddings"],
                cat_por_conteudo,
                ids_emb,
                matriz,
                top_n,
                gerado_iso,
            )
            resumo["negativas_descartadas"] += n_neg
            resumo["negativas_por_conclusao"] += n_conc
            if not itens:
                resumo["usuarios_sem_recomendacao"] += 1
                continue
            for item in itens:
                if item["classificacao"] == "Positivo":
                    resumo["positivas"] += 1
                else:
                    resumo["estaveis"] += 1
                recomendacoes.append(item)

        resumo["total"] = len(recomendacoes)
        return recomendacoes, resumo

    def _recomendar_usuario(
        self,
        usuario_id,
        interacoes,
        conteudos,
        embeddings,
        cat_por_conteudo,
        ids_emb,
        matriz,
        top_n,
        gerado_iso,
    ):
        concluidos = set()
        pares_vis = []
        pares_cur = []
        tempo_por_categoria = defaultdict(float)
        positivos_por_categoria = defaultdict(int)
        tempo_total = 0.0
        positivos_total = 0
        vistos_cur = set()

        for row in interacoes:
            cid = int(row.conteudo_id)
            if self._eh_conclusao(row):
                concluidos.add(cid)

            cat_id = cat_por_conteudo.get(cid)

            if self._eh_consumo(row):
                tempo = max(_como_float(row.tempo_consumido), 1.0)
                tempo_total += tempo
                if cat_id is not None:
                    tempo_por_categoria[cat_id] += tempo
                vetor = embeddings.get(cid)
                if vetor is not None:
                    pares_vis.append((tempo, vetor))

            if self._eh_positivo(row) and cid not in vistos_cur:
                vistos_cur.add(cid)
                positivos_total += 1
                if cat_id is not None:
                    positivos_por_categoria[cat_id] += 1
                vetor = embeddings.get(cid)
                if vetor is not None:
                    pares_cur.append((1.0, vetor))

        centroide_vis = _centroide(pares_vis)
        centroide_cur = _centroide(pares_cur)

        ivis_por_id = {}
        icur_por_id = {}
        if matriz is not None and centroide_vis is not None:
            scores = np.clip(matriz @ centroide_vis, 0.0, 1.0)
            ivis_por_id = {cid: float(s) for cid, s in zip(ids_emb, scores)}
        if matriz is not None and centroide_cur is not None:
            scores = np.clip(matriz @ centroide_cur, 0.0, 1.0)
            icur_por_id = {cid: float(s) for cid, s in zip(ids_emb, scores)}

        ranqueados = []
        n_neg = 0
        n_conc = 0
        for c in conteudos:
            cid = int(c.conteudo_id)
            iconc = 0 if cid in concluidos else 1
            if iconc == 0:
                n_conc += 1

            ivis = ivis_por_id.get(cid)
            if ivis is None:
                ivis = self._proporcao(tempo_por_categoria.get(int(c.categoria_id), 0.0), tempo_total)

            icur = icur_por_id.get(cid)
            if icur is None:
                icur = self._proporcao(
                    positivos_por_categoria.get(int(c.categoria_id), 0),
                    positivos_total,
                )

            ivis = _clip01(ivis)
            icur = _clip01(icur)
            pontos = calcular_pontuacao(ivis, icur, iconc)
            classe = classificar_recomendacao(pontos, iconc)
            if classe == "Negativo":
                n_neg += 1
                continue
            ranqueados.append(
                {
                    "usuario_id": int(usuario_id),
                    "conteudo_id": cid,
                    "titulo": c.titulo,
                    "categoria": c.nome,
                    "tipo": c.tipo,
                    "pontuacao": pontos,
                    "classificacao": classe,
                    "ivis": round(ivis, 4),
                    "icur": round(icur, 4),
                    "iconc": iconc,
                    "gerado_em": gerado_iso,
                }
            )

        ranqueados.sort(key=lambda item: (-item["pontuacao"], item["conteudo_id"]))
        escolhidos = ranqueados[:top_n]
        for posicao, item in enumerate(escolhidos, start=1):
            item["posicao"] = posicao
        return escolhidos, n_neg, n_conc

    def _eh_consumo(self, row):
        if row.tipo_interacao in TIPOS_CONSUMO:
            return True
        return _como_float(row.tempo_consumido) > 0

    def _eh_positivo(self, row):
        if row.tipo_interacao == TIPO_CURTIDA:
            return True
        if row.avaliacao_atribuida is None:
            return False
        return int(row.avaliacao_atribuida) >= self.nota_minima

    @staticmethod
    def _eh_conclusao(row):
        if row.tipo_interacao == TIPO_CONCLUSAO:
            return True
        return _como_float(row.percentual_conclusao) >= 100.0

    @staticmethod
    def _proporcao(parte, total):
        if not total:
            return 0.0
        return _clip01(_como_float(parte) / _como_float(total))

    def persistir(self, recomendacoes, gerado_em):
        """Grava a geracao atual na tabela recomendacao (RF11), em transacao."""
        linhas = self._linhas_persistencia(recomendacoes, gerado_em)
        if not linhas:
            self.logger.warning(
                "Nenhuma recomendacao para persistir no PostgreSQL."
            )
            return 0

        session = self.SessionLocal()
        try:
            stmt = insert(Recomendacao).values(linhas)
            stmt = stmt.on_conflict_do_update(
                constraint="uq_recomendacao_usuario_conteudo_geracao",
                set_={
                    "pontuacao": stmt.excluded.pontuacao,
                    "posicao": stmt.excluded.posicao,
                    "classificacao": stmt.excluded.classificacao,
                },
            )
            session.execute(stmt)
            session.commit()
        except Exception:
            session.rollback()
            self.logger.exception("Falha de persistencia das recomendacoes")
            raise
        finally:
            session.close()

        self.logger.info(
            "Recomendacoes enviadas ao PostgreSQL: " + str(len(linhas))
        )
        self._consultar_persistidas(gerado_em)
        return len(linhas)

    @staticmethod
    def _linhas_persistencia(recomendacoes, gerado_em):
        linhas = []
        vistos = set()
        for item in recomendacoes or []:
            uid = int(item["usuario_id"])
            cid = int(item["conteudo_id"])
            posicao = int(item["posicao"])
            if posicao < 1:
                continue
            chave = (uid, cid, gerado_em)
            if chave in vistos:
                continue
            vistos.add(chave)
            linhas.append(
                {
                    "usuario_id": uid,
                    "conteudo_id": cid,
                    "pontuacao": Decimal(str(item["pontuacao"])),
                    "posicao": posicao,
                    "classificacao": str(item["classificacao"]),
                    "gerado_em": gerado_em,
                }
            )
        return linhas

    def _consultar_persistidas(self, gerado_em):
        session = self.SessionLocal()
        try:
            total = session.scalar(select(func.count()).select_from(Recomendacao))
            da_geracao = session.scalar(
                select(func.count())
                .select_from(Recomendacao)
                .where(Recomendacao.gerado_em == gerado_em)
            )
            por_classe = session.execute(
                select(Recomendacao.classificacao, func.count())
                .where(Recomendacao.gerado_em == gerado_em)
                .group_by(Recomendacao.classificacao)
                .order_by(Recomendacao.classificacao)
            ).all()
            self.logger.info(
                "Consulta recomendacao (COUNT)="
                + str(total)
                + ", desta_geracao="
                + str(da_geracao)
                + " | "
                + ", ".join(nome + "=" + str(qtd) for nome, qtd in por_classe)
            )
            amostra = session.execute(
                select(
                    Recomendacao.usuario_id,
                    Recomendacao.posicao,
                    Recomendacao.conteudo_id,
                    Conteudo.titulo,
                    Recomendacao.pontuacao,
                    Recomendacao.classificacao,
                    Recomendacao.gerado_em,
                )
                .join(Conteudo, Conteudo.conteudo_id == Recomendacao.conteudo_id)
                .where(Recomendacao.gerado_em == gerado_em)
                .order_by(Recomendacao.usuario_id, Recomendacao.posicao)
                .limit(5)
            ).all()
            for uid, posicao, cid, titulo, pontos, classe, quando in amostra:
                self.logger.info(
                    "  amostra rec usuario="
                    + str(uid)
                    + " | #"
                    + str(posicao)
                    + " id="
                    + str(cid)
                    + " | "
                    + classe
                    + " | pts="
                    + str(pontos)
                    + " | "
                    + quando.isoformat(timespec="seconds")
                    + " | "
                    + titulo
                )
        finally:
            session.close()

    def _top_n(self, top_n):
        n = self.top_n if top_n is None else int(top_n)
        if n < 1:
            raise ValueError("top_n deve ser um inteiro >= 1.")
        return n

    def _gravar(self, relatorio):
        CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
        with open(CAMINHO_SAIDA, "w", encoding="utf-8") as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        self.logger.info("Recomendacoes gravadas em " + str(CAMINHO_SAIDA))

    def _logar_resumo(self, resumo, recomendacoes, top_n):
        self.logger.info(
            "Resumo RF10: total="
            + str(resumo["total"])
            + ", persistidas="
            + str(resumo.get("persistidas", 0))
            + ", positivas="
            + str(resumo["positivas"])
            + ", estaveis="
            + str(resumo["estaveis"])
            + ", negativas_descartadas="
            + str(resumo["negativas_descartadas"])
            + " (conclusao="
            + str(resumo["negativas_por_conclusao"])
            + "), usuarios_sem_recomendacao="
            + str(resumo["usuarios_sem_recomendacao"])
            + "/"
            + str(resumo["usuarios_processados"])
        )
        vistos = []
        for item in recomendacoes:
            uid = item["usuario_id"]
            if uid in vistos:
                continue
            vistos.append(uid)
            if len(vistos) >= 3:
                break
        amostra = [item for item in recomendacoes if item["usuario_id"] in vistos]
        if not amostra:
            self.logger.warning("Nenhuma recomendacao Positiva/Estavel para apresentar.")
            return
        self.logger.info("Amostra (ate 3 usuarios, top_n=" + str(top_n) + "):")
        for item in amostra:
            self.logger.info(
                "  usuario="
                + str(item["usuario_id"])
                + " | #"
                + str(item["posicao"])
                + " id="
                + str(item["conteudo_id"])
                + " | "
                + item["classificacao"]
                + " | pts="
                + str(item["pontuacao"])
                + " | ivis="
                + str(item["ivis"])
                + " icur="
                + str(item["icur"])
                + " iconc="
                + str(item["iconc"])
                + " | "
                + item["categoria"]
                + " | "
                + item["titulo"]
            )


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    gerador = GeradorRecomendacoes()
    if args:
        gerador.gerar(usuario_id=int(args[0]))
        return 0
    gerador.gerar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
