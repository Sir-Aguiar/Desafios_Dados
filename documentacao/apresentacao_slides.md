# Roteiro Completo de Apresentação (Pitch de 10 Minutos)
## Desafio Prático 1 — Pipeline de Recomendação e Dashboard de Conteúdos Educacionais
**Fundamentos de Dados para IA (FIC_DEV)**

---

## 1. Distribuição de Tempo da Apresentação

| Bloco | Slides | Assunto Principal | Tempo Alocado |
| :--- | :---: | :--- | :---: |
| **Abertura & Arquitetura** | Slide 1 | Problema de negócio e fluxo do pipeline integrado | ~35 segundos |
| **Ingestão & Qualidade** | Slide 2 | Governança de dados, auditoria e correções sem perdas | ~55 segundos |
| **IA & Busca Vetorial** | Slide 3 | Embeddings, pgvector e fórmula do motor de recomendação | ~60 segundos |
| **Dashboard & KPIs** | Slides 4 a 7 | **Foco Principal**: Big Numbers, categorias, formatos e séries | **~5 minutos** |
| **Engenharia & Desafios** | Slide 8 | Solução de problemas técnicos reais e uso de IA com auditoria | ~60 segundos |
| **Fechamento** | Slide 9 | Recomendações pedagógicas e plano de ação estratégico | ~60 segundos |
| **Total** | **9 Slides** | **Pitch Completo** | **~9 min 30 s** |

---

## 2. Slides e Notas do Apresentador

---

### Slide 1 — Visão Geral do Pipeline e Problema de Negócio
- **Tempo**: `00:00 - 00:35`
- **Bullets do Slide**:
  - **Problema**: Plataforma multiformato com alto volume de dados, mas baixa visibilidade de engajamento discente
  - **Pipeline Integrado**: Ingestão (CSV/JSON) $\rightarrow$ Armazenamento Híbrido $\rightarrow$ IA Vetorial $\rightarrow$ Dashboard Executivo
  - **Meta Analítica**: Transformar 3.000 registros operacionais em decisões pedagógicas e redução da evasão
- **Fala Sugerida (Notas do Apresentador)**:
  > *"Bom dia a todos os membros da banca. Hoje apresentamos a solução da nossa equipe para a plataforma de conteúdos educacionais. Nosso desafio principal não foi apenas construir um pipeline que funcionasse tecnicamente, mas responder a uma dor crítica de qualquer edtech: como transformar dados brutos de navegação em decisões pedagógicas concretas para combater a evasão de alunos. Nossa arquitetura conecta fontes multimodais em CSV e JSON, passa por um armazenamento híbrido no PostgreSQL e MongoDB, utiliza representações vetoriais com pgvector para inteligência semântica e entrega os resultados mastigados em um dashboard analítico no Apache Superset. Vamos ver como esses dados se comportaram na prática."*

---

### Slide 2 — Governança e Qualidade dos Dados de Entrada
- **Tempo**: `00:35 - 01:30`
- **Bullets do Slide**:
  - **Catálogo de Conteúdos**: 1.000 itens \| 0 correções (**0,0%** — origem 100% íntegra)
  - **Histórico de Interações**: 1.000 eventos \| 356 correções (**35,6%** — saneamento de nulos e percentuais)
  - **Comentários e Avaliações (MongoDB)**: 1.000 registros \| 837 correções (**83,7%** — sanitização textual e notas)
  - **Governança Final**: **100% de conformidade** em todas as bases, sem descarte de linhas
- **Fala Sugerida (Notas do Apresentador)**:
  > *"Começando pela base de tudo: a confiabilidade da ingestão. Processamos três mil registros no total, mil de cada fonte, e aplicamos regras rigorosas de saneamento antes de qualquer gravação. O catálogo de conteúdos chegou perfeito: mil itens lidos, zero correções necessárias. Já nas interações dos estudantes, 35,6% dos registros precisaram de tratamento de valores nulos e normalização de percentuais. Nos comentários em MongoDB, 83,7% passaram por higienização de strings e validação de notas. O grande diferencial de engenharia da nossa equipe foi garantir 100% de conformidade operacional final com zero descarte de linhas. Nenhum dado foi varrido para debaixo do tapete: tudo foi validado, corrigido e integrado com rastreabilidade."*

---

### Slide 3 — Inteligência Semântica e Motor de Recomendação
- **Tempo**: `01:30 - 02:30`
- **Bullets do Slide**:
  - **Vetorização**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensões com `pgvector`)
  - **Precisão Semântica (RF09)**:
    - Busca específica (*"Python avançado com POO e decorators"*): **0,84** de similaridade (alta assertividade)
    - Busca ampla (*"Fundamentos de banco de dados para IA"*): **0,66** de similaridade (tema difuso)
  - **Regra de Recomendação**: $\text{Pontuação} = \left(\frac{I_{vis} + I_{cur}}{2}\right) \times 100 \times I_{conc}$ (conteúdo concluído é zerado)
  - **Eficiência do Motor**: **744 recomendações geradas** \| **1,96% de seletividade** (744 de 38.007 pares) \| **78,09% de alta afinidade** ($\ge 70$)
