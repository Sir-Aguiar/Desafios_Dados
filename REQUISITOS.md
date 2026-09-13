# Requisitos Funcionais

Documento de acompanhamento do **Desafio Prático 1 — Fundamentos de Dados para IA (FIC_DEV)**.

Legenda:

- `[x]` concluído
- `[ ]` não concluído ou incompleto

## Resumo

| Requisito | Título | Status |
|-----------|--------|--------|
| RF01 | Inicialização e configuração | Concluído |
| RF02 | Leitura das fontes de dados | Concluído |
| RF03 | Validação dos dados | Concluído |
| RF04 | Tratamento e padronização | Concluído |
| RF05 | Resumo da ingestão | Concluído |
| RF06 | Persistência no PostgreSQL | Concluído |
| RF07 | Persistência no MongoDB | Concluído |
| RF08 | Geração e armazenamento de embeddings | Concluído |
| RF09 | Busca por similaridade semântica | Concluído |
| RF10 | Geração de recomendações | Concluído |
| RF11 | Persistência das recomendações | Concluído |
| RF12 | Produção de métricas e KPIs | Concluído |
| RF13 | Dashboard no Apache Superset | Concluído |
| RF14 | Registro de execução | Concluído |

---

## RF01 — Inicialização e configuração

O sistema deverá:

- [x] ser executado pelo comando `python -m src.main`
- [x] utilizar um arquivo de configuração no formato JSON ou YAML
- [x] permitir configurar os caminhos dos arquivos de entrada
- [x] permitir configurar os parâmetros de conexão com o PostgreSQL, o MongoDB e o banco vetorial
- [x] separar senhas e informações sensíveis do código-fonte
- [x] apresentar mensagens que indiquem o início e o término do processamento

As senhas poderão ser armazenadas em variáveis de ambiente ou em um arquivo `.env` que não deverá ser incluído no controle de versão.

- [x] senhas em variáveis de ambiente ou arquivo `.env`
- [x] `.env` excluído do controle de versão (`.gitignore`)

**Status atual:** atendido. A execução ocorre via `python -m src.main`. Os caminhos das fontes, o modelo de embeddings e os parâmetros de busca/recomendação estão em `config.yaml`. Credenciais do PostgreSQL e do MongoDB vêm do `.env`. O banco vetorial usa pgvector no mesmo PostgreSQL.

---

## RF02 — Leitura das fontes de dados

O sistema deverá ler, no mínimo:

- [x] um arquivo CSV contendo o catálogo de conteúdos educacionais
- [x] um arquivo JSON contendo as interações dos usuários
- [x] um arquivo JSON contendo comentários ou avaliações

O sistema deverá informar o nome e a quantidade de registros encontrados em cada fonte.

- [x] informar o nome de cada fonte lida
- [x] informar a quantidade de registros encontrados em cada fonte

**Status atual:** atendido em `src/ingestao.py`.

---

## RF03 — Validação dos dados

Cada registro deverá ser classificado como:

- [x] válido
- [x] inválido
- [x] incompleto
- [x] duplicado

A aplicação deverá registrar o motivo da classificação dos registros que não forem considerados válidos.

- [x] registrar o motivo da classificação dos registros não válidos

As validações deverão contemplar, quando aplicável:

- [x] presença dos campos obrigatórios
- [x] validade dos identificadores
- [x] formato das datas
- [x] domínio dos valores categóricos
- [x] intervalo das avaliações
- [x] valores numéricos negativos ou incompatíveis
- [x] referências a usuários ou conteúdos inexistentes

**Status atual:** atendido em `src/validacao.py`. As quatro classificações existem e os motivos são registrados. O formato das datas é validado de forma estrita: `data_publicacao` e `data` em `YYYY-MM-DD`; `data_hora` em `YYYY-MM-DDTHH:MM:SS`.

---

## RF04 — Tratamento e padronização

O sistema deverá:

- [x] remover espaços desnecessários
- [x] uniformizar o uso de letras maiúsculas e minúsculas
- [x] padronizar categorias, tipos e níveis dos conteúdos
- [x] converter datas para um formato padronizado
- [x] converter campos numéricos
- [x] tratar ou registrar valores ausentes
- [x] identificar e eliminar duplicidades
- [x] preservar os arquivos originais
- [x] gravar os dados tratados em um diretório próprio

As decisões de tratamento deverão ser registradas na documentação da solução.

- [x] registrar as decisões de tratamento na documentação da solução

**Status atual:** atendido em `src/tratamento.py`. Os arquivos tratados vão para `dados/processados/`, sem alterar os originais em `dados/brutos/`. As decisões (espaços, caixa canônica, datas, numéricos, nulos, duplicatas e o que conta como corrigido) estão em `documentacao/decisoes_tratamento.md`.

