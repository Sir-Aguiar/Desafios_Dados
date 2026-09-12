"""
Ponto de entrada do pipeline.
Executado com: python -m src.main
"""
import time
import sys

from src.config import load_config
from src.logger import get_logger
from src.ingestao import Ingestor
from src.validacao import Validador
from src.tratamento import Tratador
from src.persistencia import PersistenciaPostgres
from src.persistencia_mongo import PersistenciaMongo
from src.embeddings import GeradorEmbeddings
from src.busca_semantica import BuscadorSemantico
from src.recomendacao import GeradorRecomendacoes


def main():
    inicio = time.time()
    logger = get_logger(__name__)

    logger.info("=" * 60)
    logger.info("INICIO DO PIPELINE - Plataforma Educacional")
    logger.info("=" * 60)

    try:
        config = load_config()

        # ---------- FASE 1: Ingestao (RF02) ----------
        logger.info("[FASE 1] Ingestao de dados (RF02)")
        ingestor = Ingestor()
        ingestor.processar()

        # ---------- FASE 1: Validacao (RF03) ----------
        logger.info("[FASE 1] Validacao de dados (RF03)")
        validador = Validador()
        ids_conteudos = set(ingestor.df_catalogo["conteudo_id"].tolist())
        ids_usuarios = set(ingestor.df_interacoes["usuario_id"].tolist())
        validador.validar_catalogo(ingestor.df_catalogo)
        validador.validar_interacoes(ingestor.df_interacoes, ids_conteudos, ids_usuarios)
        validador.validar_comentarios(ingestor.lista_comentarios, ids_conteudos, ids_usuarios)

        # ---------- FASE 1: Tratamento (RF04) ----------
        logger.info("[FASE 1] Tratamento e padronizacao (RF04)")
        tratador = Tratador()
        df_catalogo = tratador.tratar_catalogo(ingestor.df_catalogo)
        df_interacoes = tratador.tratar_interacoes(ingestor.df_interacoes)
        df_comentarios = tratador.tratar_comentarios(ingestor.lista_comentarios)

        # ---------- FASE 2: Persistencia PostgreSQL (RF06) ----------
        logger.info("[FASE 2] Persistencia PostgreSQL (RF06)")
        persistencia = PersistenciaPostgres()
        carregados_pg = persistencia.carregar(df_catalogo, df_interacoes)
        logger.info("Registros enviados ao PostgreSQL: " + str(carregados_pg))

        # ---------- FASE 2: Persistencia MongoDB (RF07) ----------
        logger.info("[FASE 2] Persistencia MongoDB (RF07)")
        persistencia_mongo = PersistenciaMongo()
        try:
            carregados_mongo = persistencia_mongo.carregar(df_comentarios, df_catalogo)
        finally:
            persistencia_mongo.fechar()
        logger.info("Documentos enviados ao MongoDB: " + str(carregados_mongo))

        # ---------- FASE 2: Embeddings (RF08) ----------
        logger.info("[FASE 2] Geracao de embeddings (RF08)")
        gerador_embeddings = GeradorEmbeddings()
        resultado_emb = gerador_embeddings.gerar()
        logger.info("Embeddings: " + str(resultado_emb))

        # ---------- FASE 2: Busca semantica (RF09) ----------
        logger.info("[FASE 2] Busca semantica (RF09)")
        buscador = BuscadorSemantico(gerador=gerador_embeddings)
        resultado_busca = buscador.demonstrar()
        logger.info(
            "Consultas semanticas demonstradas: "
            + str(len(resultado_busca["consultas"]))
        )

        # ---------- FASE 2: Recomendacao (RF10/RF11) ----------
        logger.info("[FASE 2] Geracao e persistencia de recomendacoes (RF10/RF11)")
        gerador_rec = GeradorRecomendacoes()
        resultado_rec = gerador_rec.gerar()
        logger.info(
            "Recomendacoes geradas: "
            + str(resultado_rec["resumo"]["total"])
            + ", persistidas: "
            + str(resultado_rec["resumo"].get("persistidas", 0))
        )

        # ---------- FASE 2: Resumo (RF05) ----------
        logger.info("[FASE 2] Consolidando resumo da ingestao (RF05)")
        duracao = round(time.time() - inicio, 2)
        resumo = ingestor.consolidar_resumo(
            relatorios_validacao=validador.get_relatorios(),
            corrigidos=tratador.get_corrigidos(),
            carregados_pg=carregados_pg,
            carregados_mongo=carregados_mongo,
            tempo=duracao,
        )
        logger.info("Resumo: " + str(resumo))

        # ---------- STUBS ----------
        logger.info("-" * 60)
        logger.info("[STUB] KPIs (RF12) .................. nao implementado")
        logger.info("-" * 60)

        logger.info("FIM DO PIPELINE - duracao: " + str(duracao) + "s")
        return 0

    except Exception as e:
        logger.exception("Erro fatal no pipeline: " + str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())