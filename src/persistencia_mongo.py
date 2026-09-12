"""
Persistencia semiestruturada no MongoDB (RF07).
Filtra comentarios tratados, enriquece com categoria do catalogo
e faz upsert na colecao comentarios.
"""
from datetime import datetime

import pandas as pd
from pymongo import ASCENDING, ReplaceOne
from pymongo.errors import CollectionInvalid, PyMongoError

from src.config import load_config, mongo_uri
from src.database import get_mongo_client, get_mongo_db, ping_mongo
from src.logger import get_logger
from src.validacao import CATEGORIAS_VALIDAS

NOME_COLECAO = "comentarios"
TAMANHO_LOTE = 1000

CAMPOS_COMENTARIO_OBRIGATORIOS = [
    "usuario_id",
    "conteudo_id",
    "avaliacao",
    "comentario",
    "data",
]

VALIDADOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "usuario_id",
            "conteudo_id",
            "avaliacao",
            "comentario",
            "tags",
            "data",
            "categoria",
        ],
        "properties": {
            "usuario_id": {"bsonType": ["int", "long"]},
            "conteudo_id": {"bsonType": ["int", "long"]},
            "avaliacao": {
                "bsonType": ["int", "long"],
                "minimum": 1,
                "maximum": 5,
            },
            "comentario": {"bsonType": "string"},
            "tags": {"bsonType": "array", "items": {"bsonType": "string"}},
            "data": {"bsonType": "date"},
            "categoria": {"bsonType": "string", "minLength": 1},
        },
    }
}


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


def _como_tags(valor):
    if _eh_nulo(valor):
        return []
    if hasattr(valor, "tolist") and not isinstance(valor, (list, tuple, str)):
        valor = valor.tolist()
    if not isinstance(valor, (list, tuple)):
        return []
    return sorted({str(item).strip().lower() for item in valor if str(item).strip()})


