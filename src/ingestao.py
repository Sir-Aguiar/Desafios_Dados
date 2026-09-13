"""
Modulo de ingestao dos dados brutos - RF02.
Le CSV e JSON, reporta quantos registros cada fonte possui.
"""
import json
from pathlib import Path
import pandas as pd

from src.config import load_config
from src.logger import get_logger


class Ingestor:
    """Le e mantem em memoria os dados brutos das 3 fontes."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = load_config()

        # DataFrames/listas carregados
        self.df_catalogo = None
        self.df_interacoes = None
        self.lista_comentarios = None

        # Contadores (para o resumo RF05)
        self.resumo = {
            "catalogo": {"lidos": 0, "validos": 0, "invalidos": 0, "incompletos": 0, "duplicados": 0, "corrigidos": 0},
            "interacoes": {"lidos": 0, "validos": 0, "invalidos": 0, "incompletos": 0, "duplicados": 0, "corrigidos": 0},
            "comentarios": {"lidos": 0, "validos": 0, "invalidos": 0, "incompletos": 0, "duplicados": 0, "corrigidos": 0},
            "carregados_postgres": 0,
            "carregados_mongo": 0,
            "tempo_total_segundos": 0.0,
        }

    # ------------------------------------------------------------------
    # RF02.1 - Ler o catalogo (CSV)
    # ------------------------------------------------------------------
    def _ler_catalogo(self):
        caminho = Path(self.config["fontes_dados"]["catalogo"])
        self.logger.info("Lendo catalogo CSV: " + caminho.name)
        try:
            self.df_catalogo = pd.read_csv(caminho, encoding="utf-8")
            qtd = len(self.df_catalogo)
            self.resumo["catalogo"]["lidos"] = qtd
            self.logger.info("  -> " + str(qtd) + " registros lidos de " + caminho.name)
        except Exception as e:
            self.logger.error("Falha ao ler " + caminho.name + ": " + str(e))
            raise

    # ------------------------------------------------------------------
    # RF02.2 - Ler as interacoes (JSON)
    # ------------------------------------------------------------------
    def _ler_interacoes(self):
        caminho = Path(self.config["fontes_dados"]["interacoes"])
        self.logger.info("Lendo interacoes JSON: " + caminho.name)
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
            self.df_interacoes = pd.DataFrame(dados)
            qtd = len(self.df_interacoes)
            self.resumo["interacoes"]["lidos"] = qtd
            self.logger.info("  -> " + str(qtd) + " registros lidos de " + caminho.name)
        except Exception as e:
            self.logger.error("Falha ao ler " + caminho.name + ": " + str(e))
            raise

    # ------------------------------------------------------------------
    # RF02.3 - Ler os comentarios (JSON)
    # ------------------------------------------------------------------
    def _ler_comentarios(self):
        caminho = Path(self.config["fontes_dados"]["comentarios"])
        self.logger.info("Lendo comentarios JSON: " + caminho.name)
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                self.lista_comentarios = json.load(f)
            qtd = len(self.lista_comentarios)
            self.resumo["comentarios"]["lidos"] = qtd
            self.logger.info("  -> " + str(qtd) + " registros lidos de " + caminho.name)
        except Exception as e:
            self.logger.error("Falha ao ler " + caminho.name + ": " + str(e))
            raise

    # ------------------------------------------------------------------
    # Orquestrador
    # ------------------------------------------------------------------
    def processar(self):
        self.logger.info("--- Iniciando leitura das fontes de dados ---")
        self._ler_catalogo()
        self._ler_interacoes()
        self._ler_comentarios()
        self.logger.info("--- Leitura concluida ---")
        self.logger.info("Colunas do catalogo: " + str(list(self.df_catalogo.columns)))
        self.logger.info("Colunas das interacoes: " + str(list(self.df_interacoes.columns)))
        if self.lista_comentarios:
            self.logger.info("Chaves de um comentario: " + str(list(self.lista_comentarios[0].keys())))

    # ------------------------------------------------------------------
    # RF05 - Consolidar e persistir o resumo
    # ------------------------------------------------------------------
    def consolidar_resumo(self, relatorios_validacao, corrigidos, carregados_pg, carregados_mongo, tempo, tempos_etapas=None):
        """Junta as metricas de ingestao + validacao + tratamento em um JSON."""
        for fonte in ("catalogo", "interacoes", "comentarios"):
            self.resumo[fonte]["validos"] = relatorios_validacao[fonte]["validos"]
            self.resumo[fonte]["invalidos"] = relatorios_validacao[fonte]["invalidos"]
            self.resumo[fonte]["incompletos"] = relatorios_validacao[fonte]["incompletos"]
            self.resumo[fonte]["duplicados"] = relatorios_validacao[fonte]["duplicados"]

        if isinstance(corrigidos, dict):
            for fonte in ("catalogo", "interacoes", "comentarios"):
                self.resumo[fonte]["corrigidos"] = int(corrigidos.get(fonte, 0))
        else:
            self.resumo["catalogo"]["corrigidos"] = int(corrigidos or 0)
            self.resumo["interacoes"]["corrigidos"] = 0
            self.resumo["comentarios"]["corrigidos"] = 0

        self.resumo["carregados_postgres"] = carregados_pg
        self.resumo["carregados_mongo"] = carregados_mongo
        self.resumo["tempo_total_segundos"] = tempo
        if tempos_etapas:
            self.resumo["tempos_etapas"] = tempos_etapas

        # Gravar em JSON
        destino = Path("dados/processados/resumo_ingestao.json")
        destino.parent.mkdir(parents=True, exist_ok=True)
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(self.resumo, f, indent=2, ensure_ascii=False)

        self.logger.info("Resumo da ingestao gravado em " + str(destino))
        return self.resumo

    def get_resumo(self):
        return self.resumo