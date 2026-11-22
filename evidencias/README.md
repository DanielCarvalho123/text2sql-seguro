# Índice de evidências de funcionamento

> Todas as evidências devem sair da execução real do projeto na tag `v1.0`.
> Preencher os campos marcados com `___` **depois** de gerar cada evidência. Não inventar números.

## Evidências obrigatórias

| # | Evidência | Arquivo / link | Status |
| --- | --- | --- | --- |
| 1 | Vídeo (3 a 5 min, tela inteira, `docker compose up` do zero + fluxo principal) | `videos/demo.mp4` ou link: ___ | ☐ |
| 2 | Execução verde do CI na tag `v1.0` | link: ___ · captura: `prints/ci-verde.png` | ☐ |
| 3 | Resultados da avaliação | `../eval/resultados/` · comando: `docker compose run --rm app python eval/avaliar.py` | ☐ |
| 4 | Logs de uma execução completa | `logs/execucao-completa.log` (copiado de `logs/app.log`) | ☐ |
| 5 | Capturas de tela (≥ 5, incluindo uma falha tratada) | `prints/` | ☐ |
| 6 | Casos de falha (≥ 3, com análise da causa) | [`casos-de-falha.md`](casos-de-falha.md) | ☐ |
| 7 | Histórico do Git (commits de todos, PRs revisados) | link: https://github.com/USUARIO/text2sql-seguro/pulls?q=is%3Apr | ☐ |

## Afirmações do trabalho de pesquisa → evidência

| Afirmação (seção da pesquisa) | Evidência que comprova |
| --- | --- |
| "O sistema atinge ___% de acurácia por execução" (4.1) | `eval/resultados/resumo.md`, `resultados_completo.csv` |
| "Sem o esquema, a acurácia cai para ___%" (4.1) | `resultados_sem_esquema.csv` |
| "O validador conteve ___/26 ataques SQL sem bloquear consultas legítimas" (4.2) | `ataques_sql.csv`, job do CI |
| "O banco não foi alterado durante a avaliação" (4.2) | `resumo.json` → `banco_inalterado` |
| "Sem validação, o modelo gerou ___ comandos perigosos" (4.2) | `ataques_prompt_sem_validacao.csv` |
| "O sistema pediu esclarecimento em ___/10 perguntas ambíguas" (4.3) | `ambiguas_completo.csv` |
| "As explicações receberam nota média ___" (4.4) | `explicacoes_para_avaliar.csv` (com notas) |
| "Tempo mediano de ___ s por pergunta" (4.5) | `resumo.json` |

## Capturas sugeridas

1. `01-tela-inicial.png` — modelo pronto
2. `02-resultado.png` — pergunta com tabela e gráfico
3. `03-ambigua.png` — pedido de esclarecimento
4. `04-bloqueada.png` — "Apague todos os pedidos cancelados" bloqueado (falha tratada)
5. `05-erro-corrigido.png` — resposta com 2 tentativas
6. `ci-verde.png` — GitHub Actions verde na tag v1.0
