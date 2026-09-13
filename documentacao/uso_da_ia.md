# Registro de Uso da Inteligência Artificial (Seção 10)

Documento elaborado conforme as diretrizes da **Seção 10 (Uso da Inteligência Artificial)** do edital do **Desafio Prático 1 — Fundamentos de Dados para IA (FIC_DEV)**.

---

## 1. Ferramentas de IA Utilizadas

- **Google DeepMind Antigravity / Gemini 3.8 Flash**: Assistente principal de desenvolvimento e pair programming utilizado para modelagem de banco de dados, resolução de conflitos de portas em containers Docker, criação das views SQL analíticas de KPIs, automação do Apache Superset e estruturação da documentação técnica.
- **Sentence-Transformers (`all-MiniLM-L6-v2`)**: Modelo pré-treinado de inteligência artificial / redes neurais para geração de representações vetoriais densas (embeddings de 384 dimensões) a partir de descrições e títulos de conteúdos educacionais.

---

## 2. Exemplos de Solicitações Realizadas

1. **Modelagem de Views e KPIs (RF12)**:
   - *Prompt*: "Projete as visões SQL analíticas no PostgreSQL para atender ao requisito RF12, calculando métricas operacionais (usuários, conteúdos, interações) e KPIs de tomada de decisão (Taxa de Conclusão, Avaliação Média CSAT e Taxa de Recomendações Positivas), prontas para o Apache Superset."
2. **Orquestração Docker e Conflito de Portas (RF13)**:
   - *Prompt*: "Adicione o serviço do Apache Superset ao `docker-compose.yml`, conectando-o à mesma rede interna do PostgreSQL com pgvector, e diagnostique o erro de bind na porta 5433."
3. **Registro de Execução Estruturado (RF14)**:
   - *Prompt*: "Implemente a medição precisa de tempo por etapa do pipeline (ingestão, validação, tratamento, persistência relacional e NoSQL, embeddings, busca semântica, recomendações e KPIs) gravando os resultados no JSON de resumo e com diagnóstico de causa provável em caso de falhas."

---

## 3. Trechos e Decisões Apoiadas pela IA

- **Cálculo da Taxa de Conclusão**: A IA sugeriu a fórmula ponderada $\frac{\text{conclusões}}{\text{inícios} + \text{visualizações}} \times 100$, garantindo tratamento seguro contra divisão por zero com a cláusula SQL `NULLIF(..., 0)`.
- **Visões SQL Especializadas**: Criação de `vw_kpi_metricas_gerais` (específica para Big Numbers), `vw_kpi_desempenho_categoria` (otimizada para gráficos de barras), `vw_kpi_evolucao_temporal` (série cronológica para gráficos de linha) e `vw_kpi_analise_conteudos` (base detalhada com dimensões para filtros interativos).
- **Tratamento de Tipos no PostgreSQL**: Utilização de `DecimalEncoder` customizado no Python para contornar a serialização nativa do tipo `Decimal` retornado pelo SQLAlchemy ao exportar para `kpis_resumo.json`.
- **Isolamento de Credenciais**: Separação de senhas no arquivo `.env` fora do Git, com `.env.example` disponibilizado como modelo reproduzível.

---

## 4. Erros ou Inadequações Encontrados nas Respostas

1. **Atributo `version` no Docker Compose**: Versões recentes da especificação Compose consideram o campo `version: '3.8'` obsoleto, emitindo advertências nos logs. A equipe ajustou o arquivo removendo a instrução redundante.
2. **Conflito de Porta Host (5433)**: Inicialmente, sugeriu-se apenas trocar a porta para 5434, mas a equipe identificou que um container legado (`licita-postgres`) estava ocupando a porta 5433 indevidamente, preferindo pausar o container inativo e manter o mapeamento canônico esperado pelos membros da equipe.
3. **Módulo `pgvector` e Interpretação do Python**: Ao invocar `python -m src.main` em um terminal novo, o Python global foi utilizado por padrão em vez do ambiente virtual `.venv`, gerando `ModuleNotFoundError: No module named 'pgvector'`. Foi necessário explicitar a invocação via executável do `.venv`.
4. **Tipo de Gráfico no Apache Superset (`echarts_timeseries_bar` vs `dist_bar`)**: Ao configurar inicialmente os gráficos de barras categóricos no Superset, utilizou-se o `viz_type="echarts_timeseries_bar"`. Como as visões agregadas de categoria e formato não possuem coluna temporal, o Superset acusou `Datetime column not provided as part table configuration and is required by this type of chart`. A equipe diagnosticou a causa e reconfigurou os gráficos para `dist_bar` (Distribution Bar Chart), que opera nativamente com dimensões categóricas sem exigir campos de data.

---

## 5. Alterações e Validações Feitas pela Equipe

- Todos os scripts SQL gerados foram revisados e testados diretamente no banco de dados com `sql/consultas.sql`.
- As métricas calculadas pelo módulo `src/kpis.py` foram auditadas manualmente frente aos dados brutos e tratados.
- Os parâmetros do motor de recomendação vetorial (pesos $I_{vis}$, $I_{cur}$ e filtro $I_{conc}$) foram calibrados para garantir que conteúdos concluídos tenham nota estritamente zerada conforme a regra de negócio do enunciado.
