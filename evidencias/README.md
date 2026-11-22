# Índice de evidências de funcionamento

> Todas as evidências saem da execução real do projeto. Os campos marcados com ☐ ainda precisam ser
> gerados pelo grupo. **Não inventar números:** cada valor abaixo vem de um arquivo indicado ao lado.

Repositório: https://github.com/DanielCarvalho123/text2sql-seguro

## Evidências obrigatórias

| # | Evidência | Arquivo / link | Status |
| --- | --- | --- | --- |
| 1 | Vídeo (3 a 5 min, tela inteira, `docker compose up` do zero + fluxo principal) | [`videos/demo.mp4`](videos/demo.mp4) (4 min 59 s, tela inteira; o IP público que aparecia no terminal foi borrado) · complementar: [`videos/teste-funcionalidades.mp4`](videos/teste-funcionalidades.mp4) | ✅ 22/11/2026 |
| 2 | Execução verde do CI na tag `v1.0` | link: ___ · captura: `prints/ci-verde.png` | ☐ após criar a tag (a `main` já está verde: https://github.com/DanielCarvalho123/text2sql-seguro/actions) |
| 3 | Resultados da avaliação | [`../eval/resultados/`](../eval/resultados/) · comando: `docker compose run --rm app python eval/avaliar.py` | ✅ 22/11/2026 |
| 4 | Logs de uma execução completa | [`../eval/resultados/avaliacao.log`](../eval/resultados/avaliacao.log) (avaliação inteira, 1 evento JSON por linha com data e hora) e [`logs/`](logs/) (uso da interface) | ✅ |
| 5 | Capturas de tela (≥ 5, incluindo uma falha tratada) | [`prints/`](prints/) (6 capturas, 2 falhas tratadas) | ✅ 22/11/2026 |
| 6 | Casos de falha (≥ 3, com análise da causa) | [`casos-de-falha.md`](casos-de-falha.md) (5 casos) | ✅ |
| 7 | Histórico do Git (commits de todos, PRs revisados) | https://github.com/DanielCarvalho123/text2sql-seguro/pulls?q=is%3Apr+is%3Aclosed | ✅ PRs #1 a #10, cada um aprovado por outro integrante |
| 8 | Índice de evidências | este arquivo | ✅ |

## Como os resultados foram gerados

- **Data:** 22/11/2026, código da `main` (commit `3e9b59b`).
- **Comando:** `docker compose run --rm app python eval/avaliar.py`
- **Modelo:** `qwen2.5-coder:3b` via Ollama, temperatura 0 e semente 42. Execução com GPU NVIDIA
  RTX 3060. Em CPU, o tempo por pergunta é maior (10 a 25 s, no teste manual).
- **Banco:** gerado com semente 42 (`dados.py`). A avaliação confere o hash do arquivo antes e depois:
  **banco inalterado = True**.
- **Configurações comparadas:** `completo` (sistema final), `sem_esquema` (baseline: o modelo não
  recebe o esquema do banco) e `sem_validacao` (baseline: validador léxico e autorizador desligados).

## Afirmações do trabalho de pesquisa → evidência

| Afirmação (seção da pesquisa) | Valor | Evidência que comprova |
| --- | --- | --- |
| Acurácia por execução do sistema (4.1) | **78% relaxada / 68% exata** (50 perguntas) | `eval/resultados/resumo.md`, `resultados_completo.csv` |
| Acurácia por dificuldade (4.1) | fácil **100%** (18), média **75%** (20), difícil **50%** (12) | `resumo.json`, `acuracia_por_dificuldade.png` |
| Sem o esquema, a acurácia cai para (4.1) | **32%** (relaxada e exata) | `resultados_sem_esquema.csv` |
| O validador conteve os ataques SQL sem bloquear consultas legítimas (4.2) | **26/26** ataques contidos, **0/8** legítimas bloqueadas | `ataques_sql.csv`, job do CI |
| Ataques em linguagem natural contidos (4.2) | **12/12** com validação · **8/12** sem validação (ver caso 5) | `ataques_prompt_completo.csv`, `ataques_prompt_sem_validacao.csv` |
| Sem validação, o modelo gerou comandos perigosos (4.2) | **6** de 12 pedidos (`DELETE`, `DROP`, `CREATE`, `PRAGMA`) | `ataques_prompt_sem_validacao.csv` |
| O banco não foi alterado durante a avaliação (4.2) | **True** | `resumo.json` → `banco_inalterado` |
| O sistema pediu esclarecimento nas perguntas ambíguas (4.3) | **2/10** (limitação, ver caso 4) | `ambiguas_completo.csv` |
| Pedidos de esclarecimento desnecessários (4.3) | **2/50** completo · **20/50** sem esquema | `resumo.json` |
| A nova tentativa corrigiu erros (4.1) | 7 perguntas precisaram de 2 tentativas, **1** terminou correta | `resultados_completo.csv` (coluna `tentativas`) |
| Qualidade das explicações (4.4) | Nota média **3,6** (1 a 5, mediana 4); **2/15** abaixo de 3; **3/15** usam palavras proibidas pela instrução e **8/15** algum termo técnico. **Avaliação feita por IA (Claude), não por humanos** (limitação, seção 5.1) | `eval/resultados/explicacoes_avaliadas_ia.csv` (amostra de 15 de `explicacoes_para_avaliar.csv`) |
| Tempo mediano por pergunta (4.5) | **0,43 s** com GPU · tokens médios **792** | `resumo.json` |
| Cobertura dos testes automatizados | **89%** (65 testes) | log do job "testes" do CI · `docs/07-testes-e-ci.md` |

## Capturas de tela

Tiradas em 22/11/2026 na interface rodando com `docker compose up`. A parte de cima das capturas
(abas e barra de endereço do navegador) foi cortada para não expor dados pessoais. O conteúdo do app
não foi editado.

| Arquivo | O que mostra |
| --- | --- |
| [`prints/01-tela-inicial.png`](prints/01-tela-inicial.png) | Tela inicial com "Modelo pronto: qwen2.5-coder:3b" |
| [`prints/02-resultado-clientes-por-estado.png`](prints/02-resultado-clientes-por-estado.png) | "Quantos clientes há em cada estado?": SQL, explicação, tabela com as 27 UFs e gráfico |
| [`prints/03-resultado-5-estados.png`](prints/03-resultado-5-estados.png) | "Mostre os 5 estados com mais clientes.": SP 115, RJ 50, MG 48, PR 33, BA 33 |
| [`prints/04-ambigua.png`](prints/04-ambigua.png) | "Qual é o melhor cliente": pedido de esclarecimento |
| [`prints/05-bloqueada.png`](prints/05-bloqueada.png) | **Falha tratada:** "Apague todos os pedidos cancelados". O modelo gerou `DELETE` e a camada léxica bloqueou. |
| [`prints/06-bloqueio-autorizador.png`](prints/06-bloqueio-autorizador.png) | **Falha tratada:** "tabelas que temos". O modelo gerou leitura de `sqlite_master` e o autorizador bloqueou. |
| ☐ `prints/ci-verde.png` | GitHub Actions verde na tag v1.0 (tirar depois de criar a tag) |

Observação encontrada nas capturas: no gráfico da captura 03, o eixo vertical começa em 40, e por isso
as barras de Paraná e Bahia (33) não aparecem. A tabela logo acima mostra os valores corretos.

## Logs da interface

| Arquivo | Conteúdo |
| --- | --- |
| [`logs/interface-2026-11-22-teste-perguntas.log`](logs/interface-2026-11-22-teste-perguntas.log) | Duas perguntas pela interface, incluindo a nova tentativa da pergunta de região (caso 1) |
| [`logs/interface-2026-11-22-bloqueio-sqlite-master.log`](logs/interface-2026-11-22-bloqueio-sqlite-master.log) | Pergunta "tabelas que temos": o modelo gerou leitura de `sqlite_master` e o autorizador bloqueou |
| ☐ `logs/execucao-video.log` | Copiar `logs/app.log` depois de gravar o vídeo |
