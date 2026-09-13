-- =====================================================================
-- RF12 — Visões SQL de Métricas e KPIs (Plataforma Educacional)
-- Banco: plataforma_educacional
-- Schema: public
--
-- Estas views disponibilizam métricas operacionais e KPIs estratégicos
-- prontos para consumo pelo Apache Superset e relatórios analíticos.
-- =====================================================================

BEGIN;

-- ---------------------------------------------------------------------
-- 1. vw_kpi_metricas_gerais
-- Métricas operacionais e KPIs consolidados em linha única (Big Numbers / Cartões)
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_kpi_metricas_gerais AS
WITH ultimas_recs AS (
    SELECT *
    FROM recomendacao
    WHERE gerado_em = (SELECT MAX(gerado_em) FROM recomendacao)
)
SELECT
    (SELECT COUNT(*) FROM usuario)                                            AS total_usuarios,
    (SELECT COUNT(*) FROM conteudo)                                           AS total_conteudos,
    (SELECT COUNT(*) FROM interacao)                                          AS total_interacoes,
    (SELECT COUNT(*) FROM interacao WHERE avaliacao_atribuida IS NOT NULL)    AS total_avaliacoes,
    (SELECT ROUND(AVG(avaliacao_atribuida)::numeric, 2)
     FROM interacao WHERE avaliacao_atribuida IS NOT NULL)                    AS avaliacao_media_global,
    (SELECT COUNT(*)
     FROM interacao
     WHERE tipo_interacao = 'conclusão' OR percentual_conclusao >= 100)       AS total_conclusoes,
    (SELECT ROUND(
        (COUNT(*) FILTER (WHERE tipo_interacao = 'conclusão' OR percentual_conclusao >= 100)::numeric /
         NULLIF(COUNT(*) FILTER (WHERE tipo_interacao IN ('início', 'visualização')), 0) * 100)::numeric, 2)
     FROM interacao)                                                          AS taxa_conclusao_global_pct,
    (SELECT ROUND(AVG(tempo_consumido)::numeric, 1) FROM interacao)           AS tempo_medio_consumo_min,
    (SELECT COUNT(*) FROM ultimas_recs)                                       AS total_recomendacoes_lote,
    (SELECT ROUND(
        (COUNT(*) FILTER (WHERE classificacao = 'Positivo')::numeric /
         NULLIF(COUNT(*), 0) * 100)::numeric, 2)
     FROM ultimas_recs)                                                       AS taxa_recomendacoes_positivas_pct;

-- ---------------------------------------------------------------------
-- 2. vw_kpi_desempenho_categoria
-- Desempenho analítico agrupado por Categoria e Tipo de Conteúdo (Gráfico de Barras)
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_kpi_desempenho_categoria AS
SELECT
    cat.nome                                                             AS categoria_nome,
    co.tipo                                                              AS tipo_conteudo,
    COUNT(DISTINCT co.conteudo_id)                                       AS qtd_conteudos,
    COUNT(i.interacao_id)                                                AS total_interacoes,
    COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'visualização') AS visualizacoes,
    COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'início')       AS inicios,
    COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'conclusão' OR i.percentual_conclusao >= 100) AS conclusoes,
    COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'curtida')      AS curtidas,
    COUNT(i.interacao_id) FILTER (WHERE i.avaliacao_atribuida IS NOT NULL) AS avaliacoes,
    ROUND(
        (COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'conclusão' OR i.percentual_conclusao >= 100)::numeric /
         NULLIF(COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao IN ('início', 'visualização')), 0) * 100)::numeric, 2
    )                                                                    AS taxa_conclusao_pct,
    ROUND(AVG(i.avaliacao_atribuida)::numeric, 2)                        AS avaliacao_media,
    ROUND(AVG(i.tempo_consumido)::numeric, 1)                            AS tempo_medio_consumido_min
FROM categoria cat
JOIN conteudo co ON co.categoria_id = cat.categoria_id
LEFT JOIN interacao i ON i.conteudo_id = co.conteudo_id
GROUP BY cat.nome, co.tipo;

-- ---------------------------------------------------------------------
-- 3. vw_kpi_evolucao_temporal
-- Série temporal de engajamento diário (Gráfico de Linhas)
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_kpi_evolucao_temporal AS
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
ORDER BY data;

-- ---------------------------------------------------------------------
-- 4. vw_kpi_analise_conteudos
-- Detalhamento individual dos conteúdos com filtros dimensionais (Tabelas e Filtros Superset)
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_kpi_analise_conteudos AS
SELECT
    co.conteudo_id,
    co.titulo,
    cat.nome                                                             AS categoria_nome,
    co.tipo,
    co.nivel,
    co.carga_horaria_min,
    co.data_publicacao,
    co.autor,
    COUNT(i.interacao_id)                                                AS total_interacoes,
    COUNT(DISTINCT i.usuario_id)                                         AS usuarios_distintos,
    COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'visualização') AS visualizacoes,
    COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'conclusão' OR i.percentual_conclusao >= 100) AS conclusoes,
    ROUND(
        (COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'conclusão' OR i.percentual_conclusao >= 100)::numeric /
         NULLIF(COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao IN ('início', 'visualização')), 0) * 100)::numeric, 2
    )                                                                    AS taxa_conclusao_pct,
    ROUND(AVG(i.avaliacao_atribuida)::numeric, 2)                        AS avaliacao_media,
    ROUND(AVG(i.tempo_consumido)::numeric, 1)                            AS tempo_medio_minutos
