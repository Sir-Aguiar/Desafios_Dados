# Geração de recomendações (RF10)

O motor fica em `src/recomendacao.py`. Lê usuários, interações, catálogo e vetores de `embedding_conteudo` (RF08) no PostgreSQL. A geração (RF10) grava `dados/processados/recomendacoes.json`. Em seguida o mesmo módulo persiste o lote na tabela `recomendacao` (RF11). Consultas de verificação estão em `sql/consultas.sql` (blocos RF10 e RF11).

## 1. O que entra no ranking

Para cada par usuário × conteúdo candidato o sistema calcula três índices em `[0, 1]` e a pontuação oficial:

```
Pontuação = ((Ivis + Icur) / 2) * 100 * Iconc
```

A pontuação varia de 0 a 100. Os pesos `peso_ivis` / `peso_icur` do `config.yaml` (ambos 0,5) descrevem essa média simples; a fórmula do enunciado é a que vale.

| Índice | Sinal de negócio | Como é calculado |
|--------|------------------|------------------|
| **Ivis** | conteúdos visualizados / consumidos | Similaridade de cosseno (a mesma do RF09: `1 - distância`) entre o embedding do candidato e o **centroide** dos vetores pgvector dos conteúdos que o usuário consumiu (`visualização`, `início`, `conclusão`, ou `tempo_consumido > 0`), ponderado pelo tempo. Sem embedding de consumo, cai na proporção de tempo na mesma categoria. |
| **Icur** | curtidas e avaliações positivas | O mesmo cosseno, usando o centroide dos conteúdos com `tipo_interacao = curtida` ou `avaliacao_atribuida >= nota_minima_avaliacao_positiva` (padrão 4). Sem histórico explícito, Icur = 0. |
| **Iconc** | remoção de concluídos | `0` se o usuário já concluiu o conteúdo (`conclusão` ou `percentual_conclusao >= 100`); `1` caso contrário. Com 0 a pontuação zera. |

Cossenos negativos são cortados em 0, para os índices permanecerem na faixa pedida.

## 2. Classificação

| Status | Regra | Destino |
|--------|-------|---------|
| **Positivo** | pontuação >= 70 | entra na lista de sugestões |
| **Estável** | 40 < pontuação < 70 | entra na lista de sugestões |
| **Negativo** | pontuação <= 40 **ou** Iconc = 0 | descartado da lista |

O enunciado escreve a faixa estável como `40 > pontuação < 70`. Interpretamos o intervalo intermediário aberto `(40, 70)`, que é o que sobra entre Negativo (`<= 40`) e Positivo (`>= 70`).

A lista apresentada é só Positivo e Estável, ordenada por pontuação decrescente, limitada a `recomendacao.top_n_por_usuario` (padrão 5). A posição 1 é a de maior pontuação daquele usuário. Cada item traz usuário, conteúdo recomendado, pontuação, posição e data de geração.

## 3. Execução de referência

Rodado depois do RF08 (modelo `sentence-transformers/all-mpnet-base-v2`, `top_n=5`):

| Indicador | Valor |
|-----------|------:|
| Usuários processados | 150 |
| Recomendações apresentadas | 742 |
| Positivas | 576 |
| Estáveis | 166 |
| Negativas descartadas | 46 775 (154 por conclusão) |
| Usuários sem sugestão | 0 |
| Conteúdos concluídos que voltaram à lista | 0 |

Quase todos os usuários recebem 5 itens; alguns (sem curtida/avaliação) ficam só com Estável e podem ter menos de 5, porque `Icur = 0` limita a pontuação a `Ivis * 50`.

### Usuário 1 — concluiu Storytelling; Iconc remove o material já feito

Histórico inclui conclusão do curso de Storytelling com Dados (id 179). As sugestões são **outros** conteúdos do mesmo tema, não o concluído.

| Posição | ID | Título | Pontuação | Status |
|--------:|---:|--------|----------:|--------|
| 1 | 94 | Curso Completo de Storytelling com Dados… | 72,26 | Positivo |
| 2 | 63 | Especialização em Storytelling com Dados… | 70,39 | Positivo |
| 3 | 237 | Solucionando Desafios do Dia a Dia em Storytelling… | 69,88 | Estável |
| 4 | 797 | Formação Prática em Storytelling com Dados… | 69,86 | Estável |
| 5 | 358 | Masterclass de Storytelling com Dados… | 69,46 | Estável |

### Usuário 2 — visualiza Ciência de Dados e curte/avalia bem

Ivis e Icur altos juntos; os cinco primeiros são Positivo (métricas de modelos e DataOps).

| Posição | ID | Categoria | Pontuação | Status |
|--------:|---:|-----------|----------:|--------|
| 1 | 736 | Ciência de Dados | 78,15 | Positivo |
| 2 | 880 | Engenharia de Dados | 77,37 | Positivo |
| 3 | 452 | Ciência de Dados | 77,08 | Positivo |
| 4 | 91 | Engenharia de Dados | 76,92 | Positivo |
| 5 | 74 | Ciência de Dados | 75,76 | Positivo |

### Usuário 3 — só visualizou; sem curtida nem nota >= 4

Icur = 0. A pontuação vira `Ivis * 50`. Só passam conteúdos com Ivis > 0,80 (Estável logo acima de 40). O material concluído de ingestão CSV/JSON/Parquet (id 614) não aparece; aparecem podcasts do mesmo assunto.

| Posição | ID | Título | Ivis | Icur | Pontuação | Status |
|--------:|---:|--------|-----:|-----:|----------:|--------|
| 1 | 208 | Papo de Dados Ep. 104: Ingestão Eficiente de CSV, JSON e Parquet | 0,8139 | 0 | 40,69 | Estável |
| 2 | 185 | Papo de Dados Ep. 15: Ingestão Eficiente de CSV, JSON e Parquet | 0,8119 | 0 | 40,59 | Estável |

## 4. Como repetir

```bash
# todos os usuarios (depois do RF06 e do RF08)
python -m src.recomendacao

# um usuario
python -m src.recomendacao 1
```

O pipeline (`python -m src.main`) chama a mesma geração depois da busca semântica.

## 5. Persistência no PostgreSQL (RF11)

Cada linha gravada em `recomendacao` tem os campos mínimos do requisito:

| Coluna | Papel |
|--------|--------|
| `usuario_id` | usuário da sugestão (FK) |
| `conteudo_id` | conteúdo recomendado (FK) |
| `pontuacao` | pontuação final (0–100, `NUMERIC(5,2)`) |
| `posicao` | posição no ranking daquele usuário (>= 1) |
| `gerado_em` | data e hora da geração (lote) |
| `classificacao` | Positivo / Estável (Negativo não é persistido) |

A inserção é transacional. Recargas **não truncam**: a unicidade `(usuario_id, conteudo_id, gerado_em)` e `(usuario_id, posicao, gerado_em)` permite um novo snapshot por execução. Em conflito no mesmo segundo, o upsert atualiza pontuação, posição e classificação. O ranking “atual” é o `MAX(gerado_em)`.

Depois do commit o pipeline consulta `COUNT` da tabela, `COUNT` do lote e uma amostra com join em `conteudo`. Execução de referência: **742** linhas persistidas (576 Positivo, 166 Estável), as mesmas geradas no RF10.

```bash
python -m src.recomendacao
```
