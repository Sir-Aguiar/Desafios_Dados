-- RF06 — consultas de verificacao dos registros persistidos
-- Executar apos a carga (python -m src.main) no banco plataforma_educacional.

-- Contagem por tabela
SELECT 'usuario' AS entidade, COUNT(*) AS total FROM usuario
UNION ALL
SELECT 'categoria', COUNT(*) FROM categoria
UNION ALL
SELECT 'conteudo', COUNT(*) FROM conteudo
UNION ALL
SELECT 'interacao', COUNT(*) FROM interacao
UNION ALL
SELECT 'recomendacao', COUNT(*) FROM recomendacao
ORDER BY entidade;

-- Conteudos por categoria
SELECT c.nome AS categoria, COUNT(*) AS qtd_conteudos
FROM conteudo co
JOIN categoria c ON c.categoria_id = co.categoria_id
GROUP BY c.nome
ORDER BY qtd_conteudos DESC, c.nome;

-- Interacoes por tipo
SELECT tipo_interacao, COUNT(*) AS qtd
FROM interacao
GROUP BY tipo_interacao
ORDER BY qtd DESC, tipo_interacao;

-- Orfaos (nao deve retornar linha se as FKs estiverem inteiras)
SELECT i.interacao_id
FROM interacao i
LEFT JOIN usuario u ON u.usuario_id = i.usuario_id
LEFT JOIN conteudo c ON c.conteudo_id = i.conteudo_id
WHERE u.usuario_id IS NULL OR c.conteudo_id IS NULL;

SELECT co.conteudo_id
FROM conteudo co
LEFT JOIN categoria c ON c.categoria_id = co.categoria_id
WHERE c.categoria_id IS NULL;

-- RF08 — embeddings associados ao conteudo
SELECT
    COUNT(*) AS total_embeddings,
    COUNT(DISTINCT modelo) AS modelos,
    COUNT(DISTINCT conteudo_id) AS conteudos
FROM embedding_conteudo;

SELECT modelo, COUNT(*) AS qtd
FROM embedding_conteudo
GROUP BY modelo
ORDER BY qtd DESC, modelo;

SELECT
    e.conteudo_id,
    c.titulo,
    e.modelo,
    vector_dims(e.vetor) AS dimensao,
    left(e.texto_origem, 80) AS texto_origem
FROM embedding_conteudo e
JOIN conteudo c ON c.conteudo_id = e.conteudo_id
ORDER BY e.conteudo_id
LIMIT 5;

-- Conteudos persistidos sem embedding (nao deve retornar linha apos o RF08)
SELECT co.conteudo_id, co.titulo
FROM conteudo co
LEFT JOIN embedding_conteudo e ON e.conteudo_id = co.conteudo_id
WHERE e.conteudo_id IS NULL
ORDER BY co.conteudo_id;

-- RF09 — vizinhos semanticos de um conteudo ja embeddado (sem gerar vetor da consulta).
-- A busca em linguagem natural roda em Python (src/busca_semantica.py): o embedding
-- da frase usa o mesmo modelo do RF08 e a distancia de cosseno (operador <=>).
-- Similaridade = 1 - distancia. Troque o conteudo_id de referencia se quiser outro tema.
SELECT
    ROW_NUMBER() OVER (ORDER BY e.vetor <=> ref.vetor) AS posicao,
    c.conteudo_id,
    c.titulo,
    cat.nome AS categoria,
    c.tipo,
    ROUND((1 - (e.vetor <=> ref.vetor))::numeric, 4) AS similaridade,
    ROUND((e.vetor <=> ref.vetor)::numeric, 4) AS distancia
FROM embedding_conteudo e
JOIN conteudo c ON c.conteudo_id = e.conteudo_id
JOIN categoria cat ON cat.categoria_id = c.categoria_id
CROSS JOIN (
    SELECT vetor
    FROM embedding_conteudo
    WHERE conteudo_id = 92
) ref
ORDER BY e.vetor <=> ref.vetor
LIMIT 5;
