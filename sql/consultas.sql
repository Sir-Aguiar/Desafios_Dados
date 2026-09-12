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
