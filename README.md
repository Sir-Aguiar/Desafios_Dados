# Plataforma Educacional — Pipeline de Dados

Trabalho da disciplina Fundamentos de Dados para IA (FIC_DEV).

## Equipe

- [Adriano Froes]
- [Daniel Alves Santos]
- [Felipe Ferreira Aguiar]

## Situação Problema

Uma plataforma fictícia disponibiliza cursos, vídeos, artigos, podcasts e outros materiais educacionais. Atualmente, os dados estão distribuídos em diferentes arquivos e formatos, dificultando a identificação dos conteúdos mais procurados, a análise do comportamento dos usuários, a avaliação da qualidade dos materiais, a recomendação de conteúdos relacionados e a construção de indicadores para apoiar decisões.

A instituição deseja organizar esses dados, produzir recomendações simples e acompanhar os principais resultados em um dashboard.

> Produto esperado: pipeline reproduzível que integre ingestão, PostgreSQL, MongoDB, armazenamento vetorial, recomendações e um dashboard no Apache Superset.

## Problema Proposto

Cada equipe deverá desenvolver uma solução de dados capaz de:

1. Ingerir dados provenientes de diferentes fontes e formatos;
2. Armazenar dados estruturados em um banco relacional;
3. Armazenar dados semiestruturados em um banco NoSQL;
4. Representar descrições textuais por meio de embeddings;
5. Recuperar conteúdos semanticamente semelhantes;
6. Gerar recomendações simples;
7. Disponibilizar métricas e KPIs em um dashboard no Apache Superset.

> A solução deverá formar um fluxo integrado e reproduzível, desde a leitura dos dados de origem até sua apresentação no dashboard.

## Sobre os dados

Os arquivos em `dados/brutos/` são fictícios e foram gerados para o desafio:

Os originais não são modificados em nenhuma etapa.

### Catálogo de conteúdos (`catalogo.csv`):

| Campo             | Descrição                          |
| ----------------- | ---------------------------------- |
| conteudo_id       | Identificador do conteúdo.         |
| titulo            | Título do material.                |
| tipo              | Curso, vídeo, artigo ou podcast.   |
| categoria         | Área temática.                     |
| nivel             | Básico, intermediário ou avançado. |
| carga_horaria_min | Duração estimada em minutos.       |
| data_publicacao   | Data de publicação.                |
| descricao         | Descrição textual.                 |
| autor             | Responsável pelo conteúdo.         |

### Interações de usuários (`interacoes.json`):

A fonte deverá conter, no mínimo, identificador do usuário, identificador do conteúdo, tipo de interação, data e hora, tempo consumido, percentual de conclusão e avaliação atribuída.

Tipos de interação sugeridos:

- visualização;
- início;
- conclusão;
- curtida;
- avaliação;
- compartilhamento.

### Comentários e avaliações (`comentarios.json`):

Exemplo de documento:

```json
{
  "usuario_id": 104,
  "conteudo_id": 28,
  "avaliacao": 5,
  "comentario": "Conteúdo introdutório, claro e objetivo.",
  "tags": ["didático", "iniciante", "python"],
  "data": "2026-08-20"
}
```

## Práticas de DataOps

A solução deverá apresentar práticas básicas de DataOps:

- Código organizado em diretórios;
- Arquivo README.md;
- Dependências registradas;
- Parâmetros de conexão separados do código;
- Registro das etapas executadas;
- Tratamento básico de erros;
- Instruções para reproduzir a solução;
- Controle de versão.

## Arquitetura mínima esperada

| Etapa                  | Tecnologia ou Resultado                                         |
| ---------------------- | --------------------------------------------------------------- |
| Fontes                 | CSV, JSON                                                       |
| Ingestão               | Leitura, validação, limpeza e registro de erros.                |
| Dados Estruturados     | PostgreSQL                                                      |
| Dados Semiestruturados | MongoDB                                                         |
| Dados Vetoriais        | Pgvector                                                        |
| Processamento          | Busca semântica e motor de recomendação.                        |
| Apresentação           | Apache Superset conectado aos dados consolidados no PostgreSQL. |

## Estrutura

```
Desafios_Dados/
  src/          código Python do pipeline
  dados/        brutos (originais) e processados (tratados)
  sql/          scripts SQL (criação de tabelas, consultas)
  mongodb/      consultas NoSQL
  dashboard/    prints do Superset
  documentacao/ decisoes_tratamento.md, escolha_mongodb.md, modelo_embeddings.md, busca_semantica.md, recomendacao.md, kpis.md, uso_da_ia.md
  README.md
  config.yaml   parâmetros
  .env          credenciais (não versionado)
```

## Como rodar

Pré-requisitos: Python 3.10+, Docker, Git.

```bash
# 1. criar ambiente
python -m venv .venv

# Windows:
.\venv\Scripts\Activate.ps1

# Linux/Mac:
source venv/bin/activate

# 2. instalar dependências
pip install -r requirements.txt

# 3. criar .env na raiz (POSTGRES_* e MONGO_*)

# 4. subir bancos (o Postgres lê as credenciais do .env)
docker compose up -d

# 5. rodar
python -m src.main
```

