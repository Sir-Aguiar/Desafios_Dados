"""
Cliente MongoDB compartilhado (RF07).
A URI e o nome do banco vêm do .env via src.config.
"""
from pymongo import MongoClient

from src.config import load_config, mongo_uri

TIMEOUT_MS = 5000


def get_mongo_client(config=None):
    """Cria um MongoClient com timeout curto de seleção do servidor."""
    cfg = config or load_config()
    return MongoClient(
        mongo_uri(cfg),
        serverSelectionTimeoutMS=TIMEOUT_MS,
    )


def get_mongo_db(client=None, config=None):
    """Devolve o banco configurado (cria o client se nao for informado)."""
    cfg = config or load_config()
    if client is None:
        client = get_mongo_client(cfg)
    return client[cfg["mongo"]["dbname"]]


def ping_mongo(client):
    """Confirma que o servidor responde. Levanta erro se a conexao falhar."""
    client.admin.command("ping")