FROM conteudo co
JOIN categoria cat ON cat.categoria_id = co.categoria_id
LEFT JOIN interacao i ON i.conteudo_id = co.conteudo_id
GROUP BY
    co.conteudo_id,
    co.titulo,
    cat.nome,
    co.tipo,
    co.nivel,
    co.carga_horaria_min,
    co.data_publicacao,
    co.autor;

-- ---------------------------------------------------------------------
-- 5. vw_kpi_recomendacoes_resumo
-- Métricas consolidadas sobre o motor de recomendação vetorial
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_kpi_recomendacoes_resumo AS
SELECT
    cat.nome                               AS categoria_nome,
    r.classificacao,
    COUNT(r.recomendacao_id)               AS qtd_recomendacoes,
    ROUND(AVG(r.pontuacao)::numeric, 2)    AS pontuacao_media,
    ROUND(MIN(r.pontuacao)::numeric, 2)    AS pontuacao_min,
    ROUND(MAX(r.pontuacao)::numeric, 2)    AS pontuacao_max,
    MAX(r.gerado_em)                       AS lote_gerado_em
FROM recomendacao r
JOIN conteudo co ON co.conteudo_id = r.conteudo_id
JOIN categoria cat ON cat.categoria_id = co.categoria_id
WHERE r.gerado_em = (SELECT MAX(gerado_em) FROM recomendacao)
GROUP BY cat.nome, r.classificacao;

-- ---------------------------------------------------------------------
-- 6. vw_kpi_engajamento_formato
-- Desempenho comparativo por Formato Didático (Curso, Vídeo, Artigo, Podcast)
-- Responde à Pergunta de Negócio 1 (retenção por formato de mídia)
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_kpi_engajamento_formato AS
SELECT
    co.tipo                                                              AS formato_conteudo,
    COUNT(DISTINCT co.conteudo_id)                                       AS total_conteudos_catalogo,
    COUNT(i.interacao_id)                                                AS total_interacoes,
    COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'visualização') AS visualizacoes,
    COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'início')       AS inicios,
    COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'conclusão' OR i.percentual_conclusao >= 100) AS conclusoes,
    ROUND(
        (COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao = 'conclusão' OR i.percentual_conclusao >= 100)::numeric /
         NULLIF(COUNT(i.interacao_id) FILTER (WHERE i.tipo_interacao IN ('início', 'visualização')), 0) * 100)::numeric, 2
    )                                                                    AS taxa_conclusao_pct,
    ROUND(AVG(i.avaliacao_atribuida)::numeric, 2)                        AS avaliacao_media,
    ROUND(AVG(i.tempo_consumido)::numeric, 1)                            AS tempo_medio_consumido_min,
    ROUND(AVG(co.carga_horaria_min)::numeric, 1)                         AS carga_horaria_media_estimada_min
FROM conteudo co
LEFT JOIN interacao i ON i.conteudo_id = co.conteudo_id
GROUP BY co.tipo
ORDER BY total_interacoes DESC;

-- ---------------------------------------------------------------------
-- 7. vw_kpi_conversao_recomendacoes
-- Avalia a eficácia do motor vetorial (RF10/RF11): se os itens sugeridos foram consumidos
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_kpi_conversao_recomendacoes AS
WITH lote_atual AS (
    SELECT *
    FROM recomendacao
    WHERE gerado_em = (SELECT MAX(gerado_em) FROM recomendacao)
),
interacoes_posteriores AS (
    SELECT DISTINCT i.usuario_id, i.conteudo_id
    FROM interacao i
    JOIN lote_atual l ON l.usuario_id = i.usuario_id AND l.conteudo_id = i.conteudo_id
    WHERE i.tipo_interacao IN ('visualização', 'início', 'conclusão', 'curtida')
)
SELECT
    COUNT(l.recomendacao_id)                                             AS total_recomendacoes_geradas,
    COUNT(p.conteudo_id)                                                 AS total_recomendacoes_consumidas,
    ROUND((COUNT(p.conteudo_id)::numeric / NULLIF(COUNT(l.recomendacao_id), 0) * 100)::numeric, 2) AS taxa_conversao_global_pct,
    COUNT(l.recomendacao_id) FILTER (WHERE l.classificacao = 'Positivo') AS total_positivas,
    COUNT(p.conteudo_id) FILTER (WHERE l.classificacao = 'Positivo')     AS positivas_consumidas,
    ROUND(
        (COUNT(p.conteudo_id) FILTER (WHERE l.classificacao = 'Positivo')::numeric /
         NULLIF(COUNT(l.recomendacao_id) FILTER (WHERE l.classificacao = 'Positivo'), 0) * 100)::numeric, 2
    )                                                                    AS taxa_conversao_positivos_pct,
    COUNT(l.recomendacao_id) FILTER (WHERE l.classificacao = 'Estável')  AS total_estaveis,
    COUNT(p.conteudo_id) FILTER (WHERE l.classificacao = 'Estável')   AS estaveis_consumidas,
    ROUND(
        (COUNT(p.conteudo_id) FILTER (WHERE l.classificacao = 'Estável')::numeric /
         NULLIF(COUNT(l.recomendacao_id) FILTER (WHERE l.classificacao = 'Estável'), 0) * 100)::numeric, 2
    )                                                                    AS taxa_conversao_estaveis_pct
FROM lote_atual l
LEFT JOIN interacoes_posteriores p ON p.usuario_id = l.usuario_id AND p.conteudo_id = l.conteudo_id;

COMMIT;
