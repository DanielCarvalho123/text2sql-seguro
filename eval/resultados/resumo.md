# Resumo da avaliação (2026-11-22T17:50:37, modelo `qwen2.5-coder:3b`)

## Validador contra SQL malicioso (sem modelo)

| Ataques contidos | Consultas legítimas bloqueadas por engano |
| --- | --- |
| 26/26 | 0/8 |

## Comparação entre configurações

| Configuração | Acurácia exata | Acurácia relaxada | Fácil | Média | Difícil | Ambíguas detectadas | Ataques contidos | Modelo gerou SQL perigoso | Tempo mediano (s) | Tokens médios |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| completo | 68.0% | 78.0% | 100.0% | 75.0% | 50.0% | 2/10 | 12/12 | 6 | 0.43 | 792 |
| sem_esquema | 32.0% | 32.0% | 66.7% | 15.0% | 8.3% | 10/10 | 12/12 | 6 | 0.48 | 494 |
| sem_validacao | 66.0% | 76.0% | 100.0% | 75.0% | 41.7% | 2/10 | 9/12 | 6 | 0.4 | 809 |

Banco inalterado após a avaliação: **True**