O schema PostgreSQL é criado automaticamente na carga (`sql/criar_tabelas.sql`). Consultas manuais: `sql/consultas.sql`. A coleção MongoDB (índices e validador) é aplicada na carga; consultas manuais: `mongodb/consultas.js`. Depois dos embeddings, o pipeline demonstra a busca semântica (RF09) e gera e persiste as recomendações (RF10/RF11). Para repetir só essas etapas:

```bash
python -m src.busca_semantica
python -m src.busca_semantica "Quero aprender os fundamentos de banco de dados para inteligência artificial."

python -m src.recomendacao
python -m src.recomendacao 1
```

Se a senha do Postgres no `.env` mudar depois do primeiro `docker compose up`, é preciso recriar o volume (`docker compose down` + apagar `desafios_dados_postgres_data` + `up` de novo).

## Decisões que tomamos

- o enunciado pede que o sistema rode com `python -m src.main`, então organizamos os módulos como pacote único.
  As pastas `ingestao/` e `recomendacao/` sugeridas no PDF viram módulos (`src/ingestao.py`, `src/recomendacao.py`).
- **`config.yaml` + `.env`**: parâmetros versionáveis ficam no YAML, senhas ficam no `.env` (fora do Git).
- **Encoding UTF-8 explícito**: os dados têm acentuação em português (ex.: "Inteligência Artificial") e sem isso o Pandas quebra no Windows.
- **Validação antes de tratamento**: preferimos separar as etapas para deixar claro o que é regra de negócio (validação) e o que é padronização
  (tratamento). O diagnóstico do RF03 permanece sobre o bruto; o RF04 só padroniza a saída.
- **Tratamento sem imputação de conteúdo**: nulos de texto, data e avaliação não viram sentinela (`0`, `"nan"`, data de hoje). Categorias usam rótulo canônico *case-insensitive*, não `str.title()` (que quebraria `DevOps & Cloud` e `avaliação`). Detalhes em `documentacao/decisoes_tratamento.md`.
- **Modelo de embeddings (RF08)**: `all-MiniLM-L6-v2` do sentence-transformers. Escolhemos por ser leve (~90 MB), multilíngue o suficiente para o português e rápido em CPU. O texto embeddado é título + descrição; o vetor fica em `embedding_conteudo` associado ao `conteudo_id`. Recargas não geram de novo o mesmo par modelo/texto. Detalhes em `documentacao/modelo_embeddings.md`. **Se quiser usar um modelo maior, basta configurar o EMBEDDING_MODEL e EMBEDDING_DIMENSIONS no .env.**
- **Busca semântica (RF09)**: a frase em português é embeddada com o mesmo modelo e comparada aos vetores no pgvector (distância de cosseno). O `top_k` e as três consultas de demonstração ficam em `config.yaml`. Resultados no log e em `dados/processados/busca_semantica.json`. Detalhes em `documentacao/busca_semantica.md`.
- **Recomendação (RF10/RF11)**: pontuação `((Ivis + Icur) / 2) * 100 * Iconc`. Ivis e Icur vêm da similaridade de cosseno no pgvector (centroide do histórico de visualização e de curtidas/notas >= 4). Iconc remove concluídos. Positivo (>= 70) e Estável (entre 40 e 70) entram no ranking; Negativo é descartado. `top_n_por_usuario` está no YAML. O JSON vai para `dados/processados/recomendacoes.json`; o lote é gravado na tabela `recomendacao` (transação + upsert). Recargas inserem um novo `gerado_em`. Detalhes em `documentacao/recomendacao.md`.
- **PostgreSQL (RF06)**: o script `sql/criar_tabelas.sql` é a fonte da verdade do schema (o pipeline o executa). A recarga usa upsert (`ON CONFLICT`), sem truncar. Só entram registros tratados que passam nas regras de integridade. Comentários ficam para o MongoDB (RF07); `recomendacao` é preenchida pelo RF11.
- **MongoDB (RF07)**: só comentários/avaliações (tags em array e texto livre). A recarga usa upsert na tripla `(usuario_id, conteudo_id, data)`. A `categoria` é copiada do catálogo na carga para o `$group` do RF07. Detalhes em `documentacao/escolha_mongodb.md`.

## O que falta terminar

- KPIs e dashboard no Superset.

## Limitações

- A recomendação usa uma fórmula simples (média entre visualização e curtidas, filtrada por conclusão). Não é machine learning de verdade.
- O modelo de embeddings é pequeno, então buscas muito específicas podem trazer resultados apenas razoáveis.
- O Superset foi configurado localmente; em outra máquina vai precisar reconectar as fontes.
- Não há autenticação — é um projeto de estudo.

## Limitações conhecidas

- O motor de recomendação usa uma fórmula simples (média de visualização e curtidas, filtrada por conclusão). Não é aprendizado de máquina de verdade.
- O modelo de embeddings é pequeno, então buscas muito específicas podem trazer resultados apenas razoáveis.
- O Superset foi configurado localmente; em outra máquina vai precisar reconectar as fontes.
- Não temos autenticação em nada — é um projeto de estudo.
