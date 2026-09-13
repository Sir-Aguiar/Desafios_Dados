# Dashboard Apache Superset — Plataforma Educacional (RF13)

Este diretório contém a especificação, arquivos e evidências do dashboard analítico construído no Apache Superset a partir dos dados estruturados no PostgreSQL (`plataforma_educacional`).

---

## 1. Como Acessar o Apache Superset

1. Certifique-se de que os containers estão em execução:
   ```bash
   docker compose up -d
   ```
2. Abra o navegador em:
   [http://localhost:8088](http://localhost:8088)
3. Credenciais de acesso:
   - **Usuário**: `admin`
   - **Senha**: `admin`

---

## 2. Visão Geral dos Indicadores e Gráficos do Dashboard

O dashboard foi expandido para reunir 10 visões integradas cobrindo desde KPIs estratégicos até controle de qualidade e motor de recomendação:

1. **Linha de Cartões de Indicadores (Big Numbers)**:
   - **Total de Usuários Ativos**: 150 discentes (MAX de `vw_kpi_metricas_gerais`)
   - **Avaliação Média Geral (CSAT)**: 4.48 estrelas em escala de 1 a 5
   - **Taxa de Conclusão Global**: 28.6% dos conteúdos iniciados/visualizados
   - **Taxa de Recomendações Positivas**: 78.1% (materiais com score $\ge$ 70)
   - **Taxa de Seletividade do Motor**: 1.96% (744 persistidos de 38.007 candidatos)

2. **Linha 2 — Análise de Engajamento e Séries Temporais**:
   - **Engajamento e Conclusões por Categoria (Barras)**: Total de interações e conclusões por trilha (`vw_kpi_desempenho_categoria`).
   - **Evolução Temporal de Interações Diárias (Linhas)**: Série cronológica de volume diário de acessos (`vw_kpi_evolucao_temporal`).

3. **Linha 3 — Inteligência de Recomendações e Formatos**:
   - **Distribuição de Recomendações por Categoria (Barras)**: Volume de sugestões geradas por área temática (`vw_kpi_recomendacoes_categoria_status`).
   - **Engajamento e Retenção por Formato de Conteúdo (Barras)**: Desempenho comparativo entre Cursos, Vídeos, Podcasts e Artigos (`vw_kpi_engajamento_formato`).

4. **Linha 4 — Auditoria e Confiabilidade de Dados**:
   - **Controle de Qualidade e Higienização da Ingestão (Tabela)**: Auditoria completa das fontes de dados (`catalogo`, `interacoes`, `comentarios`), exibindo volume lido, corrigido, taxa de correção e 100% de conformidade (`vw_kpi_qualidade_ingestao`).

5. **Datasets Sincronizados no Superset (12 Views)**:
   - `vw_kpi_metricas_gerais`
   - `vw_kpi_desempenho_categoria`
   - `vw_kpi_evolucao_temporal`
   - `vw_kpi_analise_conteudos`
   - `vw_kpi_recomendacoes_resumo`
   - `vw_kpi_seletividade_recomendacao`
   - `vw_kpi_recomendacoes_categoria_status`
   - `vw_kpi_qualidade_ingestao`
   - `vw_kpi_desempenho_categoria_tipo`
   - `vw_kpi_evolucao_temporal_diaria`
   - `vw_kpi_engajamento_formato`
   - `vw_kpi_conversao_recomendacoes`

---

## 3. Resposta às Perguntas de Negócio

- **Pergunta 1**: *Quais categorias e tipos de conteúdo apresentam maior taxa de engajamento e conclusão pelos alunos, indicando onde a instituição deve priorizar a produção de novos materiais?*
  - **Resposta**: Formatos dinâmicos (Vídeos em *DevOps & Cloud* e *Engenharia de Dados* com taxas de 44% a 50%, e Podcasts em *Programação* com 61.54%) superam amplamente cursos longos tradicionais em retenção, mantendo médias de satisfação acima de 4.5. Recomenda-se priorizar a produção de vídeos práticos e podcasts temáticos.
- **Pergunta 2**: *Qual é o comportamento temporal do consumo na plataforma e quais temas sustentam consistentemente avaliações médias superiores a 4 estrelas?*
  - **Resposta**: O consumo apresenta regularidade com picos nos ciclos de lançamento. Todas as categorias mantêm médias superiores a 4.0, com destaque para *Engenharia de Dados* (4.85) e *Programação & Software* (4.80).

---

## 4. Estrutura de Evidências

As capturas de tela e evidências de execução do dashboard estão armazenadas em `dashboard/evidencias/`:
- `dashboard/evidencias/dashboard_geral.png`: Visão geral do painel completo com cartões e gráficos.
- `dashboard/evidencias/grafico_barras_categorias.png`: Detalhe do gráfico comparativo de categorias.
- `dashboard/evidencias/grafico_linhas_temporal.png`: Detalhe da evolução temporal de interações.
