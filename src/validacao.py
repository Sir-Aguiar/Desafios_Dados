"""
Modulo de validacao dos dados - RF03.
Classifica cada registro como: valido, invalido, incompleto ou duplicado.
Registra o motivo de cada classificacao nao-valida.
"""
import pandas as pd

from src.logger import get_logger

# ----------------------------------------------------------------------
# Dominios validos (descobertos pela analise dos dados reais)
# ----------------------------------------------------------------------
TIPOS_VALIDOS = {"Artigo", "Curso", "Podcast", "Vídeo"}
CATEGORIAS_VALIDAS = {
    "Banco de Dados", "Business Intelligence", "Ciência de Dados",
    "DevOps & Cloud", "Engenharia de Dados", "Inteligência Artificial",
    "Programação & Software", "Segurança & Governança",
}
NIVEIS_VALIDOS = {"Avançado", "Básico", "Intermediário"}
TIPOS_INTERACAO_VALIDOS = {
    "avaliação", "compartilhamento", "conclusão",
    "curtida", "início", "visualização",
}


class Validador:
    """Valida os registros das 3 fontes e devolve um relatorio detalhado."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.relatorios = {
            "catalogo": {"validos": 0, "invalidos": 0, "incompletos": 0, "duplicados": 0, "motivos": []},
            "interacoes": {"validos": 0, "invalidos": 0, "incompletos": 0, "duplicados": 0, "motivos": []},
            "comentarios": {"validos": 0, "invalidos": 0, "incompletos": 0, "duplicados": 0, "motivos": []},
        }

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    def _registrar_motivo(self, fonte, registro_id, motivo, tipo="invalido"):
        self.relatorios[fonte][tipo] += 1
        self.relatorios[fonte]["motivos"].append({
            "id": registro_id,
            "classificacao": tipo,
            "motivo": motivo,
        })

    # ------------------------------------------------------------------
    # RF03.1 - Validar o catalogo
    # ------------------------------------------------------------------
    def validar_catalogo(self, df):
        self.logger.info("Validando catalogo...")
        ids_vistos = set()
        colunas_obrigatorias = ["conteudo_id", "titulo", "tipo", "categoria",
                                "nivel", "carga_horaria_min", "data_publicacao"]

        for idx, row in df.iterrows():
            cid = row.get("conteudo_id")

            # 1) Duplicado?
            if cid in ids_vistos:
                self._registrar_motivo("catalogo", cid, "conteudo_id duplicado", "duplicados")
                continue
            ids_vistos.add(cid)

            # 2) Incompleto?
            faltando = [c for c in colunas_obrigatorias if pd.isna(row.get(c))]
            if faltando:
                self._registrar_motivo("catalogo", cid, "campos ausentes: " + str(faltando), "incompletos")
                continue

            # 3) Invalido?
            motivos = []
            if row["tipo"] not in TIPOS_VALIDOS:
                motivos.append("tipo invalido: " + str(row["tipo"]))
            if row["categoria"] not in CATEGORIAS_VALIDAS:
                motivos.append("categoria invalida: " + str(row["categoria"]))
            if row["nivel"] not in NIVEIS_VALIDOS:
                motivos.append("nivel invalido: " + str(row["nivel"]))
            try:
                carga = int(row["carga_horaria_min"])
                if carga < 0:
                    motivos.append("carga_horaria negativa: " + str(carga))
            except (ValueError, TypeError):
                motivos.append("carga_horaria nao-numerica: " + str(row["carga_horaria_min"]))

            if motivos:
                self._registrar_motivo("catalogo", cid, "; ".join(motivos), "invalidos")
                continue

            self.relatorios["catalogo"]["validos"] += 1

        r = self.relatorios["catalogo"]
        self.logger.info("  Catalogo: " + str(r["validos"]) + " validos, "
                         + str(r["invalidos"]) + " invalidos, "
                         + str(r["incompletos"]) + " incompletos, "
                         + str(r["duplicados"]) + " duplicados")

    # ------------------------------------------------------------------
    # RF03.2 - Validar as interacoes
    # ------------------------------------------------------------------
    def validar_interacoes(self, df, ids_conteudos_validos, ids_usuarios_validos):
        self.logger.info("Validando interacoes...")
        colunas_obrigatorias = ["usuario_id", "conteudo_id", "tipo_interacao",
                                "data_hora", "tempo_consumido", "percentual_conclusao"]
        chaves_vistas = set()

        for idx, row in df.iterrows():
            uid = row.get("usuario_id")
            cid = row.get("conteudo_id")

            # 1) Duplicado?
            chave = (uid, cid, str(row.get("data_hora")))
            if chave in chaves_vistas:
                self._registrar_motivo("interacoes", str(uid) + "-" + str(cid),
                                       "interacao duplicada", "duplicados")
                continue
            chaves_vistas.add(chave)

            # 2) Incompleto?
            faltando = [c for c in colunas_obrigatorias if pd.isna(row.get(c))]
            if faltando:
                self._registrar_motivo("interacoes", str(uid) + "-" + str(cid),
                                       "campos ausentes: " + str(faltando), "incompletos")
                continue

            # 3) Invalido?
            motivos = []
            if row["tipo_interacao"] not in TIPOS_INTERACAO_VALIDOS:
                motivos.append("tipo_interacao invalido: " + str(row["tipo_interacao"]))
            if uid not in ids_usuarios_validos:
                motivos.append("usuario_id inexistente: " + str(uid))
            if cid not in ids_conteudos_validos:
                motivos.append("conteudo_id inexistente: " + str(cid))
            try:
                tempo = int(row["tempo_consumido"])
                if tempo < 0:
                    motivos.append("tempo_consumido negativo: " + str(tempo))
            except (ValueError, TypeError):
                motivos.append("tempo_consumido nao-numerico: " + str(row["tempo_consumido"]))
            try:
                perc = float(row["percentual_conclusao"])
                if perc < 0 or perc > 100:
                    motivos.append("percentual fora de 0-100: " + str(perc))
            except (ValueError, TypeError):
                motivos.append("percentual nao-numerico: " + str(row["percentual_conclusao"]))

            aval = row.get("avaliacao_atribuida")
            if aval is not None and not pd.isna(aval):
                try:
                    av = int(aval)
                    if av < 1 or av > 5:
                        motivos.append("avaliacao fora de 1-5: " + str(av))
                except (ValueError, TypeError):
                    motivos.append("avaliacao nao-numerica: " + str(aval))

            if motivos:
                self._registrar_motivo("interacoes", str(uid) + "-" + str(cid),
                                       "; ".join(motivos), "invalidos")
                continue

            self.relatorios["interacoes"]["validos"] += 1

        r = self.relatorios["interacoes"]
        self.logger.info("  Interacoes: " + str(r["validos"]) + " validos, "
                         + str(r["invalidos"]) + " invalidos, "
                         + str(r["incompletos"]) + " incompletos, "
                         + str(r["duplicados"]) + " duplicados")

    # ------------------------------------------------------------------
    # RF03.3 - Validar os comentarios
    # ------------------------------------------------------------------
    def validar_comentarios(self, lista, ids_conteudos_validos, ids_usuarios_validos):
        self.logger.info("Validando comentarios...")
        colunas_obrigatorias = ["usuario_id", "conteudo_id", "avaliacao", "comentario", "data"]
        chaves_vistas = set()

        for coment in lista:
            uid = coment.get("usuario_id")
            cid = coment.get("conteudo_id")

            # 1) Duplicado?
            chave = (uid, cid, coment.get("data"))
            if chave in chaves_vistas:
                self._registrar_motivo("comentarios", str(uid) + "-" + str(cid),
                                       "comentario duplicado", "duplicados")
                continue
            chaves_vistas.add(chave)

            # 2) Incompleto?
            faltando = [c for c in colunas_obrigatorias if coment.get(c) in (None, "")]
            if faltando:
                self._registrar_motivo("comentarios", str(uid) + "-" + str(cid),
                                       "campos ausentes: " + str(faltando), "incompletos")
                continue

            # 3) Invalido?
            motivos = []
            try:
                av = int(coment["avaliacao"])
                if av < 1 or av > 5:
                    motivos.append("avaliacao fora de 1-5: " + str(av))
            except (ValueError, TypeError):
                motivos.append("avaliacao nao-numerica: " + str(coment["avaliacao"]))
            if uid not in ids_usuarios_validos:
                motivos.append("usuario_id inexistente: " + str(uid))
            if cid not in ids_conteudos_validos:
                motivos.append("conteudo_id inexistente: " + str(cid))
            if "tags" in coment and not isinstance(coment["tags"], list):
                motivos.append("tags nao e lista")

            if motivos:
                self._registrar_motivo("comentarios", str(uid) + "-" + str(cid),
                                       "; ".join(motivos), "invalidos")
                continue

            self.relatorios["comentarios"]["validos"] += 1

        r = self.relatorios["comentarios"]
        self.logger.info("  Comentarios: " + str(r["validos"]) + " validos, "
                         + str(r["invalidos"]) + " invalidos, "
                         + str(r["incompletos"]) + " incompletos, "
                         + str(r["duplicados"]) + " duplicados")

    def get_relatorios(self):
        return self.relatorios