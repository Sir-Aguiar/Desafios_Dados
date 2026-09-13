# Documentação de Métricas e KPIs (RF12) e Dashboard Superset (RF13)

Este documento detalha o conjunto de métricas operacionais e indicadores-chave de desempenho (KPIs) da Plataforma Educacional, bem como a arquitetura das visões no PostgreSQL e a concepção do dashboard no Apache Superset.

---

## 1. Métricas Operacionais

As métricas operacionais fornecem um panorama quantitativo imediato sobre o volume de dados e o funcionamento da plataforma.

### Métrica Operacional 1: Volume Geral da Plataforma
- **Nome**: Total de Usuários, Conteúdos e Interações Cadastradas
- **Objetivo**: Monitorar o dimensionamento da plataforma, o catálogo ofertado e a atividade geral dos discentes.
- **Fórmula**:
  - `Total Usuários = COUNT(DISTINCT usuario_id)` em `usuario`
  - `Total Conteúdos = COUNT(DISTINCT conteudo_id)` em `conteudo`
  - `Total Interações = COUNT(interacao_id)` em `interacao`
- **Fonte dos Dados**: Tabelas `usuario`, `conteudo`, `interacao` no PostgreSQL.
- **Periodicidade**: Contínua / Por lote de processamento.
- **Interpretação**: Indica a escala operacional do sistema. O crescimento sustentado do número de interações em relação a conteúdos indica alta tração dos materiais disponibilizados.

### Métrica Operacional 2: Volume e Tempo Médio de Consumo
- **Nome**: Tempo Médio Consumido e Total de Minutos Navegados
- **Objetivo**: Acompanhar o tempo de permanência e engajamento prático dos usuários com os materiais didáticos.
- **Fórmula**:
  - `Tempo Médio = AVG(tempo_consumido)` (em minutos)
  - `Tempo Total = SUM(tempo_consumido)`
- **Fonte dos Dados**: Tabela `interacao` no PostgreSQL.
- **Periodicidade**: Diária.
- **Interpretação**: Materiais de maior duração (ex.: cursos) devem refletir médias de tempo maiores. Valores muito baixos em relação à carga horária estimada apontam potencial abandono precoce.

---

## 2. KPIs Estratégicos (Orientados à Tomada de Decisão)

### KPI 1: Taxa de Conclusão de Conteúdos (Completion Rate)
- **Nome**: Taxa de Conclusão Global e por Categoria
- **Objetivo**: Avaliar a capacidade de retenção dos conteúdos, medindo a proporção de alunos que iniciam ou visualizam um material e o concluem com sucesso.
- **Fórmula**:
  $$\text{Taxa de Conclusão (\%)} = \left( \frac{\text{COUNT}(\text{interações de conclusão ou percentual} \ge 100)}{\text{COUNT}(\text{interações de início ou visualização})} \right) \times 100$$
- **Fonte dos Dados**: Visões `vw_kpi_metricas_gerais` e `vw_kpi_desempenho_categoria` (tabelas `interacao`, `conteudo`, `categoria`).
- **Periodicidade**: Diária e Semanal.
- **Interpretação**:
  - **$\ge 60\%$ (Alta retenção)**: Conteúdo com excelente engajamento, didática adequada e duração balanceada.
  - **$30\% - 59\%$ (Retenção moderada)**: Comportamento típico para cursos extensos; requer monitoramento dos módulos intermediários.
  - **$< 30\%$ (Baixa retenção)**: Alerta crítico. Indica material prolixo, dificuldade técnica desproporcional ao nível indicado ou barreiras de usabilidade.

### KPI 2: Avaliação Média da Plataforma e Satisfação Percebida (Rating Médio)
- **Nome**: Avaliação Média por Categoria e Conteúdo (CSAT / Estrelas)
- **Objetivo**: Quantificar a percepção de qualidade pedagógica, relevância e clareza dos conteúdos pelo feedback explícito dos estudantes.
- **Fórmula**:
  $$\text{Avaliação Média} = \frac{\sum \text{avaliacao\_atribuida}}{\text{COUNT}(\text{interações com avaliação válida entre 1 e 5})}$$
- **Fonte dos Dados**: Visões `vw_kpi_metricas_gerais` e `vw_kpi_desempenho_categoria` (tabela `interacao`).
- **Periodicidade**: Contínua / Semanal.
- **Interpretação**:
  - **$\ge 4.2$**: Excelência de conteúdo. Candidato prioritário para ser sugerido no motor de recomendação.
  - **$3.5 - 4.1$**: Qualidade aceitável, mas com oportunidades pontuais de melhoria didática.
  - **$< 3.5$**: Desempenho insuficiente. Recomenda-se descontinuação ou refatoração integral do material pelo autor.

