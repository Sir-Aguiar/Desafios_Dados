-- =====================================================================
-- ESTRUTURAS AUXILIARES PARA LOGS DE CARGA E LOTE (RF12)
-- =====================================================================

-- Tabela para persistir o resumo de qualidade da ingestão (alimenta KPI 3)
CREATE TABLE IF NOT EXISTS log_ingestao (
    id            SERIAL PRIMARY KEY,
    fonte         VARCHAR(50) NOT NULL,
    lidos         INTEGER     NOT NULL,
    validos       INTEGER     NOT NULL,
    invalidos     INTEGER     NOT NULL,
    incompletos   INTEGER     NOT NULL,
    duplicados    INTEGER     NOT NULL,
    corrigidos    INTEGER     NOT NULL,
    executado_em  TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para persistir o resumo operacional do lote de recomendação (alimenta KPI 1)
CREATE TABLE IF NOT EXISTS log_lote_recomendacao (
    id                     SERIAL PRIMARY KEY,
    gerado_em              TIMESTAMP NOT NULL,
    total_avaliados        INTEGER   NOT NULL,
    persistidas            INTEGER   NOT NULL,
    positivas              INTEGER   NOT NULL,
    estaveis               INTEGER   NOT NULL,
    descartadas_pontuacao  INTEGER   NOT NULL,
    descartadas_conclusao  INTEGER   NOT NULL
);

-- Popula com os dados reais calculados no pipeline se estiverem vazias
INSERT INTO log_ingestao (fonte, lidos, validos, invalidos, incompletos, duplicados, corrigidos, executado_em)
SELECT 'catalogo', 1000, 1000, 0, 0, 0, 0, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM log_ingestao WHERE fonte = 'catalogo');

INSERT INTO log_ingestao (fonte, lidos, validos, invalidos, incompletos, duplicados, corrigidos, executado_em)
SELECT 'interacoes', 1000, 1000, 0, 0, 0, 356, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM log_ingestao WHERE fonte = 'interacoes');

INSERT INTO log_ingestao (fonte, lidos, validos, invalidos, incompletos, duplicados, corrigidos, executado_em)
SELECT 'comentarios', 1000, 1000, 0, 0, 0, 837, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM log_ingestao WHERE fonte = 'comentarios');

INSERT INTO log_lote_recomendacao (gerado_em, total_avaliados, persistidas, positivas, estaveis, descartadas_pontuacao, descartadas_conclusao)
SELECT '2026-09-13 15:02:15', 38007, 744, 581, 163, 37109, 154
WHERE NOT EXISTS (SELECT 1 FROM log_lote_recomendacao);

-- Views
CREATE OR REPLACE VIEW vw_kpi_seletividade_recomendacao AS
SELECT
    gerado_em,
    persistidas                                                         AS recomendacoes_persistidas,
    descartadas_pontuacao,
    descartadas_conclusao,
    total_avaliados                                                     AS total_candidatos_avaliados,
    ROUND(
        (persistidas::numeric / NULLIF(total_avaliados, 0) * 100)::numeric, 2
    )                                                                   AS taxa_seletividade_pct,
    ROUND(
        (positivas::numeric / NULLIF(persistidas, 0) * 100)::numeric, 2
    )                                                                   AS taxa_alta_afinidade_pct
FROM log_lote_recomendacao
WHERE gerado_em = (SELECT MAX(gerado_em) FROM log_lote_recomendacao);

CREATE OR REPLACE VIEW vw_kpi_recomendacoes_categoria_status AS
SELECT
    cat.nome                            AS categoria_nome,
    r.classificacao,
    COUNT(r.recomendacao_id)            AS qtd_recomendacoes,
    ROUND(AVG(r.pontuacao)::numeric, 2) AS pontuacao_media,
    ROUND(MIN(r.pontuacao)::numeric, 2) AS pontuacao_minima,
    ROUND(MAX(r.pontuacao)::numeric, 2) AS pontuacao_maxima
FROM recomendacao r
JOIN conteudo co ON co.conteudo_id = r.conteudo_id
JOIN categoria cat ON cat.categoria_id = co.categoria_id
WHERE r.gerado_em = (SELECT MAX(gerado_em) FROM recomendacao)
GROUP BY cat.nome, r.classificacao
ORDER BY cat.nome, r.classificacao;

CREATE OR REPLACE VIEW vw_kpi_qualidade_ingestao AS
SELECT
    fonte,
    lidos,
    validos,
    corrigidos,
    invalidos,
    incompletos,
    duplicados,
    ROUND((corrigidos::numeric / NULLIF(lidos, 0) * 100)::numeric, 2)   AS taxa_correcao_pct,
    ROUND((validos::numeric / NULLIF(lidos, 0) * 100)::numeric, 2)      AS taxa_conformidade_pct,
    executado_em
FROM log_ingestao
WHERE id IN (SELECT MAX(id) FROM log_ingestao GROUP BY fonte);

CREATE OR REPLACE VIEW vw_kpi_desempenho_categoria_tipo AS
SELECT
    cat.nome                                                             AS categoria_nome,
    co.tipo                                                              AS tipo_conteudo,
    COUNT(DISTINCT co.conteudo_id)                                       AS qtd_conteudos,
    COUNT(i.interacao_id)                                                AS total_interacoes,
    COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'visualização') AS visualizacoes,
    COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'início')       AS inicios,
    COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'conclusão' OR i.percentual_conclusao >= 100) AS conclusoes,
    ROUND(
        (COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'conclusão' OR i.percentual_conclusao >= 100)::numeric /
         NULLIF(COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao IN ('início', 'visualização')), 0) * 100)::numeric, 2
    )                                                                    AS taxa_conclusao_pct,
    ROUND(AVG(i.avaliacao_atribuida)::numeric, 2)                        AS avaliacao_media,
    ROUND(AVG(i.tempo_consumido)::numeric, 1)                            AS tempo_medio_consumido_min
FROM categoria cat
JOIN conteudo co ON co.categoria_id = cat.categoria_id
LEFT JOIN interacao i ON i.conteudo_id = co.conteudo_id
GROUP BY cat.nome, co.tipo
ORDER BY cat.nome, co.tipo;

CREATE OR REPLACE VIEW vw_kpi_evolucao_temporal_diaria AS
SELECT
    i.data_hora::date                                                    AS data,
    COUNT(i.interacao_id)                                                AS total_interacoes,
    COUNT(DISTINCT i.usuario_id)                                         AS usuarios_ativos_dia,
    COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'visualização') AS visualizacoes,
    COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'início')       AS inicios,
    COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'conclusão' OR i.percentual_conclusao >= 100) AS conclusoes,
    COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'curtida')      AS curtidas,
    COUNT(i.interacao_id) FILTER (WHERE i.avaliacao_atribuida IS NOT NULL) AS avaliacoes,
    ROUND(AVG(i.avaliacao_atribuida)::numeric, 2)                        AS avaliacao_media_dia,
    SUM(i.tempo_consumido)                                               AS tempo_total_consumido_min
FROM interacao i
GROUP BY i.data_hora::date
ORDER BY data ASC;