- **Fala Sugerida (Notas do Apresentador)**:
  > *"Para a busca e recomendação, geramos vetores de 384 dimensões utilizando o modelo MiniLM-L6-v2 integrado nativamente ao PostgreSQL via extensão pgvector. Validamos que a busca semântica responde com altíssima precisão quando a intenção do aluno é clara: para uma consulta como 'Python avançado com POO', atingimos similaridade de 0,84 no topo do ranking. Para termos mais amplos, como 'Fundamentos de banco para IA', a similaridade fica em torno de 0,66, refletindo com precisão a dispersão do tema. Nosso motor de recomendação combina histórico de visualização e curtida com uma trava obrigatória: conteúdos já concluídos têm pontuação zerada automaticamente. Avaliamos mais de 38 mil pares possíveis de usuário e conteúdo, e o motor foi cirúrgico: persistiu apenas 744 recomendações — uma taxa de seletividade de 1,96% —, sendo que mais de 78% dessas sugestões são de altíssima afinidade, com pontuação superior a 70 pontos."*

---

### Slide 4 — Painel Executivo: O Diagnóstico Global (RF12 / RF13)
- **Tempo**: `02:30 - 03:30`
- **Bullets do Slide**:
  - **Base Ativa**: 150 alunos consumindo 1.000 conteúdos em 1.000 interações
  - **Satisfação Geral (CSAT)**: **4,48 / 5,00** estrelas (aprovação massiva do catálogo)
  - **Tempo Médio de Estudo**: **144,9 minutos** por material
  - **Taxa de Conclusão Global**: **28,62%** (154 conclusões sobre 538 inícios/visualizações)
  - **O Paradoxo do Negócio**: Alunos amam o conteúdo (nota 4,48), mas menos de 1 em cada 3 conclui o que começa
- **Fala Sugerida (Notas do Apresentador)**:
  > *"Entrando agora no coração do nosso projeto: o que esses números realmente nos dizem sobre o negócio no nosso Dashboard do Superset? Temos uma base ativa de 150 alunos interagindo com mil conteúdos. À primeira vista, o cenário parece dos sonhos: a avaliação média global é de 4,48 estrelas em 5. Os estudantes que avaliam o catálogo atribuem notas de excelência. Porém, ao cruzar esse dado com a conclusão, encontramos o grande paradoxo da plataforma: a taxa de conclusão global é de apenas 28,62%. Foram 154 conclusões para mais de 530 materiais iniciados ou visualizados, com um tempo médio de consumo de cerca de 145 minutos. A pergunta que fizemos aos dados foi: se o conteúdo é tão bem avaliado, por que menos de um terço dos alunos chega até o fim? Fomos investigar onde está esse atrito."*

---

### Slide 5 — Descoberta 1: O Desempenho por Trilhas Temáticas
- **Tempo**: `03:30 - 05:00`
- **Bullets do Slide**:
  - **Líder Absoluto em Conclusão**: *DevOps & Cloud* (**42,62%** de conclusão \| 141 interações)
  - **Maior Volume de Acesso**: *Business Intelligence* (144 interações \| 26,92% de conclusão)
  - **Ponto Crítico de Evasão**: *Segurança & Governança* (**13,16%** de conclusão \| 195 min médios)
  - **Campeão de Satisfação**: *Engenharia de Dados* (**4,75** estrelas de CSAT médio)
  - **Diagnóstico**: O gargalo de abandono em Segurança não é falta de interesse, mas atrito no formato do material
- **Fala Sugerida (Notas do Apresentador)**:
  > *"Nossa primeira hipótese foi: será que algumas áreas do conhecimento são rejeitadas pelos alunos? Olhamos para o gráfico de barras por categoria. Vejam o contraste: DevOps & Cloud é o nosso campeão de engajamento prático, atingindo 42,6% de taxa de conclusão com 141 interações. Logo ao lado, Business Intelligence lidera o volume bruto com 144 interações. Por outro lado, encontramos um abismo em Segurança & Governança: a taxa de término cai para alarmantes 13,16%, mesmo sendo a categoria com maior tempo médio gasto por aluno — quase 195 minutos. E aqui está a chave: em Segurança, a nota média é altíssima: 4,68 estrelas! E Engenharia de Dados lidera a satisfação com 4,75. Isso prova tecnicamente que o aluno não abandona por falta de interesse no tema. O problema é a forma como o conteúdo está empacotado."*