---

## RF05 — Resumo da ingestão

Ao final da ingestão, o sistema deverá apresentar e armazenar um resumo contendo:

- [x] quantidade de registros lidos
- [x] quantidade de registros válidos
- [x] quantidade de registros inválidos
- [x] quantidade de registros incompletos
- [x] quantidade de registros duplicados
- [x] quantidade de registros corrigidos
- [x] quantidade de registros carregados em cada banco de dados
- [x] tempo total de processamento

O resumo deverá ser gravado em formato JSON.

- [x] gravar o resumo em formato JSON

**Status atual:** o JSON é gravado em `dados/processados/resumo_ingestao.json`. Os campos de **corrigidos** vêm do tratamento (RF04). `carregados_postgres` e `carregados_mongo` vêm das cargas do RF06 e do RF07.

---

## RF06 — Persistência no PostgreSQL

O sistema deverá armazenar os dados estruturados no PostgreSQL.

O banco deverá possuir, no mínimo, entidades equivalentes a:

- [x] usuário
- [x] conteúdo
- [x] categoria
- [x] interação
- [x] recomendação

A implementação deverá:

- [x] definir chaves primárias
- [x] definir chaves estrangeiras
- [x] impedir duplicidades de identificadores
- [x] manter a integridade dos relacionamentos
- [x] utilizar transações durante a carga
- [x] permitir consultar os registros armazenados

A equipe deverá entregar o script SQL utilizado para criar as tabelas.

- [x] entregar o script SQL de criação das tabelas

**Status atual:** atendido. O DDL está em `sql/criar_tabelas.sql` (PK, FK, UNIQUE, CHECK). Os models SQLAlchemy em `src/models.py` espelham o script. A carga em `src/persistencia.py` filtra os tratados, faz upsert transacional (`usuario`, `conteudo`, `interacao`) e consulta `COUNT` após o commit. A tabela `recomendacao` é criada no DDL e preenchida pelo RF11. Consultas manuais em `sql/consultas.sql`.

---

## RF07 — Persistência no MongoDB

O sistema deverá armazenar no MongoDB os comentários, avaliações ou outros dados semiestruturados.

- [x] armazenar comentários, avaliações ou dados semiestruturados no MongoDB

Cada documento deverá manter a identificação do usuário e do conteúdo ao qual está relacionado.

- [x] manter `usuario_id` e `conteudo_id` em cada documento

A aplicação deverá permitir, no mínimo:

- [x] inserir documentos
- [x] consultar comentários de determinado conteúdo
- [x] localizar documentos por tag
- [x] filtrar avaliações pela nota
- [x] agregar a quantidade de comentários ou avaliações por categoria

A equipe deverá justificar a escolha dos dados armazenados no MongoDB.

- [x] justificar a escolha dos dados armazenados no MongoDB

**Status atual:** atendido em `src/persistencia_mongo.py`. A coleção `comentarios` recebe os tratados, com `usuario_id`, `conteudo_id` e `categoria` desnormalizada. Índices e validador estão em `mongodb/indices.js`; consultas de verificação em `mongodb/consultas.js`. A justificativa está em `documentacao/escolha_mongodb.md`.

---

## RF08 — Geração e armazenamento de embeddings

O sistema deverá:

- [x] utilizar o título e a descrição dos conteúdos para gerar uma representação textual
- [x] gerar um embedding para cada conteúdo válido
- [x] associar o embedding ao identificador do conteúdo
- [x] armazenar os vetores em PostgreSQL com pgvector
- [x] evitar a geração duplicada de embeddings para o mesmo conteúdo
- [x] registrar o modelo utilizado para gerar os vetores

A equipe deverá documentar o modelo de embeddings e a estratégia de preparação dos textos.

- [x] documentar o modelo de embeddings
- [x] documentar a estratégia de preparação dos textos

**Status atual:** atendido em `src/embeddings.py`. O texto é a concatenação de título e descrição. Só entram conteúdos já persistidos em `conteudo` (RF06). Cada vetor é gravado em `embedding_conteudo` com `conteudo_id` (PK/FK), `modelo` e `texto_origem`. Recargas reaproveitam o vetor se modelo e texto não mudaram. O DDL está em `sql/criar_embeddings.sql` (extensão `vector` + índice HNSW). Decisões em `documentacao/modelo_embeddings.md`.

---

## RF09 — Busca por similaridade semântica

O sistema deverá receber uma consulta em linguagem natural e retornar os conteúdos semanticamente mais semelhantes.

