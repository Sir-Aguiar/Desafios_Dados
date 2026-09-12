"""
Busca por similaridade semantica (RF09).

Recebe uma consulta em linguagem natural, gera o embedding com o
mesmo modelo do RF08 e devolve os conteudos mais proximos no pgvector.
"""
import json
import sys
from datetime import datetime

from sqlalchemy import func, literal, select

from src.config import RAIZ_PROJETO, load_config
from src.embeddings import GeradorEmbeddings
from src.logger import get_logger
from src.models import Categoria, Conteudo, EmbeddingConteudo

CAMINHO_SAIDA = RAIZ_PROJETO / "dados" / "processados" / "busca_semantica.json"

CONSULTAS_PADRAO = [
    "Quero aprender os fundamentos de banco de dados para inteligência artificial.",
    "Como orquestrar microsserviços com Kubernetes na prática?",
    "Preciso de conteúdo sobre Python avançado com orientação a objetos e decorators.",
]


class BuscadorSemantico:
    """Consulta o pgvector e ranqueia conteudos por similaridade de cosseno."""

    def __init__(self, gerador=None):
        self.logger = get_logger(__name__)
        self.config = load_config()
        busca = self.config.get("busca_semantica") or {}
        self.top_k = int(busca.get("top_k_padrao") or 5)
        consultas = busca.get("consultas_demonstracao") or CONSULTAS_PADRAO
        self.consultas_demonstracao = [str(c).strip() for c in consultas if str(c).strip()]
        if not self.consultas_demonstracao:
            self.consultas_demonstracao = list(CONSULTAS_PADRAO)
        self.gerador = gerador or GeradorEmbeddings()

    def buscar(self, consulta, top_k=None):
        """Devolve os top_k conteudos mais semelhantes a uma frase em portugues."""
        texto = (consulta or "").strip()
        if not texto:
            raise ValueError("A consulta semantica nao pode ser vazia.")
        k = self._top_k(top_k)
        self.logger.info(
            "Consulta semantica (top_k=" + str(k) + "): " + texto
        )

        session = self.gerador.SessionLocal()
        try:
            total = session.scalar(select(func.count()).select_from(EmbeddingConteudo))
            if not total:
                self.logger.warning(
                    "Nenhum embedding no PostgreSQL; busca semantica sem resultados."
                )
                return []

            vetor = [float(x) for x in self.gerador.encode_textos([texto])[0]]
            distancia = EmbeddingConteudo.vetor.cosine_distance(vetor)
            similaridade = literal(1.0) - distancia
            linhas = session.execute(
                select(
                    Conteudo.conteudo_id,
                    Conteudo.titulo,
                    Categoria.nome,
                    Conteudo.tipo,
                    distancia.label("distancia"),
                    similaridade.label("similaridade"),
                )
                .join(Conteudo, Conteudo.conteudo_id == EmbeddingConteudo.conteudo_id)
                .join(Categoria, Categoria.categoria_id == Conteudo.categoria_id)
                .where(EmbeddingConteudo.modelo == self.gerador.modelo_nome)
                .order_by(distancia)
                .limit(k)
            ).all()

            resultados = []
            for posicao, row in enumerate(linhas, start=1):
                item = {
                    "posicao": posicao,
                    "conteudo_id": int(row.conteudo_id),
                    "titulo": row.titulo,
                    "categoria": row.nome,
                    "tipo": row.tipo,
                    "similaridade": round(float(row.similaridade), 4),
                    "distancia": round(float(row.distancia), 4),
                }
                resultados.append(item)
                self.logger.info(
                    "  #"
                    + str(item["posicao"])
                    + " id="
                    + str(item["conteudo_id"])
                    + " | "
                    + item["categoria"]
                    + " | "
                    + item["tipo"]
                    + " | sim="
                    + str(item["similaridade"])
                    + " | "
                    + item["titulo"]
                )
            if not resultados:
                self.logger.warning(
                    "Busca semantica sem resultados para o modelo "
                    + self.gerador.modelo_nome
                )
            return resultados
        except Exception:
            self.logger.exception("Falha na busca semantica")
            raise
        finally:
            session.close()

    def demonstrar(self, consultas=None, top_k=None):
        """Executa pelo menos tres consultas distintas e grava o JSON de evidencia."""
        frases = consultas if consultas is not None else self.consultas_demonstracao
        frases = [str(c).strip() for c in frases if str(c).strip()]
        if len(frases) < 3:
            raise ValueError(
                "O RF09 exige pelo menos tres consultas semanticas diferentes."
            )

        k = self._top_k(top_k)
        self.logger.info(
            "Demonstrando "
            + str(len(frases))
            + " consultas semanticas (top_k="
            + str(k)
            + ", modelo="
            + self.gerador.modelo_nome
            + ")"
        )

        relatorio = {
            "modelo": self.gerador.modelo_nome,
            "top_k": k,
            "consultado_em": datetime.now().isoformat(timespec="seconds"),
            "consultas": [],
        }
        for frase in frases:
            relatorio["consultas"].append(
                {"consulta": frase, "resultados": self.buscar(frase, top_k=k)}
            )
        self._gravar(relatorio)
        return relatorio

    def _top_k(self, top_k):
        k = self.top_k if top_k is None else int(top_k)
        if k < 1:
            raise ValueError("top_k deve ser um inteiro >= 1.")
        return k

    def _gravar(self, relatorio):
        CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
        with open(CAMINHO_SAIDA, "w", encoding="utf-8") as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        self.logger.info("Resultados da busca semantica gravados em " + str(CAMINHO_SAIDA))


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    buscador = BuscadorSemantico()
    if args:
        buscador.buscar(" ".join(args))
        return 0
    buscador.demonstrar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
