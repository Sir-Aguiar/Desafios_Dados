-- RF08 — extensão pgvector e tabela de embeddings
-- Banco: plataforma_educacional (docker-compose.yml)
--
-- Substitua __DIMENSAO__ pela dimensao do modelo
-- (384 no all-MiniLM-L6-v2; 768 no all-mpnet-base-v2).
-- O pipeline (src/embeddings.py) faz essa substituicao automaticamente.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS embedding_conteudo (
    conteudo_id   INTEGER        PRIMARY KEY,
    texto_origem  TEXT           NOT NULL,
    modelo        VARCHAR(200)   NOT NULL,
    vetor         vector(__DIMENSAO__) NOT NULL,
    gerado_em     TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_embedding_conteudo
        FOREIGN KEY (conteudo_id)
        REFERENCES conteudo (conteudo_id)
        ON UPDATE RESTRICT
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_embedding_conteudo_modelo
    ON embedding_conteudo (modelo);

-- Indice para busca por similaridade de cosseno (RF09).
CREATE INDEX IF NOT EXISTS ix_embedding_conteudo_vetor
    ON embedding_conteudo USING hnsw (vetor vector_cosine_ops);