Exemplo de consulta:

> Quero aprender os fundamentos de banco de dados para inteligência artificial.

Para cada resultado, o sistema deverá apresentar:

- [x] posição no resultado
- [x] identificador do conteúdo
- [x] título
- [x] categoria
- [x] tipo
- [x] valor de similaridade ou distância

A quantidade de resultados retornados deverá ser configurável.

- [x] quantidade de resultados configurável
- [x] receber consulta em linguagem natural
- [x] retornar os conteúdos semanticamente mais semelhantes

A equipe deverá demonstrar pelo menos três consultas semânticas diferentes.

- [x] demonstrar pelo menos três consultas semânticas diferentes

**Status atual:** atendido em `src/busca_semantica.py`. A consulta é embeddada com o mesmo modelo do RF08 e ranqueada no pgvector (`<=>`). Cada item traz posição, `conteudo_id`, título, categoria, tipo, similaridade e distância. O `top_k` vem de `busca_semantica.top_k_padrao`. As três frases de demonstração estão em `config.yaml`; o pipeline e `python -m src.busca_semantica` as executam e gravam `dados/processados/busca_semantica.json`. Detalhes em `documentacao/busca_semantica.md`.

---

## RF10 — Geração de recomendações

O sistema deverá gerar recomendações de conteúdos para um usuário.

A recomendação deverá considerar, no mínimo:

- [x] conteúdos visualizados
- [x] conteúdos curtidos ou bem avaliados
- [x] remoção dos conteúdos já concluídos pelo usuário

O sistema deverá apresentar, para cada recomendação:

- [x] usuário
- [x] conteúdo recomendado
- [x] pontuação
- [x] posição
- [x] data de geração

A equipe deverá utilizar a seguinte fórmula.

A formulação baseia-se exclusivamente em três variáveis calculadas entre o usuário e o conteúdo candidato:

- **Índice de Visualizações (Ivis):** mede o nível de afinidade temática com os conteúdos que o usuário consome e visualiza com frequência (calculado por similaridade vetorial via pgvector ou pela proporção de tempo consumido na mesma categoria), assumindo valores contínuos na faixa de 0.0 a 1.0.
- **Índice de Curtidas e Avaliações (Icur):** representa o interesse explícito e a aprovação do usuário em materiais relacionados (baseado no histórico de curtidas ou avaliações positivas com nota igual ou superior a 4), variando igualmente entre 0.0 e 1.0.
- **Índice de Remoção de Concluídos (Iconc):** funciona como um filtro binário eliminatório obrigatório pelo requisito de negócio. Assume valor 0 caso o usuário já tenha concluído o conteúdo (anulando qualquer pontuação), e valor 1 caso o material ainda não tenha sido concluído, mantendo-o apto para recomendação.

```
Pontuação = ((Ivis + Icur) / 2) * 100 * Iconc
```

Regra básica: a pontuação é a média simples entre o índice de visualização e o de curtidas, multiplicada pelo filtro de conclusão. Varia de 0 a 100.

- [x] implementar a fórmula `Pontuação = ((Ivis + Icur) / 2) * 100 * Iconc`

### Regra de classificação (tipo de recomendação)

Com base na pontuação calculada, o sistema atribui o status da recomendação:

- **Positivo** (pontuação >= 70): forte afinidade. O usuário visualiza ativamente conteúdos desse tema e costuma curtir/avaliar positivamente.
- **Estável** (40 > pontuação < 70): afinidade moderada. O usuário demonstrou interesse parcial (ou apenas visualizou pouco, ou ainda não avaliou conteúdos semelhantes).
- **Negativo** (pontuação <= 40 ou Iconc = 0): baixo interesse ou conteúdo já concluído (descartado da lista de sugestões).

- [x] classificar como Positivo (pontuação >= 70)
- [x] classificar como Estável (faixa intermediária de pontuação)
- [x] classificar como Negativo (pontuação <= 40 ou Iconc = 0)

**Status atual:** atendido em `src/recomendacao.py`. Ivis é a similaridade de cosseno no pgvector com o centroide dos conteúdos consumidos (fallback: tempo na categoria). Icur usa o mesmo critério sobre curtidas e avaliações `>= 4`. Iconc zera conteúdos concluídos. Negativo sai da lista de sugestões; Positivo e Estável entram ranqueados até `top_n_por_usuario`. Cada item traz usuário, conteúdo, pontuação, posição, classificação, índices e data de geração. O pipeline e `python -m src.recomendacao` gravam `dados/processados/recomendacoes.json` e persistem o lote no PostgreSQL (RF11). Detalhes em `documentacao/recomendacao.md`.

