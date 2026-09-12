"""
Modulo de tratamento e padronizacao - RF04.
Remove espacos, padroniza dominios, converte datas e numericos,
elimina duplicidades. Os arquivos ORIGINAIS nao sao modificados:
o resultado vai para dados/processados/.
"""
from pathlib import Path
import pandas as pd

from src.config import load_config
from src.logger import get_logger


class Tratador:
    """Trata e padroniza os dados apos a validacao."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = load_config()
        self.dir_saida = Path("dados/processados")
        self.dir_saida.mkdir(parents=True, exist_ok=True)
        self.corrigidos = 0  # conta registros que sofreram alguma correcao

    # ------------------------------------------------------------------
    # RF04.1 - Tratar catalogo
    # ------------------------------------------------------------------
    def tratar_catalogo(self, df):
        self.logger.info("Tratando catalogo...")
        antes = len(df)
        df = df.copy()

        # 1) Remover espacos nas colunas de texto
        colunas_texto = ["titulo", "tipo", "categoria", "nivel", "descricao", "autor"]
        for col in colunas_texto:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        # 2) Padronizar categorias / tipos / niveis (Title Case)
        df["tipo"] = df["tipo"].str.strip().str.title()
        df["categoria"] = df["categoria"].str.strip()
        df["nivel"] = df["nivel"].str.strip().str.title()

        # 3) Carga horaria: garantir inteiro nao-negativo
        df["carga_horaria_min"] = pd.to_numeric(df["carga_horaria_min"], errors="coerce").fillna(0).astype(int)

        # 4) Data em formato ISO YYYY-MM-DD
        df["data_publicacao"] = pd.to_datetime(df["data_publicacao"], errors="coerce").dt.strftime("%Y-%m-%d")

        # 5) Remover duplicatas por conteudo_id (mantem primeira ocorrencia)
        duplicados = df.duplicated(subset=["conteudo_id"]).sum()
        if duplicados:
            self.corrigidos += duplicados
            df = df.drop_duplicates(subset=["conteudo_id"], keep="first")

        # 6) Salvar
        destino = self.dir_saida / "catalogo_tratado.csv"
        df.to_csv(destino, index=False, encoding="utf-8")
        self.logger.info("  Catalogo tratado: " + str(antes) + " -> " + str(len(df))
                         + " registros (" + str(duplicados) + " duplicados removidos)")
        return df

    # ------------------------------------------------------------------
    # RF04.2 - Tratar interacoes
    # ------------------------------------------------------------------
    def tratar_interacoes(self, df):
        self.logger.info("Tratando interacoes...")
        antes = len(df)
        df = df.copy()

        # 1) Padronizar tipo_interacao (Title Case)
        df["tipo_interacao"] = df["tipo_interacao"].astype(str).str.strip()

        # 2) Datas para ISO 8601
        df["data_hora"] = pd.to_datetime(df["data_hora"], errors="coerce").dt.strftime("%Y-%m-%dT%H:%M:%S")

        # 3) Numericos
        df["tempo_consumido"] = pd.to_numeric(df["tempo_consumido"], errors="coerce").fillna(0).astype(int)
        df["percentual_conclusao"] = pd.to_numeric(df["percentual_conclusao"], errors="coerce").fillna(0.0).round(2)
        df["avaliacao_atribuida"] = pd.to_numeric(df["avaliacao_atribuida"], errors="coerce")

        # 4) Remover duplicatas pela tripla (usuario, conteudo, data_hora)
        chaves = ["usuario_id", "conteudo_id", "data_hora"]
        duplicados = df.duplicated(subset=chaves).sum()
        if duplicados:
            self.corrigidos += duplicados
            df = df.drop_duplicates(subset=chaves, keep="first")

        # 5) Salvar
        destino = self.dir_saida / "interacoes_tratadas.json"
        df.to_json(destino, orient="records", force_ascii=False, indent=2)
        self.logger.info("  Interacoes tratadas: " + str(antes) + " -> " + str(len(df))
                         + " registros (" + str(duplicados) + " duplicados removidos)")
        return df

    # ------------------------------------------------------------------
    # RF04.3 - Tratar comentarios
    # ------------------------------------------------------------------
    def tratar_comentarios(self, lista):
        self.logger.info("Tratando comentarios...")
        antes = len(lista)
        df = pd.DataFrame(lista)

        # 1) Trim no texto do comentario
        df["comentario"] = df["comentario"].astype(str).str.strip()

        # 2) Avaliacao como inteiro
        df["avaliacao"] = pd.to_numeric(df["avaliacao"], errors="coerce").fillna(0).astype(int)

        # 3) Data ISO
        df["data"] = pd.to_datetime(df["data"], errors="coerce").dt.strftime("%Y-%m-%d")

        # 4) Tags: garantir lista de strings sem espacos
        df["tags"] = df["tags"].apply(
            lambda t: sorted(set(str(x).strip().lower() for x in t)) if isinstance(t, list) else []
        )

        # 5) Remover duplicatas por (usuario, conteudo, data)
        chaves = ["usuario_id", "conteudo_id", "data"]
        duplicados = df.duplicated(subset=chaves).sum()
        if duplicados:
            self.corrigidos += duplicados
            df = df.drop_duplicates(subset=chaves, keep="first")

        # 6) Salvar
        destino = self.dir_saida / "comentarios_tratados.json"
        df.to_json(destino, orient="records", force_ascii=False, indent=2)
        self.logger.info("  Comentarios tratados: " + str(antes) + " -> " + str(len(df))
                         + " registros (" + str(duplicados) + " duplicados removidos)")
        return df

    def get_corrigidos(self):
        return self.corrigidos