---

### Slide 6 — Descoberta 2: O Formato Didático Define a Retenção
- **Tempo**: `05:00 - 06:30`
- **Bullets do Slide**:
  - **O Campeão do Dataset**: *Podcast em Programação & Software* $\rightarrow$ **61,54% de conclusão**
  - **O Pior Gargalo**: *Vídeo em Segurança & Governança* $\rightarrow$ **6,67% de conclusão**
  - **Formatos Ágeis Vencem**: Vídeos (**33,85%**) e Podcasts (**29,20%**) lideram retenção com ~30 min de duração
  - **A Evasão dos Cursos Longos**: Apenas **23,14%** de término geral (exigem 563 min de dedicação)
  - **Decisão Estratégica**: Decompor cursos densos em microlearning (vídeos curtos) e podcasts temáticos
- **Fala Sugerida (Notas do Apresentador)**:
  > *"Quando cruzamos Categoria com Formato Didático, encontramos a resposta definitiva — este é o insight mais forte de todo o projeto. O conteúdo com maior taxa de término absoluto de todo o dataset é Podcast em Programação & Software, com 61,54% de conclusão. Os alunos escutam os 28 minutos médios de áudio e concluem o aprendizado com nota 4,27. No extremo oposto, o pior gargalo de toda a plataforma é Vídeo em Segurança & Governança, onde a conclusão despenca para meros 6,67%. Olhando a visão geral de formatos, o padrão é irrefutável: Vídeos e Podcasts sustentam taxas médias de 29% a 34% de conclusão, porque exigem cerca de 30 minutos de atenção. Já os Cursos Longos tradicionais têm a pior retenção média da plataforma, com apenas 23,1%, exigindo mais de 560 minutos. A recomendação executiva para a diretoria pedagógica é clara: não criem cursos monolíticos de 10 horas. Quebrem esses temas em trilhas de microlearning com vídeos curtos e podcasts temáticos."*

---

### Slide 7 — Descoberta 3: Comportamento Temporal e Sazonalidade
- **Tempo**: `06:30 - 07:30`
- **Bullets do Slide**:
  - **Cobertura Cronológica**: 234 dias com atividade mapeada ao longo do ano acadêmico
  - **Consumo Diário Médio**: 4,27 interações/dia com ritmo estável
  - **Padrão de Picos**: Concentração em datas específicas (dias com 7 a 12 interações registradas)
  - **Gatilho de Engajamento**: Picos associados diretamente a lançamentos de trilhas e períodos de entrega
- **Fala Sugerida (Notas do Apresentador)**:
  > *"No gráfico temporal de linhas do Superset, mapeamos 234 dias de consumo contínuo durante o ano letivo. Identificamos uma média saudável de 4,3 interações diárias. No entanto, o aprendizado não acontece em fluxo estritamente uniforme: temos picos expressivos que chegam a 7, 10 e até 12 interações em um único dia. Ao correlacionar esses picos com o calendário, percebemos que eles coincidem exatamente com semanas de encerramento de ciclos e lançamentos de materiais novos. O aluno reage fortemente a estímulos de novidade e prazos bem definidos, o que valida o uso de campanhas periódicas de reengajamento."*

---

### Slide 8 — Desafios Técnicos Superados e Engenharia com IA
- **Tempo**: `07:30 - 08:30`
- **Bullets do Slide**:
  - **Armadilha do Superset**: Erro de `datetime` em barras categóricas $\rightarrow$ Diagnóstico e migração para `dist_bar`
  - **Qualidade de Dados**: Incompatibilidade de tipos e nulos $\rightarrow$ Tratamento algorítmico sem perda de registros
  - **Uso da IA (Gemini)**: Aceleração na modelagem SQL de views analíticas e orquestração Docker
  - **Auditoria da Equipe**: 100% das fórmulas e métricas foram recalculadas e validadas contra o banco
- **Fala Sugerida (Notas do Apresentador)**:
  > *"Como em qualquer projeto de engenharia de dados em produção, enfrentamos desafios técnicos reais que nos exigiram senso crítico. No Superset, por exemplo, ao tentar plotar os gráficos de barras por categoria, a ferramenta exigia uma coluna temporal obrigatória porque estava configurada como série temporal. Diagnosticamos que o componente adequado para dados categóricos sem data é o dist_bar, reestruturando o payload e restabelecendo o painel com sucesso. Em relação ao uso de Inteligência Artificial, utilizamos o modelo Gemini como parceiro de pair programming para acelerar a escrita das visões SQL e scripts de automação. Mas como rege a boa prática de engenharia, 100% dos cálculos, agrupamentos com NULLIF e métricas foram auditados e recalculados pela equipe contra o PostgreSQL, garantindo total integridade das fórmulas."*