### KPI 3: Taxa de Qualidade e Assertividade das Recomendações
- **Nome**: Índice de Recomendações de Alta Afinidade (Taxa de Recomendações Positivas)
- **Objetivo**: Avaliar a eficiência do motor vetorial baseado em embeddings e pgvector em gerar sugestões relevantes para os usuários.
- **Fórmula**:
  $$\text{Taxa de Positivas (\%)} = \left( \frac{\text{COUNT}(\text{recomendações com status 'Positivo' [pontuação} \ge 70\text{]})}{\text{COUNT}(\text{total de recomendações geradas no lote})} \right) \times 100$$
- **Fonte dos Dados**: Visão `vw_kpi_recomendacoes_resumo` e tabela `recomendacao`.
- **Periodicidade**: Por lote de execução do pipeline.
- **Interpretação**:
  - Proporções acima de 60% demonstram que o motor encontra itens altamente correlatos ao histórico de consumo ($I_{vis}$) e aprovação ($I_{cur}$) dos estudantes, sem sugerir conteúdos desconexos.

### KPI 4: Retenção e Engajamento por Formato Didático
- **Nome**: Taxa de Conclusão e Tempo Médio por Formato de Mídia
- **Objetivo**: Comparar o comportamento e evasão dos alunos entre diferentes formatos (Curso, Vídeo, Artigo, Podcast) para guiar o esforço de produção.
- **Fórmula**:
  $$\text{Taxa Conclusão por Formato (\%)} = \left( \frac{\text{COUNT}(\text{conclusões no formato})}{\text{COUNT}(\text{inícios e visualizações no formato})} \right) \times 100$$
- **Fonte dos Dados**: Visão `vw_kpi_engajamento_formato` (tabelas `conteudo` e `interacao`).
- **Periodicidade**: Mensal / Por ciclo de produção.
- **Interpretação**: Vídeos e Podcasts apresentam taxas de conclusão superiores ($\approx 30\% - 34\%$) devido à menor barreira de tempo, enquanto cursos longos ($\approx 23\%$) demandam estratégias de gamificação ou quebra modular.

### KPI 5: Taxa de Conversão do Motor de Recomendação Vetorial
- **Nome**: Taxa de Aderência Real às Recomendações
- **Objetivo**: Mensurar se os conteúdos sugeridos pelo motor vetorial (RF10/RF11) foram efetivamente consumidos pelos usuários destinatários.
- **Fórmula**:
  $$\text{Taxa de Conversão (\%)} = \left( \frac{\text{COUNT}(\text{recomendações com interação posterior pelo mesmo usuário})}{\text{COUNT}(\text{total de recomendações geradas})} \right) \times 100$$
- **Fonte dos Dados**: Visão `vw_kpi_conversao_recomendacoes` (tabelas `recomendacao` e `interacao`).
- **Periodicidade**: Semanal.
- **Interpretação**: Taxas entre $8\%$ e $15\%$ são excelentes no contexto de sistemas de recomendação educacional sem interface push (consumo orgânico baseado em similaridade).

---

## 3. Visões Criadas no PostgreSQL

As consultas analíticas foram consolidadas em visões SQL estruturadas no arquivo `sql/criar_views_kpi.sql`:

1. **`vw_kpi_metricas_gerais`**: Linha única consolidada para alimentar os cartões de cabeçalho (Big Numbers) no Superset.
2. **`vw_kpi_desempenho_categoria`**: Métricas agrupadas por categoria e formato de mídia (Curso, Vídeo, Artigo, Podcast), expondo totais de interação, conclusões, notas médias e tempo médio.
3. **`vw_kpi_evolucao_temporal`**: Agrupamento cronológico diário (`data_hora::date`), permitindo traçar tendências de uso, dias de pico e evolução das avaliações.
4. **`vw_kpi_analise_conteudos`**: Base granular por conteúdo com dimensões categóricas (`categoria`, `tipo`, `nivel`, `autor`), viabilizando a aplicação de filtros interativos no dashboard.
5. **`vw_kpi_recomendacoes_resumo`**: Sumarização das pontuações médias e contagem de classificações (Positivo vs. Estável) geradas pelo RF10/RF11.
6. **`vw_kpi_engajamento_formato`**: Comparativo de desempenho, carga horária e taxa de conclusão por tipo de mídia didática.
7. **`vw_kpi_conversao_recomendacoes`**: Análise de conversão e eficácia prática das sugestões geradas por inteligência artificial.

---

## 4. Dashboard no Apache Superset (RF13)

