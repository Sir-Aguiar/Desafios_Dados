-- RF06 — criação das tabelas estruturadas
-- Banco: plataforma_educacional (docker-compose.yml)
-- Schema: public (Superset conecta sem search_path extra)

BEGIN;

-- -------------------------------------------------------
-- 1. categoria
-- Origem: valores canônicos de catalogo.categoria (RF04)
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS categoria (
    categoria_id  SMALLSERIAL PRIMARY KEY,
    nome          VARCHAR(80) NOT NULL,
    CONSTRAINT uq_categoria_nome UNIQUE (nome)
);

INSERT INTO categoria (nome) VALUES
    ('Banco de Dados'),
    ('Business Intelligence'),
    ('Ciência de Dados'),
    ('DevOps & Cloud'),
    ('Engenharia de Dados'),
    ('Inteligência Artificial'),
    ('Programação & Software'),
    ('Segurança & Governança')
ON CONFLICT (nome) DO NOTHING;

-- -------------------------------------------------------
-- 2. usuario
-- Não há cadastro na origem: só usuario_id em interações.
-- A PK impede duplicidade do identificador.
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuario (
    usuario_id  INTEGER PRIMARY KEY
);

-- -------------------------------------------------------
-- 3. conteudo
-- Origem: catalogo_tratado.csv
-- categoria_id (FK) normaliza o texto da planilha.
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS conteudo (
    conteudo_id         INTEGER      PRIMARY KEY,
    titulo              VARCHAR(300) NOT NULL,
    tipo                VARCHAR(20)  NOT NULL,
    categoria_id        SMALLINT     NOT NULL,
    nivel               VARCHAR(20)  NOT NULL,
    carga_horaria_min   INTEGER      NOT NULL,
    data_publicacao     DATE         NOT NULL,
    descricao           TEXT,
    autor               VARCHAR(200),

    CONSTRAINT fk_conteudo_categoria
        FOREIGN KEY (categoria_id)
        REFERENCES categoria (categoria_id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT,

    CONSTRAINT ck_conteudo_tipo
        CHECK (tipo IN ('Artigo', 'Curso', 'Podcast', 'Vídeo')),

    CONSTRAINT ck_conteudo_nivel
        CHECK (nivel IN ('Básico', 'Intermediário', 'Avançado')),

    CONSTRAINT ck_conteudo_carga
        CHECK (carga_horaria_min >= 0)
);

CREATE INDEX IF NOT EXISTS ix_conteudo_categoria ON conteudo (categoria_id);
CREATE INDEX IF NOT EXISTS ix_conteudo_tipo      ON conteudo (tipo);

-- -------------------------------------------------------
-- 4. interacao
-- Origem: interacoes_tratadas.json
-- Unicidade de negócio = (usuario_id, conteudo_id, data_hora)
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS interacao (
    interacao_id          SERIAL PRIMARY KEY,
    usuario_id            INTEGER        NOT NULL,
    conteudo_id           INTEGER        NOT NULL,
    tipo_interacao        VARCHAR(30)    NOT NULL,
    data_hora             TIMESTAMP      NOT NULL,
    tempo_consumido       INTEGER        NOT NULL,
    percentual_conclusao  NUMERIC(5, 2)  NOT NULL,
    avaliacao_atribuida   SMALLINT,

    CONSTRAINT fk_interacao_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuario (usuario_id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT,

    CONSTRAINT fk_interacao_conteudo
        FOREIGN KEY (conteudo_id)
        REFERENCES conteudo (conteudo_id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT,

    CONSTRAINT uq_interacao_usuario_conteudo_data
        UNIQUE (usuario_id, conteudo_id, data_hora),

    CONSTRAINT ck_interacao_tipo
        CHECK (tipo_interacao IN (
            'avaliação',
            'compartilhamento',
            'conclusão',
            'curtida',
            'início',
            'visualização'
        )),

    CONSTRAINT ck_interacao_tempo
        CHECK (tempo_consumido >= 0),

    CONSTRAINT ck_interacao_percentual
        CHECK (percentual_conclusao >= 0 AND percentual_conclusao <= 100),

    CONSTRAINT ck_interacao_avaliacao
        CHECK (
            avaliacao_atribuida IS NULL
            OR (avaliacao_atribuida BETWEEN 1 AND 5)
        )
);

CREATE INDEX IF NOT EXISTS ix_interacao_usuario   ON interacao (usuario_id);
CREATE INDEX IF NOT EXISTS ix_interacao_conteudo  ON interacao (conteudo_id);
CREATE INDEX IF NOT EXISTS ix_interacao_tipo      ON interacao (tipo_interacao);
CREATE INDEX IF NOT EXISTS ix_interacao_data_hora ON interacao (data_hora);

-- -------------------------------------------------------
-- 5. recomendacao
-- Preenchida pelo RF11 a partir da geracao do RF10 (não vem dos arquivos brutos)
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS recomendacao (
    recomendacao_id  SERIAL PRIMARY KEY,
    usuario_id       INTEGER        NOT NULL,
    conteudo_id      INTEGER        NOT NULL,
    pontuacao        NUMERIC(5, 2)  NOT NULL,
    posicao          SMALLINT       NOT NULL,
    classificacao    VARCHAR(10)    NOT NULL,
    gerado_em        TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_recomendacao_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuario (usuario_id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT,

    CONSTRAINT fk_recomendacao_conteudo
        FOREIGN KEY (conteudo_id)
        REFERENCES conteudo (conteudo_id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT,

    CONSTRAINT uq_recomendacao_usuario_posicao_geracao
        UNIQUE (usuario_id, posicao, gerado_em),

    CONSTRAINT uq_recomendacao_usuario_conteudo_geracao
        UNIQUE (usuario_id, conteudo_id, gerado_em),

    CONSTRAINT ck_recomendacao_pontuacao
        CHECK (pontuacao >= 0 AND pontuacao <= 100),

    CONSTRAINT ck_recomendacao_posicao
        CHECK (posicao >= 1),

    CONSTRAINT ck_recomendacao_classificacao
        CHECK (classificacao IN ('Positivo', 'Estável', 'Negativo'))
);

CREATE INDEX IF NOT EXISTS ix_recomendacao_usuario  ON recomendacao (usuario_id);
CREATE INDEX IF NOT EXISTS ix_recomendacao_conteudo ON recomendacao (conteudo_id);

COMMIT;
