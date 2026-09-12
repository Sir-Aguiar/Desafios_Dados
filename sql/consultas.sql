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
