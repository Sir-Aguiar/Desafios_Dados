# Escolha dos dados armazenados no MongoDB (RF07)

A persistência NoSQL fica em `src/persistencia_mongo.py`. O artefato reproduzível dos índices está em `mongodb/indices.js`; as consultas mínimas do requisito estão em `mongodb/consultas.js`.

## 1. O que vai para o MongoDB

Só os **comentários e avaliações** tratados (`dados/processados/comentarios_tratados.json`).

Cada documento guarda:

- `usuario_id` e `conteudo_id` (obrigatórios pelo RF07)
- `avaliacao` (nota 1–5)
- `comentario` (texto livre)
- `tags` (lista de strings)
- `data` (BSON Date)
- `categoria` (copiada do catálogo na carga)

## 2. Por que esses dados, e não os outros

O MongoDB entra no desafio como destino de **dados semiestruturados**. Comentários se encaixam nisso:

- o campo `tags` é um array de tamanho variável — modelo natural em documento, artificial em tabela relacional (exigiria tabela associativa);
- `comentario` é texto livre, sem schema rígido de colunas;
- avaliação e comentário convivem no mesmo objeto, como na fonte JSON.

Catálogo, usuários e interações **não** vão para o MongoDB. São tabulares, com chaves e restrições de domínio, e já estão no PostgreSQL (RF06). Duplicá-los no NoSQL quebraria a divisão pedida pelo enunciado (estruturado vs semiestruturado) e geraria duas fontes da verdade.

## 3. Por que desnormalizar `categoria`

O RF07 pede agregar a quantidade de comentários por categoria. Na origem, o comentário **não tem** categoria: ela pertence ao catálogo.

No MongoDB não há JOIN com o PostgreSQL. A carga copia `categoria` do `catalogo_tratado` para cada documento. Com isso o `$group` roda só no MongoDB, usando o índice `ix_comentario_categoria`.

A categoria é um rótulo estável (oito valores canônicos do RF04). O risco de divergência é baixo neste conjunto fictício; se o catálogo mudar, a recarga faz upsert e atualiza o campo.

## 4. Recarga e integridade

- Chave de negócio igual ao tratamento: `(usuario_id, conteudo_id, data)`, com índice único.
- Recarga por upsert (`ReplaceOne`), sem apagar a coleção — o mesmo critério do RF06.
- Só entram documentos com identificadores presentes, nota entre 1 e 5, data válida e `conteudo_id` existente no catálogo com categoria canônica. O JSON tratado continua auditável; o filtro é da persistência.
- O validador `$jsonSchema` da coleção espelha os CHECK do SQL: tipos, faixa da nota e campos obrigatórios.

## 5. Operações mínimas do RF07

| Operação | Como |
|----------|------|
| Inserir | `PersistenciaMongo.carregar` (upsert em lote) |
| Comentários de um conteúdo | `comentarios_do_conteudo(conteudo_id)` / `find({conteudo_id})` |
| Localizar por tag | `localizar_por_tag(tag)` / `find({tags: "nlp"})` |
| Filtrar pela nota | `filtrar_por_nota(nota)` / `find({avaliacao: 5})` |
| Agregar por categoria | `agregar_por_categoria()` / `$group` em `categoria` |