### 4.1 Perguntas de Negócio Definidas e Respostas Analíticas
1. **Pergunta 1**: *Quais categorias e tipos de conteúdo apresentam maior taxa de engajamento e conclusão pelos alunos, indicando onde a instituição deve priorizar a produção de novos materiais?*
   - **Resposta Analítica**: Materiais dinâmicos e curtos lideram a retenção: Vídeos em *DevOps & Cloud* (44.4%) e *Engenharia de Dados* (50.0%) e Podcasts em *Programação & Software* (61.5%) superam amplamente os cursos longos tradicionais em retenção (que ficam em 23.1%), mantendo notas médias elevadas (> 4.5). **Recomendação**: Priorizar a produção de pílulas em vídeo e podcasts temáticos para tópicos introdutórios.
2. **Pergunta 2**: *Qual é o comportamento temporal do consumo na plataforma e quais temas sustentam consistentemente avaliações médias superiores a 4 estrelas?*
   - **Resposta Analítica**: A evolução temporal diária mostra fluxo contínuo de estudos com maior concentração de interações em ciclos quinzenais. Todas as categorias mantêm nota média superior a 4.0, com destaque para *Engenharia de Dados* (4.85) e *Programação & Software* (4.80), demonstrando excelente maturidade técnica e aprovação pelos discentes.

### 4.2 Componentes do Dashboard e Justificativas de Escolha

| Componente | Tipo de Visualização | Fonte de Dados | Justificativa de Escolha |
|---|---|---|---|
| **Total de Usuários Ativos** | Cartão (Big Number) | `vw_kpi_metricas_gerais.total_usuarios` | Proporciona leitura visual instantânea do alcance e base ativa da plataforma educacional. |
| **Avaliação Média Global** | Cartão (Big Number) | `vw_kpi_metricas_gerais.avaliacao_media_global` | Sintetiza em um único número de destaque o padrão de qualidade e satisfação percebida pelos alunos. |
| **Taxa de Conclusão Geral** | Cartão (Big Number) | `vw_kpi_metricas_gerais.taxa_conclusao_global_pct` | Alerta de forma objetiva sobre a eficiência da retenção estudantil global. |
| **Engajamento e Conclusão por Categoria** | Gráfico de Barras | `vw_kpi_desempenho_categoria` | O gráfico de barras é a visualização ideal para comparação direta entre variáveis categóricas discretas (categorias temáticas), permitindo identificar visualmente os segmentos líderes. |
| **Evolução Temporal de Interações Diárias** | Gráfico de Linhas | `vw_kpi_evolucao_temporal` | Séries temporais são representadas com máxima fidelidade por gráficos de linhas, revelando tendências, sazonalidades e variações diárias no engajamento. |
| **Filtro por Categoria Temática** | Filtro Interativo (Select) | `vw_kpi_analise_conteudos.categoria_nome` | Permite aos gestores e coordenadores segmentar o dashboard para inspecionar áreas específicas (ex.: Inteligência Artificial, Banco de Dados). |
| **Filtro por Nível do Conteúdo** | Filtro Interativo (Select) | `vw_kpi_analise_conteudos.nivel` | Possibilita avaliar o comportamento segregado entre materiais básicos, intermediários e avançados. |

---

## 5. Guia Prático de Configuração no Apache Superset

Para reproduzir ou conectar manualmente novos gráficos no Superset:

1. **Conexão com o PostgreSQL**:
   - Menu **Settings** -> **Database Connections** -> **+ Database**.
   - Escolha **PostgreSQL**.
   - Host: `postgres` | Port: `5432` | Database Name: `plataforma_educacional`
   - Username: `postgres` | Password: `postgres`
   - String SQLAlchemy: `postgresql+psycopg2://postgres:postgres@postgres:5432/plataforma_educacional`
2. **Criação de Datasets a partir das Views**:
   - Menu **Datasets** -> **+ Dataset**.
   - Selecione a conexão PostgreSQL, Schema `public` e a view desejada (ex.: `vw_kpi_desempenho_categoria`).
3. **Criação e Adição de Gráficos ao Dashboard**:
   - Clique em **Create Chart**, selecione o Dataset e o tipo (ex.: *Big Number* ou *ECharts Bar*).
   - Configure a métrica (ex.: `MAX(total_usuarios)`) e salve adicionando ao dashboard *Plataforma Educacional — KPIs e Recomendações*.

---

## 6. Organização das Evidências (Entregáveis)

Conforme a Seção 11 do edital, as evidências estão organizadas na pasta `dashboard/`:
- `dashboard/dashboard_plataforma_educacional.zip`: Arquivo nativo exportado do Apache Superset contendo todos os slices, datasets e layouts.
- `dashboard/evidencias/dashboard_geral.png`: Captura de tela do painel consolidado em execução.
- `dashboard/README.md`: Instruções de acesso, credenciais e justificativas teóricas.
