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
        logger.info("[STUB] Embeddings (RF08) ............ nao implementado")
        logger.info("[STUB] Busca semantica (RF09) ....... nao implementado")
        logger.info("[STUB] Recomendacao (RF10) .......... nao implementado")
        logger.info("[STUB] KPIs (RF12) .................. nao implementado")
        logger.info("-" * 60)

        logger.info("FIM DO PIPELINE - duracao: " + str(duracao) + "s")
        return 0

    except Exception as e:
        logger.exception("Erro fatal no pipeline: " + str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())