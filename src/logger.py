import logging
import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
DIR_LOGS = RAIZ_PROJETO / "logs"
DIR_LOGS.mkdir(exist_ok=True)

_formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_configurado = False


def _configurar_root():
    global _configurado
    if _configurado:
        return
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(_formatter)
    root.addHandler(console)
    arquivo = logging.FileHandler(DIR_LOGS / "pipeline.log", encoding="utf-8")
    arquivo.setFormatter(_formatter)
    root.addHandler(arquivo)
    _configurado = True


def get_logger(nome):
    _configurar_root()
    return logging.getLogger(nome)
