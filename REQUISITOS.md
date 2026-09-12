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
| RF04 | Tratamento e padronização | Parcial |
| RF05 | Resumo da ingestão | Parcial |
| RF06 | Persistência no PostgreSQL | Não iniciado |
| RF07 | Persistência no MongoDB | Não iniciado |
| RF08 | Geração e armazenamento de embeddings | Não iniciado |
| RF09 | Busca por similaridade semântica | Não iniciado |
| RF10 | Geração de recomendações | Não iniciado |
| RF11 | Persistência das recomendações | Não iniciado |
| RF12 | Produção de métricas e KPIs | Não iniciado |
| RF13 | Dashboard no Apache Superset | Não iniciado |
| RF14 | Registro de execução | Parcial |

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

- [ ] registrar as decisões de tratamento na documentação da solução

**Status atual:** o tratamento está implementado em `src/tratamento.py` e os arquivos tratados vão para `dados/processados/`, sem alterar os originais em `dados/brutos/`. Falta um documento dedicado com as decisões de tratamento (o `README.md` cita algumas, mas não cobre o requisito de documentação).

---

## RF05 — Resumo da ingestão

Ao final da ingestão, o sistema deverá apresentar e armazenar um resumo contendo:

- [x] quantidade de registros lidos
- [x] quantidade de registros válidos
- [x] quantidade de registros inválidos
- [x] quantidade de registros incompletos
- [x] quantidade de registros duplicados
- [ ] quantidade de registros corrigidos
- [ ] quantidade de registros carregados em cada banco de dados
- [x] tempo total de processamento

O resumo deverá ser gravado em formato JSON.

- [x] gravar o resumo em formato JSON

**Status atual:** o JSON é gravado em `dados/processados/resumo_ingestao.json`. Os campos de **corrigidos** estão com valor placeholder (`0`). Os campos de **carregados** no PostgreSQL e no MongoDB também ficam em `0` porque a persistência ainda não foi implementada.

---

## RF06 — Persistência no PostgreSQL

O sistema deverá armazenar os dados estruturados no PostgreSQL.

O banco deverá possuir, no mínimo, entidades equivalentes a:

- [ ] usuário
- [ ] conteúdo
- [ ] categoria
- [ ] interação
- [ ] recomendação

A implementação deverá:

- [ ] definir chaves primárias
- [ ] definir chaves estrangeiras
- [ ] impedir duplicidades de identificadores
- [ ] manter a integridade dos relacionamentos
- [ ] utilizar transações durante a carga
- [ ] permitir consultar os registros armazenados

A equipe deverá entregar o script SQL utilizado para criar as tabelas.

- [ ] entregar o script SQL de criação das tabelas

**Status atual:** não iniciado. O `docker-compose.yml` sobe o PostgreSQL com pgvector, mas não há carga, modelo relacional nem script SQL.

---

## RF07 — Persistência no MongoDB

O sistema deverá armazenar no MongoDB os comentários, avaliações ou outros dados semiestruturados.

- [ ] armazenar comentários, avaliações ou dados semiestruturados no MongoDB

Cada documento deverá manter a identificação do usuário e do conteúdo ao qual está relacionado.

- [ ] manter `usuario_id` e `conteudo_id` em cada documento

A aplicação deverá permitir, no mínimo:

- [ ] inserir documentos
- [ ] consultar comentários de determinado conteúdo
- [ ] localizar documentos por tag
- [ ] filtrar avaliações pela nota
- [ ] agregar a quantidade de comentários ou avaliações por categoria

A equipe deverá justificar a escolha dos dados armazenados no MongoDB.

- [ ] justificar a escolha dos dados armazenados no MongoDB

**Status atual:** não iniciado. O MongoDB sobe via Docker, mas não há persistência nem consultas.

---

## RF08 — Geração e armazenamento de embeddings

O sistema deverá:

