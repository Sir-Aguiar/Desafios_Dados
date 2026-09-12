# Busca por similaridade semântica (RF09)

A busca fica em `src/busca_semantica.py`. Os vetores consultados são os gerados no RF08 (`embedding_conteudo`). O artefato SQL de verificação está em `sql/consultas.sql` (bloco RF09).

## 1. Como a consulta vira ranking

1. A frase em linguagem natural é embeddada com o **mesmo modelo** do RF08 (`encode_textos`, vetores normalizados).
2. O PostgreSQL ordena `embedding_conteudo.vetor` pela distância de cosseno do pgvector (`<=>` / `cosine_distance`).
3. A similaridade apresentada é `1 - distância` (vale porque os vetores estão normalizados).
4. O join com `conteudo` e `categoria` devolve identificador, título, categoria e tipo.
5. A posição é a ordem do ranking (1 = mais semelhante).

A quantidade de resultados vem de `busca_semantica.top_k_padrao` em `config.yaml` (padrão: 5). Dá para passar outro `top_k` em `BuscadorSemantico.buscar`.

Só entram vetores gravados com o modelo atualmente configurado. Assim uma troca de `EMBEDDING_MODEL` sem regenerar os embeddings não mistura espaços vetoriais.

## 2. Consultas demonstradas

As três frases estão em `config.yaml` (`busca_semantica.consultas_demonstracao`). A primeira é o exemplo do enunciado. O pipeline (`python -m src.main`) e o módulo isolado (`python -m src.busca_semantica`) as executam e gravam `dados/processados/busca_semantica.json`.

Execução de referência (modelo `sentence-transformers/all-mpnet-base-v2`, `top_k=5`):

### Consulta 1 — fundamentos de banco de dados para IA

> Quero aprender os fundamentos de banco de dados para inteligência artificial.

| Posição | ID | Título | Categoria | Tipo | Similaridade |
|--------:|---:|--------|-----------|------|-------------:|
| 1 | 630 | Papo de Dados Ep. 53: Desvendando Engenharia de Prompts e Agentes Inteligentes | Inteligência Artificial | Podcast | 0,5822 |
| 2 | 944 | Tech Talk Ep. 94: Melhores Práticas em Governança e Ética em Sistemas de IA | Inteligência Artificial | Podcast | 0,5375 |
| 3 | 314 | Tech Talk Ep. 44: Melhores Práticas em Visão Computacional e Processamento de Imagens | Inteligência Artificial | Podcast | 0,5320 |
| 4 | 437 | Arquitetura & Código Ep. 51: Inovações em Governança e Ética em Sistemas de IA | Inteligência Artificial | Podcast | 0,5244 |
| 5 | 759 | Princípios Essenciais e Arquitetura de Governança e Ética em Sistemas de IA | Inteligência Artificial | Artigo | 0,5232 |

A frase mistura dois temas. O catálogo tem muitos títulos de **Inteligência Artificial** e poucos que liguem banco de dados a IA; o embedding da consulta fica mais próximo desse agrupamento. As similaridades (~0,52–0,58) são moderadas, coerentes com uma intenção composta.

### Consulta 2 — Kubernetes e microsserviços

> Como orquestrar microsserviços com Kubernetes na prática?

| Posição | ID | Título | Categoria | Tipo | Similaridade |
|--------:|---:|--------|-----------|------|-------------:|
| 1 | 921 | Guia Definitivo e Boas Práticas sobre Orquestração de Microsserviços com Kubernetes | DevOps & Cloud | Artigo | 0,7173 |
| 2 | 14 | Arquitetura & Código Ep. 38: Inovações em Orquestração de Microsserviços com Kubernetes | DevOps & Cloud | Podcast | 0,7159 |
| 3 | 775 | Arquitetura & Código Ep. 95: Inovações em Orquestração de Microsserviços com Kubernetes | DevOps & Cloud | Podcast | 0,7117 |
| 4 | 792 | Princípios Essenciais e Arquitetura de Orquestração de Microsserviços com Kubernetes | DevOps & Cloud | Artigo | 0,7095 |
| 5 | 993 | Princípios Essenciais e Arquitetura de Orquestração de Microsserviços com Kubernetes | DevOps & Cloud | Artigo | 0,7081 |

Todos os cinco resultados são de **DevOps & Cloud** e falam de orquestração com Kubernetes. Similaridade alta (~0,71).

### Consulta 3 — Python avançado

> Preciso de conteúdo sobre Python avançado com orientação a objetos e decorators.

| Posição | ID | Título | Categoria | Tipo | Similaridade |
|--------:|---:|--------|-----------|------|-------------:|
| 1 | 99 | Princípios Essenciais e Arquitetura de Python Avançado: POO, Decorators e Geradores | Programação & Software | Artigo | 0,8154 |
| 2 | 406 | Princípios Essenciais e Arquitetura de Python Avançado: POO, Decorators e Geradores | Programação & Software | Artigo | 0,8152 |
| 3 | 316 | Melhores Práticas e Arquitetura de Python Avançado: POO, Decorators e Geradores | Programação & Software | Vídeo | 0,8093 |
| 4 | 506 | Melhores Práticas e Arquitetura de Python Avançado: POO, Decorators e Geradores | Programação & Software | Vídeo | 0,8022 |
| 5 | 19 | Solucionando Desafios do Dia a Dia em Python Avançado: POO, Decorators e Geradores | Programação & Software | Vídeo | 0,7928 |

O ranking devolve só conteúdos de **Programação & Software** sobre Python avançado (POO, decorators, geradores), com similaridade ~0,79–0,82.

## 3. Como repetir

```bash
# as tres consultas do config.yaml (depois do RF08)
python -m src.busca_semantica

# uma consulta livre (top_k do YAML)
python -m src.busca_semantica "Quero aprender os fundamentos de banco de dados para inteligência artificial."
```

No SQL, `sql/consultas.sql` mostra vizinhos de um conteúdo já embeddado (conteúdo 92 = curso de PostgreSQL/MongoDB), sem gerar o vetor da frase. A busca em linguagem natural permanece no Python, porque o embedding da consulta usa o Sentence Transformer.