class PersistenciaMongo:
    """Cria a colecao comentarios e carrega os documentos tratados."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = load_config()
        mongo = self.config["mongo"]
        if not mongo.get("dbname"):
            raise RuntimeError("Nome do banco MongoDB ausente no .env (MONGO_DB).")
        self.client = get_mongo_client(self.config)
        self.db = get_mongo_db(self.client, self.config)

    def carregar(self, df_comentarios, df_catalogo):
        """Filtra, faz upsert e devolve a quantidade de documentos enviados."""
        destino = self.db.name + " / " + NOME_COLECAO
        self.logger.info(
            "Persistindo no MongoDB: " + destino + " (" + mongo_uri(self.config) + ")"
        )

        try:
            ping_mongo(self.client)
        except Exception:
            self.logger.exception(
                "Falha de conexao com o MongoDB em " + mongo_uri(self.config)
            )
            raise

        try:
            colecao = self._preparar_colecao()
        except Exception:
            self.logger.exception(
                "Falha de persistencia ao preparar a colecao " + NOME_COLECAO
            )
            raise

        documentos = self._montar_documentos(df_comentarios, df_catalogo)
        self.logger.info(
            "Documentos validos para carga: " + str(len(documentos)) + " comentarios"
        )

        try:
            self._upsert(colecao, documentos)
        except Exception:
            self.logger.exception("Falha de persistencia durante o upsert no MongoDB")
            raise

        self._consultar(colecao)
        return len(documentos)

    def comentarios_do_conteudo(self, conteudo_id, limite=10):
        return list(
            self.db[NOME_COLECAO]
            .find(
                {"conteudo_id": int(conteudo_id)},
                {"_id": 0},
            )
            .limit(limite)
        )

    def localizar_por_tag(self, tag, limite=10):
        return list(
            self.db[NOME_COLECAO]
            .find({"tags": tag}, {"_id": 0})
            .limit(limite)
        )

    def filtrar_por_nota(self, nota, minimo=False, limite=10):
        filtro = {"avaliacao": {"$gte": int(nota)}} if minimo else {"avaliacao": int(nota)}
        return list(self.db[NOME_COLECAO].find(filtro, {"_id": 0}).limit(limite))

    def agregar_por_categoria(self):
        return list(
            self.db[NOME_COLECAO].aggregate(
                [
                    {"$group": {"_id": "$categoria", "quantidade": {"$sum": 1}}},
                    {"$sort": {"quantidade": -1, "_id": 1}},
                ]
            )
        )

    def fechar(self):
        self.client.close()

    def _preparar_colecao(self):
        nomes = self.db.list_collection_names()
        if NOME_COLECAO in nomes:
            self.db.command(
                {
                    "collMod": NOME_COLECAO,
                    "validator": VALIDADOR,
                    "validationLevel": "strict",
                    "validationAction": "error",
                }
            )
        else:
            try:
                self.db.create_collection(
                    NOME_COLECAO,
                    validator=VALIDADOR,
                    validationLevel="strict",
                    validationAction="error",
                )
            except CollectionInvalid:
                self.db.command(
                    {
                        "collMod": NOME_COLECAO,
                        "validator": VALIDADOR,
                        "validationLevel": "strict",
                        "validationAction": "error",
                    }
                )

        colecao = self.db[NOME_COLECAO]
        colecao.create_index(
            [("usuario_id", ASCENDING), ("conteudo_id", ASCENDING), ("data", ASCENDING)],
            unique=True,
            name="uq_comentario_usuario_conteudo_data",
        )
        colecao.create_index([("conteudo_id", ASCENDING)], name="ix_comentario_conteudo")
        colecao.create_index([("tags", ASCENDING)], name="ix_comentario_tags")
        colecao.create_index([("avaliacao", ASCENDING)], name="ix_comentario_avaliacao")
        colecao.create_index([("categoria", ASCENDING)], name="ix_comentario_categoria")
        self.logger.info("Colecao " + NOME_COLECAO + ": validador e indices aplicados")
        return colecao

    def _mapa_categorias(self, df_catalogo):
        mapa = {}
        if df_catalogo is None or df_catalogo.empty:
            return mapa
        for _, row in df_catalogo.iterrows():
            cid = _como_int(row.get("conteudo_id"))
            categoria = _como_texto(row.get("categoria"))
            if cid is None or categoria is None:
                continue
            if categoria not in CATEGORIAS_VALIDAS:
                continue
            mapa[cid] = categoria
        return mapa

    def _montar_documentos(self, df_comentarios, df_catalogo):
        mapa = self._mapa_categorias(df_catalogo)
        if df_comentarios is None or df_comentarios.empty:
            return []

        documentos = []
        for _, row in df_comentarios.iterrows():
            if any(_eh_nulo(row.get(c)) for c in CAMPOS_COMENTARIO_OBRIGATORIOS):
                continue
            usuario_id = _como_int(row.get("usuario_id"))
            conteudo_id = _como_int(row.get("conteudo_id"))
            if usuario_id is None or conteudo_id is None:
                continue
            if conteudo_id not in mapa:
                continue
            try:
                avaliacao = int(row["avaliacao"])
                if avaliacao < 1 or avaliacao > 5:
                    continue
            except (ValueError, TypeError):
                continue
            data = self._como_data(row.get("data"))
            if data is None:
                continue
            comentario = _como_texto(row.get("comentario"))
            if comentario is None:
                continue
            documentos.append(
                {
                    "usuario_id": usuario_id,
                    "conteudo_id": conteudo_id,
                    "avaliacao": avaliacao,
                    "comentario": comentario,
                    "tags": _como_tags(row.get("tags")),
                    "data": data,
                    "categoria": mapa[conteudo_id],
                }
            )
        return documentos

    @staticmethod
    def _como_data(valor):
        if _eh_nulo(valor):
            return None
        if isinstance(valor, datetime):
            return datetime(valor.year, valor.month, valor.day)
        texto = str(valor).strip()
        if not texto or texto.lower() == "nan":
            return None
        if "T" in texto:
            texto = texto.split("T", 1)[0]
        try:
            return datetime.strptime(texto[:10], "%Y-%m-%d")
        except (ValueError, TypeError):
            return None

    def _upsert(self, colecao, documentos):
        if not documentos:
            return
        for inicio in range(0, len(documentos), TAMANHO_LOTE):
            lote = documentos[inicio : inicio + TAMANHO_LOTE]
            operacoes = [
                ReplaceOne(
                    {
                        "usuario_id": doc["usuario_id"],
                        "conteudo_id": doc["conteudo_id"],
                        "data": doc["data"],
                    },
                    doc,
                    upsert=True,
                )
                for doc in lote
            ]
            try:
                colecao.bulk_write(operacoes, ordered=False)
            except PyMongoError:
                raise

    def _consultar(self, colecao):
        total = colecao.count_documents({})
        self.logger.info("Consulta MongoDB (COUNT comentarios): " + str(total))
        if total == 0:
            return

        amostra = colecao.find_one({}, {"_id": 0, "conteudo_id": 1})
        conteudo_id = amostra.get("conteudo_id") if amostra else None
        if conteudo_id is not None:
            qtd_conteudo = colecao.count_documents({"conteudo_id": conteudo_id})
            self.logger.info(
                "  comentarios do conteudo "
                + str(conteudo_id)
                + ": "
                + str(qtd_conteudo)
            )
            for doc in self.comentarios_do_conteudo(conteudo_id, limite=3):
                self.logger.info(
                    "    usuario="
                    + str(doc.get("usuario_id"))
                    + " nota="
                    + str(doc.get("avaliacao"))
                    + " | "
                    + str(doc.get("comentario") or "")[:80]
                )

        qtd_tag = colecao.count_documents({"tags": "nlp"})
        self.logger.info("  documentos com tag nlp: " + str(qtd_tag))
        for doc in self.localizar_por_tag("nlp", limite=1):
            self.logger.info(
                "    amostra tag nlp: conteudo="
                + str(doc.get("conteudo_id"))
                + " tags="
                + str(doc.get("tags"))
            )

        qtd_nota = colecao.count_documents({"avaliacao": 5})
        qtd_gte = colecao.count_documents({"avaliacao": {"$gte": 4}})
        self.logger.info(
            "  avaliacoes nota=5: "
            + str(qtd_nota)
            + " | nota>=4: "
            + str(qtd_gte)
        )
        self.filtrar_por_nota(5, limite=1)

        for item in self.agregar_por_categoria():
            self.logger.info(
                "  categoria "
                + str(item.get("_id"))
                + ": "
                + str(item.get("quantidade"))
                + " comentarios"
            )
