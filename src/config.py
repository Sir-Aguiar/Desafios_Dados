import os
from pathlib import Path
from urllib.parse import quote_plus

import yaml
from dotenv import load_dotenv

RAIZ_PROJETO = Path(__file__).resolve().parent.parent

_config_cache = None


def load_config():
    global _config_cache

    # Verifica se a configuração já foi carregada
    if _config_cache is not None:
        return _config_cache

    # Carrega as variáveis de ambiente
    load_dotenv(RAIZ_PROJETO / ".env")

    # Carrega o arquivo de configuração YAML
    caminho_yaml = RAIZ_PROJETO / "config.yaml"

    with open(caminho_yaml, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Configuração condicional do modelo de embeddings
    LOCAL_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    LOCAL_EMBEDDING_DIMENSIONS = os.getenv("EMBEDDING_DIMENSIONS")

    config["embeddings"]["dimensao"] = int(config["embeddings"]["dimensao"])

    if LOCAL_EMBEDDING_MODEL:
        config["embeddings"]["modelo"] = LOCAL_EMBEDDING_MODEL.strip().strip('"').strip(
            "'"
        )
    if LOCAL_EMBEDDING_DIMENSIONS:
        config["embeddings"]["dimensao"] = int(LOCAL_EMBEDDING_DIMENSIONS)

    # Configurações de PostgreSQL
    config["postgres"] = {
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "dbname": os.getenv("POSTGRES_DB"),
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
    }

    # Configurações de MongoDB
    config["mongo"] = {
        "uri": os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
        "dbname": os.getenv("MONGO_DB", "plataforma_educacional"),
    }

    # Configurações de fontes de dados
    for chave, valor in config["fontes_dados"].items():
        config["fontes_dados"][chave] = str(RAIZ_PROJETO / valor)

    # Salva a configuração em cache
    _config_cache = config

    # Retorna a configuração
    return config


def postgres_url(config=None):
    """Monta a URL SQLAlchemy a partir das credenciais do .env."""
    pg = (config or load_config())["postgres"]
    usuario = quote_plus(str(pg.get("user") or ""))
    senha = quote_plus(str(pg.get("password") or ""))
    host = pg.get("host") or "localhost"
    porta = pg.get("port") or "5432"
    banco = pg.get("dbname") or ""
    return f"postgresql+psycopg2://{usuario}:{senha}@{host}:{porta}/{banco}"


def mongo_uri(config=None):
    """Devolve a URI do MongoDB definida no .env."""
    mongo = (config or load_config())["mongo"]
    return mongo.get("uri") or "mongodb://localhost:27017/"
