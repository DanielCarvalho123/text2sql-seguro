# 6. Guia de avaliação

## Reproduzir com um comando

```bash
docker compose up -d                                  # sobe o Ollama e baixa o modelo
docker compose run --rm app python eval/avaliar.py    # roda tudo (~30 a 90 min em CPU)
```

Rodada rápida para testar: `docker compose run --rm app python eval/avaliar.py --limite 5 --configs completo`.

## O que é medido

| Métrica | Como |
| --- | --- |
| Acurácia por execução (exata e relaxada) | Resultado da consulta gerada igual ao da referência ([ADR-005](decisoes/ADR-005-acuracia-por-execucao.md)) |
| Acurácia por dificuldade | Fácil, média e difícil |
| Baseline 1: `sem_esquema` | Mesmo modelo, sem receber o esquema |
| Baseline 2: `sem_validacao` | Mesmo modelo, sem validador léxico e sem autorizador (só a conexão somente leitura) |
| Ambiguidade | Perguntas ambíguas em que o sistema pediu esclarecimento e esclarecimentos desnecessários nas 50 normais |
| Ataques SQL | Catálogo contra o validador: ataques contidos e consultas legítimas bloqueadas por engano |
| Ataques por prompt | O sistema recusou ou bloqueou? O modelo chegou a gerar SQL perigoso? |
| Integridade | Hash SHA-256 do banco antes e depois (deve ser igual) |
| Custo | Tempo mediano e tokens médios por pergunta |
| Explicações | `explicacoes_para_avaliar.csv`: dois integrantes dão nota de 1 a 5 a 15 explicações |

## Arquivos gerados em `eval/resultados/`

`resumo.md`, `resumo.json`, `resultados_<config>.csv`, `erros_<config>.csv`, `ambiguas_<config>.csv`,
`ataques_prompt_<config>.csv`, `ataques_sql.csv`, `explicacoes_para_avaliar.csv`,
`acuracia_por_dificuldade.png`, `avaliacao.log`.

## Análise de erros

Use `erros_completo.csv` para escolher pelo menos 3 casos de falha e classificar a causa (coluna
errada, filtro de status esquecido, formato de data, arredondamento, junção errada). Registre a
análise em `evidencias/casos-de-falha.md`.

Os números variam com o hardware só no tempo; com temperatura 0 e semente fixa, as respostas tendem a
se repetir, mas versões diferentes do Ollama ou do modelo podem mudar resultados. Registre a versão
(`docker compose exec ollama ollama --version`).
