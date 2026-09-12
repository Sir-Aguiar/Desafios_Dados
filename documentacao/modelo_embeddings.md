# Modelo de embeddings e preparação dos textos (RF08)

A geração e o armazenamento dos vetores ficam em `src/embeddings.py`. O artefato reproduzível do schema vetorial está em `sql/criar_embeddings.sql`. Consultas de verificação: `sql/consultas.sql` (bloco RF08).

## 1. Modelo

O padrão da solução é o modelo do Sentence Transformers declarado em `config.yaml`:

| Parâmetro | Valor padrão |
|-----------|----------------|
| Identificador | `sentence-transformers/all-MiniLM-L6-v2` |
| Dimensão | 384 |
| Cache local | `.cache/embeddings/` (fora do Git) |

Escolhemos esse modelo porque:

- é pequeno (~90 MB) e roda em CPU em tempo aceitável para ~1000 conteúdos;
- produz vetores densos adequados a similaridade de cosseno (RF09);
- o suporte a português é suficiente para títulos e descrições curtas deste catálogo.

Modelos maiores (por exemplo `all-mpnet-base-v2`, 768 dimensões) tendem a embeddings um pouco melhores, mas pesam mais no download e no tempo de encode. Para trocar, basta definir `EMBEDDING_MODEL` e `EMBEDDING_DIMENSIONS` no `.env`. O pipeline registra o nome efetivo do modelo em cada linha de `embedding_conteudo.modelo` e no log.

Os vetores são **normalizados** (`normalize_embeddings=True`). Com isso a similaridade de cosseno coincide com o produto interno, e a busca do RF09 pode usar o operador `<=>` do pgvector.

## 2. Estratégia de preparação dos textos

O RF08 pede uma representação textual a partir do **título** e da **descrição**. A função `representar_texto` concatena os dois campos nesta ordem:

```
{titulo}

{descricao}
```

Regras:

| Situação | Decisão |
|----------|---------|
| Título e descrição presentes | título, linha em branco, descrição |
| Só o título (descrição nula ou vazia) | só o título |
| Título e descrição vazios | o conteúdo é ignorado e o fato vai para o log |

Não incluímos categoria, tipo, nível nem autor no texto. Esses campos já estão no PostgreSQL estruturado; misturá-los no embedding enviesaria a similaridade semântica para o rótulo da categoria em vez do assunto descrito.

Não repetimos o título nem prefixamos rótulos (`"Título:"`, `"Descrição:"`). Os textos do catálogo já são frases em português; o modelo trata a concatenação como um único documento curto.

Os conteúdos embeddados são os **válidos já persistidos** na tabela `conteudo` (RF06). Assim o vetor só existe para identificadores que passaram na validação/tratamento e que têm chave estrangeira íntegra.

## 3. Associação ao identificador e armazenamento

Cada vetor é gravado em `embedding_conteudo` com `conteudo_id` como chave primária (FK para `conteudo`). Um conteúdo tem no máximo um embedding.

| Coluna | Papel |
|--------|--------|
| `conteudo_id` | identifica o conteúdo (associação exigida pelo RF08) |
| `texto_origem` | texto exatamente embeddado (auditoria e invalidação) |
| `modelo` | identificador do Sentence Transformer usado |
| `vetor` | `vector(N)` do pgvector, N = dimensão configurada |
| `gerado_em` | data/hora da geração ou da última atualização |

O índice HNSW em `vetor` usa `vector_cosine_ops`, preparado para a busca do RF09.

## 4. Como evitamos gerar de novo o mesmo embedding

Na recarga, o pipeline compara `(modelo, texto_origem)` já gravado com o texto atual do conteúdo:

- iguais → reaproveita o vetor, sem chamar o modelo;
- modelo diferente, texto diferente ou conteúdo novo → gera e faz upsert.

Se a dimensão configurada mudar, a tabela é recriada (um `vector(384)` não aceita vetores de 768) e os embeddings são gerados outra vez.

## 5. Falhas

Falhas ao conectar no PostgreSQL, ao aplicar o DDL, ao baixar/carregar o modelo ou ao executar o `encode` são registradas no log com origem e exceção. O pipeline interrompe a etapa: não grava vetores parciais de um lote que falhou.