- [ ] utilizar o título e a descrição dos conteúdos para gerar uma representação textual
- [ ] gerar um embedding para cada conteúdo válido
- [ ] associar o embedding ao identificador do conteúdo
- [ ] armazenar os vetores em PostgreSQL com pgvector
- [ ] evitar a geração duplicada de embeddings para o mesmo conteúdo
- [ ] registrar o modelo utilizado para gerar os vetores

A equipe deverá documentar o modelo de embeddings e a estratégia de preparação dos textos.

- [ ] documentar o modelo de embeddings
- [ ] documentar a estratégia de preparação dos textos

**Status atual:** não iniciado. O modelo `sentence-transformers/all-MiniLM-L6-v2` já está declarado em `config.yaml` e citado no `README.md`, mas não há geração nem armazenamento dos vetores. O módulo `src/busca_semantica.py` está vazio.

---

## RF09 — Busca por similaridade semântica

O sistema deverá receber uma consulta em linguagem natural e retornar os conteúdos semanticamente mais semelhantes.

Exemplo de consulta:

> Quero aprender os fundamentos de banco de dados para inteligência artificial.

Para cada resultado, o sistema deverá apresentar:

- [ ] posição no resultado
- [ ] identificador do conteúdo
- [ ] título
- [ ] categoria
- [ ] tipo
- [ ] valor de similaridade ou distância

A quantidade de resultados retornados deverá ser configurável.

- [ ] quantidade de resultados configurável
- [ ] receber consulta em linguagem natural
- [ ] retornar os conteúdos semanticamente mais semelhantes

A equipe deverá demonstrar pelo menos três consultas semânticas diferentes.

- [ ] demonstrar pelo menos três consultas semânticas diferentes

**Status atual:** não iniciado. O parâmetro `busca_semantica.top_k_padrao` já existe em `config.yaml`.

---

## RF10 — Geração de recomendações

O sistema deverá gerar recomendações de conteúdos para um usuário.

A recomendação deverá considerar, no mínimo:

- [ ] conteúdos visualizados
- [ ] conteúdos curtidos ou bem avaliados
- [ ] remoção dos conteúdos já concluídos pelo usuário

O sistema deverá apresentar, para cada recomendação:

- [ ] usuário
- [ ] conteúdo recomendado
- [ ] pontuação
- [ ] posição
- [ ] data de geração

A equipe deverá utilizar a seguinte fórmula.

A formulação baseia-se exclusivamente em três variáveis calculadas entre o usuário e o conteúdo candidato:

- **Índice de Visualizações (Ivis):** mede o nível de afinidade temática com os conteúdos que o usuário consome e visualiza com frequência (calculado por similaridade vetorial via pgvector ou pela proporção de tempo consumido na mesma categoria), assumindo valores contínuos na faixa de 0.0 a 1.0.
- **Índice de Curtidas e Avaliações (Icur):** representa o interesse explícito e a aprovação do usuário em materiais relacionados (baseado no histórico de curtidas ou avaliações positivas com nota igual ou superior a 4), variando igualmente entre 0.0 e 1.0.
- **Índice de Remoção de Concluídos (Iconc):** funciona como um filtro binário eliminatório obrigatório pelo requisito de negócio. Assume valor 0 caso o usuário já tenha concluído o conteúdo (anulando qualquer pontuação), e valor 1 caso o material ainda não tenha sido concluído, mantendo-o apto para recomendação.

```
Pontuação = ((Ivis + Icur) / 2) * 100 * Iconc
```

Regra básica: a pontuação é a média simples entre o índice de visualização e o de curtidas, multiplicada pelo filtro de conclusão. Varia de 0 a 100.

- [ ] implementar a fórmula `Pontuação = ((Ivis + Icur) / 2) * 100 * Iconc`

### Regra de classificação (tipo de recomendação)

Com base na pontuação calculada, o sistema atribui o status da recomendação:

