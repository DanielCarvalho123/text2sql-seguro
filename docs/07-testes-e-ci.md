# 7. Testes e integração contínua

## O que é testado

| Arquivo | Cobre |
| --- | --- |
| `tests/test_dados.py` | Tamanho e determinismo do banco, coerência das datas, esquema do prompt |
| `tests/test_validador.py` | Ataques léxicos, autorizador, limite de custo, limite de linhas, somente leitura, falsos positivos |
| `tests/test_gerador.py` | Extração de SQL, `AMBIGUA`, `RECUSA`, prompt com e sem esquema, prompt de correção |
| `tests/test_pipeline.py` | Fluxo completo com modelo simulado: sucesso, nova tentativa, bloqueio, ambiguidade, modelo fora do ar |
| `tests/test_avaliacao.py` | Comparação exata e relaxada; catálogo inteiro de ataques SQL |

Os testes **não precisam do Ollama**: o modelo é substituído por um falso (`tests/conftest.py`).

## Como executar

```bash
pip install -r requirements-dev.txt
ruff check .
pytest --cov
```

## Integração contínua (`.github/workflows/ci.yml`)

A cada push na `main`, pull request ou tag `v*`:

1. `ruff check .` (lint);
2. `pytest --cov` (testes com cobertura);
3. `python eval/avaliar.py --somente-ataques-sql` (catálogo de ataques; falha se algum passar);
4. `docker build` (garante que a imagem constrói).

A cobertura aparece no log do job "testes". **Atualizar aqui com o número da execução da tag v1.0:** ___%.