---

### Slide 9 — Conclusão e Recomendações para a Instituição
- **Tempo**: `08:30 - 09:30`
- **Bullets do Slide**:
  - **Ação 1 (Produção)**: Priorizar vídeos práticos em DevOps e podcasts em Programação (formatos comprovados)
  - **Ação 2 (Reformulação)**: Intervir em Segurança & Governança, fatiando materiais em micro-módulos
  - **Ação 3 (Retenção)**: Acionar o motor de recomendação (78% de alta afinidade) para reengajar alunos em risco
  - **Entrega**: Plataforma analítica completa, auditada e operando em tempo real no Superset
- **Fala Sugerida (Notas do Apresentador)**:
  > *"Para concluir, entregamos três ações estratégicas imediatas para a liderança da instituição: Primeira: Priorizar a produção de vídeos práticos e podcasts nas áreas de maior tração, como DevOps e Programação, que já provaram reter mais de 60% dos estudantes. Segunda: Intervir urgentemente nos materiais de Segurança & Governança, substituindo vídeos longos e monótonos por estudos de caso fragmentados. E terceira: Ativar em produção o motor de recomendação vetorial, que com seus 78% de precisão positiva consegue sugerir o próximo passo ideal antes que o aluno evada. A plataforma está 100% conteinerizada, documentada e com o dashboard operando em tempo real. Estamos prontos para as perguntas da banca. Muito obrigado."*

---

## 3. Folha de Apoio Rápido (Cheat Sheet da Banca)

### Números Exatos de Bolso
- **Usuários**: 150 alunos
- **Conteúdos**: 1.000 itens (272 Artigos, 256 Podcasts, 238 Vídeos, 234 Cursos)
- **Interações**: 1.000 eventos (356 avaliações, 154 conclusões)
- **Avaliação Média Global (CSAT)**: 4,48 / 5,00
- **Taxa Conclusão Global**: 28,62% (154 conclusões / 538 inícios+visualizações)
- **Tempo Médio Geral**: 144,9 min (Artigo: 9,4 min | Vídeo: 29,2 min | Podcast: 29,9 min | Curso: 563,4 min)
- **Recomendações no Lote**: 744 (581 Positivas = 78,09% | 163 Estáveis = 21,91%)
- **Seletividade do Motor**: 1,96% (744 selecionadas de 38.007 pares)
- **Qualidade de Ingestão**: Catálogo 0% corrigido | Interações 35,6% corrigido | Comentários 83,7% corrigido | 100% conformidade final

### Respostas Prontas para Perguntas da Banca
1. **Diferença de taxas de conclusão (Global 28,6% vs DevOps 42,6%)**: A taxa global pondera todos os 538 inícios/visualizações do catálogo inteiro. Categorias dinâmicas com alta prática (DevOps) convertem muito mais do que categorias densas e teóricas (Segurança, 13,1%), que puxam a média global para baixo.
2. **Seletividade de 1,96% não é restritiva demais?**: Não, o produto cartesiano totalizava 38.007 combinações. Recomendar aleatoriamente geraria ruído e repetição. O motor excluiu 37.109 pares com score < 40 e 154 já concluídos, entregando cerca de 5 recomendações hiper-personalizadas por aluno.
3. **Por que 83,7% dos comentários foram corrigidos?**: O schema do MongoDB continha strings com espaços extras, tags não padronizadas e campos nulos. O pipeline higienizou os dados defensivamente sem descartar nenhuma linha.

---

## 4. URLs de Acesso no Ambiente Docker

| Serviço | URL de Acesso | Descrição |
| :--- | :--- | :--- |
| **Apresentação Web (Docker)** | [`http://localhost:8085/`](http://localhost:8085/) | Slides interativos com temporizador, cheat sheet e notas |
| **Apache Superset (Dashboard)** | [`http://localhost:8088/superset/dashboard/1/`](http://localhost:8088/superset/dashboard/1/) | Painel analítico executivo ao vivo (`admin` / `admin`) |
| **Superset (Slug URL)** | [`http://localhost:8088/superset/dashboard/plataforma-educacional-kpis/`](http://localhost:8088/superset/dashboard/plataforma-educacional-kpis/) | URL semântica oficial do Dashboard no Superset |
| **Superset SQL Lab** | [`http://localhost:8088/sqllab/`](http://localhost:8088/sqllab/) | Console interativo para consultas SQL sob demanda |
| **PostgreSQL + pgvector** | `localhost:5433` | Banco relacional vetorial (DB: `plataforma_educacional`) |
| **MongoDB NoSQL** | `localhost:27017` | Banco NoSQL de comentários e avaliações dos estudantes |

