"""
Modulo de tratamento e padronizacao - RF04.
Remove espacos, padroniza dominios, converte datas e numericos,
elimina duplicidades. Os arquivos ORIGINAIS nao sao modificados:
o resultado vai para dados/processados/.

As decisoes deste modulo estao documentadas em
documentacao/decisoes_tratamento.md.
"""
from pathlib import Path

import pandas as pd

from src.config import load_config
from src.logger import get_logger
from src.validacao import (
    CATEGORIAS_VALIDAS,
    NIVEIS_VALIDOS,
    TIPOS_INTERACAO_VALIDOS,
    TIPOS_VALIDOS,
)


class Tratador:
    """Trata e padroniza os dados apos a validacao."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = load_config()
        self.dir_saida = Path("dados/processados")
        self.dir_saida.mkdir(parents=True, exist_ok=True)
        self.corrigidos = {
            "catalogo": 0,
            "interacoes": 0,
            "comentarios": 0,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _serie_texto(serie):
        """Remove espacos nas pontas sem transformar nulo em string 'nan'."""
        texto = serie.astype("string").str.strip()
        return texto.mask(texto.isin(["", "nan", "None", "<NA>"]))

    @staticmethod
    def _serie_canonica(serie, dominio):
        """Mapeia o valor para o rotulo canonico do dominio (case-insensitive)."""
        texto = Tratador._serie_texto(serie)
        mapa = {item.casefold(): item for item in dominio}

        def _mapear(valor):
            if pd.isna(valor):
                return pd.NA
            return mapa.get(str(valor).casefold(), valor)

        return texto.map(_mapear)

    @staticmethod
    def _serie_data(serie, formato):
        """Converte datas; valores ilegíveis ficam nulos (nao sao inventados)."""
        return pd.to_datetime(serie, errors="coerce").dt.strftime(formato)

    @staticmethod
    def _eh_nulo(valor):
        if valor is None:
            return True
        if isinstance(valor, (list, dict, set)):
            return False
        try:
            resultado = pd.isna(valor)
        except (ValueError, TypeError):
            return False
        return bool(resultado) if not hasattr(resultado, "__len__") else False

    @staticmethod
    def _contar_alterados(antes, depois, colunas):
        """Conta linhas em que ao menos um campo padronizado mudou."""
        alterados = 0
        for idx in depois.index:
            for col in colunas:
                a = antes.at[idx, col] if col in antes.columns else pd.NA
                b = depois.at[idx, col]
                a_nulo = Tratador._eh_nulo(a)
                b_nulo = Tratador._eh_nulo(b)
                if a_nulo and b_nulo:
                    continue
                if a_nulo != b_nulo or str(a).strip() != str(b).strip():
                    alterados += 1
                    break
        return alterados

    def _registrar_ausentes(self, fonte, df, colunas):
        for col in colunas:
            if col not in df.columns:
                continue
            nulos = int(df[col].isna().sum())
            if nulos:
                self.logger.info(
                    "  Valores ausentes em "
                    + fonte
                    + "."
                    + col
                    + ": "
                    + str(nulos)
                    + " (mantidos como nulo, sem imputacao)"
                )

    # ------------------------------------------------------------------
    # RF04.1 - Tratar catalogo
    # ------------------------------------------------------------------
    def tratar_catalogo(self, df):
        self.logger.info("Tratando catalogo...")
        antes = len(df)
        original = df.copy()
        df = df.copy()

        colunas_texto = ["titulo", "tipo", "categoria", "nivel", "descricao", "autor"]
        for col in colunas_texto:
            if col in df.columns:
                df[col] = self._serie_texto(df[col])

        df["tipo"] = self._serie_canonica(df["tipo"], TIPOS_VALIDOS)
        df["categoria"] = self._serie_canonica(df["categoria"], CATEGORIAS_VALIDAS)
        df["nivel"] = self._serie_canonica(df["nivel"], NIVEIS_VALIDOS)

        df["carga_horaria_min"] = pd.to_numeric(
            df["carga_horaria_min"], errors="coerce"
        ).astype("Int64")

        df["data_publicacao"] = self._serie_data(df["data_publicacao"], "%Y-%m-%d")

        colunas_cmp = [
            "titulo",
            "tipo",
            "categoria",
            "nivel",
            "carga_horaria_min",
            "data_publicacao",
            "descricao",
            "autor",
        ]
        n_alterados = self._contar_alterados(original, df, colunas_cmp)

        duplicados = int(df.duplicated(subset=["conteudo_id"]).sum())
        if duplicados:
            df = df.drop_duplicates(subset=["conteudo_id"], keep="first")

        self.corrigidos["catalogo"] = n_alterados + duplicados
        self._registrar_ausentes(
            "catalogo",
            df,
            ["titulo", "tipo", "categoria", "nivel", "carga_horaria_min", "data_publicacao"],
        )

        destino = self.dir_saida / "catalogo_tratado.csv"
        df.to_csv(destino, index=False, encoding="utf-8")
        self.logger.info(
            "  Catalogo tratado: "
            + str(antes)
            + " -> "
            + str(len(df))
            + " registros ("
            + str(duplicados)
            + " duplicados removidos, "
            + str(self.corrigidos["catalogo"])
            + " corrigidos)"
        )
        return df

    # ------------------------------------------------------------------
    # RF04.2 - Tratar interacoes
    # ------------------------------------------------------------------
    def tratar_interacoes(self, df):
        self.logger.info("Tratando interacoes...")
        antes = len(df)
        original = df.copy()
        df = df.copy()

        df["tipo_interacao"] = self._serie_canonica(
            df["tipo_interacao"], TIPOS_INTERACAO_VALIDOS
        )

        df["data_hora"] = self._serie_data(df["data_hora"], "%Y-%m-%dT%H:%M:%S")

        df["tempo_consumido"] = pd.to_numeric(
            df["tempo_consumido"], errors="coerce"
        ).astype("Int64")
        df["percentual_conclusao"] = pd.to_numeric(
            df["percentual_conclusao"], errors="coerce"
        ).round(2)
        df["avaliacao_atribuida"] = pd.to_numeric(
            df["avaliacao_atribuida"], errors="coerce"
        ).astype("Int64")

        colunas_cmp = [
            "tipo_interacao",
            "data_hora",
            "tempo_consumido",
            "percentual_conclusao",
            "avaliacao_atribuida",
        ]
        n_alterados = self._contar_alterados(original, df, colunas_cmp)

        chaves = ["usuario_id", "conteudo_id", "data_hora"]
        duplicados = int(df.duplicated(subset=chaves).sum())
        if duplicados:
            df = df.drop_duplicates(subset=chaves, keep="first")

        self.corrigidos["interacoes"] = n_alterados + duplicados
        self._registrar_ausentes(
            "interacoes",
            df,
            ["tipo_interacao", "data_hora", "tempo_consumido", "percentual_conclusao"],
        )
        nulos_aval = int(df["avaliacao_atribuida"].isna().sum())
        self.logger.info(
            "  avaliacao_atribuida nula: "
            + str(nulos_aval)
            + " (valor de negocio valido; nao imputado)"
        )

        destino = self.dir_saida / "interacoes_tratadas.json"
        df.to_json(destino, orient="records", force_ascii=False, indent=2)
        self.logger.info(
            "  Interacoes tratadas: "
            + str(antes)
            + " -> "
            + str(len(df))
            + " registros ("
            + str(duplicados)
            + " duplicados removidos, "
            + str(self.corrigidos["interacoes"])
            + " corrigidos)"
        )
        return df

    # ------------------------------------------------------------------
    # RF04.3 - Tratar comentarios
    # ------------------------------------------------------------------
    def tratar_comentarios(self, lista):
        self.logger.info("Tratando comentarios...")
        antes = len(lista)
        df = pd.DataFrame(lista)
        original = df.copy()

        df["comentario"] = self._serie_texto(df["comentario"])
        df["avaliacao"] = pd.to_numeric(df["avaliacao"], errors="coerce").astype("Int64")
        df["data"] = self._serie_data(df["data"], "%Y-%m-%d")

        df["tags"] = df["tags"].apply(
            lambda t: sorted({str(x).strip().lower() for x in t if str(x).strip()})
            if isinstance(t, list)
            else []
        )

        colunas_cmp = ["comentario", "avaliacao", "data", "tags"]
        n_alterados = self._contar_alterados(original, df, colunas_cmp)

        chaves = ["usuario_id", "conteudo_id", "data"]
        duplicados = int(df.duplicated(subset=chaves).sum())
        if duplicados:
            df = df.drop_duplicates(subset=chaves, keep="first")

        self.corrigidos["comentarios"] = n_alterados + duplicados
        self._registrar_ausentes(
            "comentarios", df, ["comentario", "avaliacao", "data"]
        )

        destino = self.dir_saida / "comentarios_tratados.json"
        df.to_json(destino, orient="records", force_ascii=False, indent=2)
        self.logger.info(
            "  Comentarios tratados: "
            + str(antes)
            + " -> "
            + str(len(df))
            + " registros ("
            + str(duplicados)
            + " duplicados removidos, "
            + str(self.corrigidos["comentarios"])
            + " corrigidos)"
        )
        return df

    def get_corrigidos(self):
        return dict(self.corrigidos)