---

## RF11 — Persistência das recomendações

As recomendações geradas deverão ser armazenadas no PostgreSQL.

Cada recomendação deverá possuir, no mínimo:

- [x] identificador do usuário
- [x] identificador do conteúdo
- [x] pontuação final
- [x] posição no resultado
- [x] data e hora da geração

**Status atual:** atendido em `GeradorRecomendacoes.persistir` (`src/recomendacao.py`). O lote do RF10 é gravado na tabela `recomendacao` (DDL do RF06) em transação, com upsert na unicidade `(usuario_id, conteudo_id, gerado_em)`. Depois do commit o pipeline consulta `COUNT` e uma amostra. Consultas manuais em `sql/consultas.sql` (bloco RF11). Detalhes em `documentacao/recomendacao.md`.

---

## RF12 — Produção de métricas e KPIs

O sistema deverá calcular, no mínimo:

- [x] duas métricas operacionais
- [x] dois KPIs orientados à tomada de decisão

Entre os indicadores possíveis estão:

- [x] quantidade de usuários
- [x] quantidade de conteúdos
- [x] visualizações por período
- [x] avaliação média
- [x] taxa de conclusão
- [x] engajamento
- [x] retenção
- [x] conversão de recomendações
- [x] tempo médio consumido
- [x] quantidade de recomendações geradas

Para cada KPI, a equipe deverá informar:

- [x] nome
- [x] objetivo
- [x] fórmula
- [x] fonte dos dados
- [x] periodicidade
- [x] interpretação

Os resultados deverão ser disponibilizados em tabelas ou visões no PostgreSQL para utilização pelo Apache Superset.

- [x] disponibilizar resultados em tabelas ou visões no PostgreSQL

**Status atual:** atendido. Foram criadas cinco visões analíticas no PostgreSQL (`sql/criar_views_kpi.sql`), incluindo `vw_kpi_metricas_gerais`, `vw_kpi_desempenho_categoria`, `vw_kpi_evolucao_temporal`, `vw_kpi_analise_conteudos` e `vw_kpi_recomendacoes_resumo`. O módulo `src/kpis.py` aplica as views e exporta o consolidado para `dados/processados/kpis_resumo.json`. A documentação completa de cada indicador, fórmula e periodicidade está registrada em `documentacao/kpis.md`.

---

## RF13 — Dashboard no Apache Superset

A equipe deverá construir um dashboard no Apache Superset utilizando os dados consolidados no PostgreSQL.

O dashboard deverá conter, no mínimo:

- [x] três cartões de indicadores
- [x] um gráfico de barras
- [x] um gráfico de linhas
- [x] dois filtros interativos

O dashboard deverá permitir responder a pelo menos duas perguntas de negócio definidas pela equipe.

- [x] definir pelo menos duas perguntas de negócio
- [x] permitir responder às perguntas de negócio pelo dashboard

A escolha de cada gráfico deverá ser justificada considerando a natureza dos dados e a informação que se deseja comunicar.

- [x] justificar a escolha de cada gráfico

**Status atual:** atendido. O Apache Superset foi orquestrado no `docker-compose.yml` (porta 8088), com provisionamento automatizado via `src/superset_init.py` e `src/superset_dashboard.py`. O painel conta com três cartões Big Number (Total de Usuários, Avaliação Média CSAT e Taxa de Conclusão Global), gráfico de barras por categoria, gráfico de linhas temporal e dois filtros interativos (Categoria e Nível). O arquivo exportado do dashboard foi gravado em `dashboard/dashboard_plataforma_educacional.zip` e a documentação completa está em `documentacao/kpis.md` e `dashboard/README.md`.

---

## RF14 — Registro de execução

Durante a execução, o sistema deverá registrar:

- [x] início e término do processamento
- [x] arquivos processados
- [x] quantidade de registros lidos
- [x] registros rejeitados
- [x] falhas de conexão
- [x] falhas na geração de embeddings
- [x] falhas de persistência
- [x] tempo de execução das principais etapas

O registro deverá permitir identificar a origem e a causa provável de cada problema.

- [x] identificar origem e causa provável nos logs já existentes (leitura, validação, persistência e conexões)

**Status atual:** atendido. Logging abrangente em console e arquivo (`logs/pipeline.log`), com cronometragem individual de cada etapa (ingestão, validação, tratamento, persistência Postgres, persistência Mongo, embeddings, busca semântica, recomendações e KPIs). Os tempos por etapa e tempo total são persistidos no JSON `dados/processados/resumo_ingestao.json`. Falhas de conexão e banco contam com diagnóstico de causa provável.

