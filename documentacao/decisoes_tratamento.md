# Decisões de tratamento e padronização (RF04)

Este documento registra as decisões aplicadas em `src/tratamento.py`. A validação (RF03) diagnostica a qualidade dos dados brutos; o tratamento padroniza os campos para as etapas seguintes, sem alterar os arquivos originais.

Implementação: `src/tratamento.py`  
Entrada: `dados/brutos/`  
Saída: `dados/processados/`

## 1. Princípios

| Princípio | Decisão |
|-----------|---------|
| Preservar origem | Os arquivos em `dados/brutos/` nunca são sobrescritos. |
| Saída separada | O resultado vai para `dados/processados/` (`catalogo_tratado.csv`, `interacoes_tratadas.json`, `comentarios_tratados.json`). |
| Diagnóstico antes da correção | A validação roda sobre os dados brutos. O tratamento não esconde problemas de origem: o resumo da ingestão continua mostrando inválidos, incompletos e duplicados encontrados no bruto. |
| Não inventar conteúdo | Não imputamos título, descrição, autor, comentário, categoria, tipo, nível, data nem avaliação. |
| Domínio canônico | Valores categóricos conhecidos são mapeados de forma *case-insensitive* para o rótulo oficial usado na validação. Valores fora do domínio são apenas limpos (espaços) e permanecem como estão. |
| Duplicata | Remove-se a ocorrência extra; permanece a primeira no arquivo. |
| Incompleto | Não é descartado nesta etapa. Campos ausentes ficam nulos e são registrados no log. A exclusão na carga dos bancos fica para RF06/RF07. |

## 2. Espaços e caixa

### Espaços

Aplicamos `strip()` nas pontas de campos textuais. Espaços internos são preservados (fazem parte do título, da descrição e do comentário).

Campos de texto vazios (`""`, `"nan"`, `"None"`) voltam a nulo. Evitamos o efeito colateral de `astype(str)` sobre `NaN`, que geraria a string `"nan"` e mascararia ausência real.

### Letras maiúsculas e minúsculas

Não usamos `str.title()` de forma indiscriminada. Em português e em nomes técnicos isso quebraria o domínio:

- `"DevOps & Cloud".title()` vira `"Devops & Cloud"`
- `"avaliação".title()` vira `"Avaliação"`, fora do domínio das interações

A uniformização é feita por **mapa canônico** (comparação `casefold` com os conjuntos de `src/validacao.py`):

| Campo | Forma canônica | Motivo |
|-------|----------------|--------|
| `tipo` | `Artigo`, `Curso`, `Podcast`, `Vídeo` | Title Case com acento em `Vídeo` |
| `categoria` | rótulos oficiais do catálogo | preserva `&`, acentos e maiúsculas internas (`DevOps`, `BI` implícito no nome completo) |
| `nivel` | `Básico`, `Intermediário`, `Avançado` | acentos oficiais |
| `tipo_interacao` | minúsculas (`avaliação`, `curtida`, `visualização`, …) | o domínio da validação é em minúsculas |
| `tags` | minúsculas, sem espaços nas pontas | busca e agregação no MongoDB (RF07) |
| `titulo`, `descricao`, `autor`, `comentario` | só `strip` | nomes próprios e redação original |

## 3. Categorias, tipos e níveis

Os conjuntos oficiais são os mesmos da validação:

- **Tipos:** Artigo, Curso, Podcast, Vídeo
- **Categorias:** Banco de Dados, Business Intelligence, Ciência de Dados, DevOps & Cloud, Engenharia de Dados, Inteligência Artificial, Programação & Software, Segurança & Governança
- **Níveis:** Básico, Intermediário, Avançado
- **Tipos de interação:** avaliação, compartilhamento, conclusão, curtida, início, visualização

Se a origem trouxer `"curso"`, `"CURSO"` ou `"Curso"`, o tratamento grava `"Curso"`. Se trouxer um valor inexistente (`"Workshop"`), ele não é forçado para outra categoria: permanece após o `strip`, porque a validação já registrou o motivo e a imputação seria silenciosa.

## 4. Datas

| Fonte | Campo | Formato de saída |
|-------|-------|------------------|
| Catálogo | `data_publicacao` | `YYYY-MM-DD` |
| Interações | `data_hora` | `YYYY-MM-DDTHH:MM:SS` |
| Comentários | `data` | `YYYY-MM-DD` |

Conversão com `pandas.to_datetime(..., errors="coerce")`. Data ilegível vira nulo; não interpolamos nem preenchemos com a data da execução. O fuso não é adicionado: a origem não traz timezone.

## 5. Campos numéricos

| Campo | Tipo tratado | Observação |
|-------|--------------|------------|
| `carga_horaria_min` | inteiro anulável | valor ilegível → nulo, não `0` |
| `tempo_consumido` | inteiro anulável | idem |
| `percentual_conclusao` | float com 2 casas | faixa 0–100 é regra da validação, não do tratamento |
| `avaliacao` / `avaliacao_atribuida` | inteiro anulável | nulo **não** vira `0` (0 está fora de 1–5) |