- **Positivo** (pontuação >= 70): forte afinidade. O usuário visualiza ativamente conteúdos desse tema e costuma curtir/avaliar positivamente.
- **Estável** (40 > pontuação < 70): afinidade moderada. O usuário demonstrou interesse parcial (ou apenas visualizou pouco, ou ainda não avaliou conteúdos semelhantes).
- **Negativo** (pontuação <= 40 ou Iconc = 0): baixo interesse ou conteúdo já concluído (descartado da lista de sugestões).

- [ ] classificar como Positivo (pontuação >= 70)
- [ ] classificar como Estável (faixa intermediária de pontuação)
- [ ] classificar como Negativo (pontuação <= 40 ou Iconc = 0)

**Status atual:** não iniciado. Parâmetros de recomendação já existem em `config.yaml` (`top_n_por_usuario`, `nota_minima_avaliacao_positiva`, pesos).

---

## RF11 — Persistência das recomendações

As recomendações geradas deverão ser armazenadas no PostgreSQL.

Cada recomendação deverá possuir, no mínimo:

- [ ] identificador do usuário
- [ ] identificador do conteúdo
- [ ] pontuação final
- [ ] posição no resultado
- [ ] data e hora da geração

**Status atual:** não iniciado. Depende do RF06 (tabela de recomendação) e do RF10 (geração).

---

## RF12 — Produção de métricas e KPIs

O sistema deverá calcular, no mínimo:

- [ ] duas métricas operacionais
- [ ] dois KPIs orientados à tomada de decisão

Entre os indicadores possíveis estão:

- quantidade de usuários
- quantidade de conteúdos
- visualizações por período
- avaliação média
- taxa de conclusão
- engajamento
- retenção
- conversão de recomendações
- tempo médio consumido
- quantidade de recomendações geradas

Para cada KPI, a equipe deverá informar:

- [ ] nome
- [ ] objetivo
- [ ] fórmula
- [ ] fonte dos dados
- [ ] periodicidade
- [ ] interpretação

Os resultados deverão ser disponibilizados em tabelas ou visões no PostgreSQL para utilização pelo Apache Superset.

- [ ] disponibilizar resultados em tabelas ou visões no PostgreSQL

**Status atual:** não iniciado. Não há `documentacao/kpis.md` nem views SQL.

---

## RF13 — Dashboard no Apache Superset

A equipe deverá construir um dashboard no Apache Superset utilizando os dados consolidados no PostgreSQL.

O dashboard deverá conter, no mínimo:

- [ ] três cartões de indicadores
- [ ] um gráfico de barras
- [ ] um gráfico de linhas
- [ ] dois filtros interativos

O dashboard deverá permitir responder a pelo menos duas perguntas de negócio definidas pela equipe.

- [ ] definir pelo menos duas perguntas de negócio
- [ ] permitir responder às perguntas de negócio pelo dashboard

A escolha de cada gráfico deverá ser justificada considerando a natureza dos dados e a informação que se deseja comunicar.

- [ ] justificar a escolha de cada gráfico

**Status atual:** não iniciado. Não há dashboard, prints nem evidências em `dashboard/`.

---

## RF14 — Registro de execução

Durante a execução, o sistema deverá registrar:

- [x] início e término do processamento
- [x] arquivos processados
- [x] quantidade de registros lidos
- [x] registros rejeitados
- [ ] falhas de conexão
- [ ] falhas na geração de embeddings
- [ ] falhas de persistência
- [ ] tempo de execução das principais etapas

O registro deverá permitir identificar a origem e a causa provável de cada problema.

- [x] identificar origem e causa provável nos logs já existentes (leitura e validação)

**Status atual:** parcialmente atendido. Há logging em arquivo (`logs/pipeline.log`) e no console, com início/fim, arquivos lidos, contagens e motivos de rejeição. Ainda faltam registros específicos de falha de conexão, embeddings e persistência (módulos ainda não implementados), além do tempo por etapa (hoje só o tempo total do pipeline).