Números negativos não são convertidos para positivo nem cortados para zero. A validação já os classifica como inválidos; o tratamento só garante o tipo.

A conversão de tipo (`5.0` → `5`) é considerada padronização e entra na contagem de registros corrigidos.

## 6. Valores ausentes

| Situação | Decisão |
|----------|---------|
| Título, descrição, autor ou comentário vazios | nulo; registrado no log |
| Categoria, tipo, nível ou tipo de interação vazios | nulo; sem imputação pela moda |
| `avaliacao_atribuida` nula | **valor de negócio válido**. Curtida, início, visualização, conclusão e compartilhamento nem sempre têm nota. Permanece `null` no JSON. |
| `avaliacao` de comentário ausente ou ilegível | nulo (não `0`) |
| Data ou número ilegível | nulo + log |

O log informa a quantidade de nulos por campo após o tratamento. Não há preenchimento por média, mediana ou valor sentinela.

## 7. Duplicidades

| Fonte | Chave de unicidade | O que permanece |
|-------|--------------------|-----------------|
| Catálogo | `conteudo_id` | primeira ocorrência |
| Interações | `(usuario_id, conteudo_id, data_hora)` | primeira ocorrência |
| Comentários | `(usuario_id, conteudo_id, data)` | primeira ocorrência |

A primeira ocorrência é a ordem do arquivo de origem, que é determinística. Não tentamos escolher o “melhor” duplicado (mais completo ou mais recente), para o resultado ser reproduzível sem regra extra.

O registro extra é eliminado do arquivo tratado e conta como corrigido. O motivo da duplicidade continua no relatório da validação.

## 8. Decisões por fonte

### Catálogo (`catalogo.csv` → `catalogo_tratado.csv`)

1. Limpar espaços em `titulo`, `tipo`, `categoria`, `nivel`, `descricao`, `autor`.
2. Canonicalizar `tipo`, `categoria` e `nivel`.
3. Converter `carga_horaria_min` para inteiro anulável.
4. Converter `data_publicacao` para `YYYY-MM-DD`.
5. Eliminar `conteudo_id` duplicado.
6. Gravar CSV UTF-8, sem índice.

### Interações (`interacoes.json` → `interacoes_tratadas.json`)

1. Canonicalizar `tipo_interacao` em minúsculas.
2. Converter `data_hora` para `YYYY-MM-DDTHH:MM:SS`.
3. Converter `tempo_consumido` para inteiro anulável.
4. Arredondar `percentual_conclusao` para 2 casas.
5. Converter `avaliacao_atribuida` para inteiro anulável, preservando nulos.
6. Eliminar a tripla duplicada.
7. Gravar JSON UTF-8 (com acentos), lista de objetos.

### Comentários (`comentarios.json` → `comentarios_tratados.json`)

1. Limpar espaços em `comentario`.
2. Converter `avaliacao` para inteiro anulável.
3. Converter `data` para `YYYY-MM-DD`.
4. Normalizar `tags`: lista de strings, `strip`, minúsculas, sem vazios, **sem duplicata na própria lista**, ordem alfabética (JSON determinístico).
5. Se `tags` não for lista, gravar `[]`.
6. Eliminar a tripla `(usuario_id, conteudo_id, data)`.
7. Gravar JSON UTF-8.

## 9. O que conta como registro corrigido

Um registro entra na métrica `corrigidos` do resumo (RF05) quando:

- ao menos um campo padronizado mudou de valor (espaços, caixa canônica, tipo numérico, data, ordem/caixa das tags); ou
- o registro foi removido por duplicidade.

Registros apenas relidos, já no formato oficial, não são corrigidos. Nulos de negócio em `avaliacao_atribuida` não são correção.

## 10. O que esta etapa não faz

- Não reclassifica o registro na validação (quem era inválido no bruto permanece inválido no relatório).
- Não carrega PostgreSQL nem MongoDB (RF06 e RF07).
- Não gera embeddings (RF08).
- Não descarta incompletos ou inválidos: isso será filtro da persistência, para o arquivo tratado continuar auditável.

## 11. Relação com a validação

A ordem no pipeline (`src/main.py`) é proposital:

1. leitura (RF02)
2. validação sobre o bruto (RF03)
3. tratamento (RF04)
4. resumo (RF05)

Assim o resumo mostra a qualidade **de origem**. Se invertêssemos validação e tratamento, problemas só de caixa (`"curso"` vs `"Curso"`) desapareceriam do diagnóstico.

## 12. Resultado na base atual

Execução de 12/09/2026 sobre `dados/brutos/`:

| Fonte | Lidos | Válidos | Corrigidos | O que mudou |
|-------|------:|--------:|-----------:|-------------|
| Catálogo | 1000 | 1000 | 0 | já estava no formato canônico |
| Interações | 1000 | 1000 | 356 | `avaliacao_atribuida` de float (`5.0`) para inteiro (`5`); 644 nulos preservados |
| Comentários | 1000 | 1000 | 837 | ordem alfabética das `tags` (a origem vinha em ordem livre) |

Nenhum duplicado foi removido nesta carga. Os originais em `dados/brutos/` permaneceram intactos.
