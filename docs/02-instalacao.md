# 2. Instalação e execução

## Pré-requisitos

| Item | Versão | Observação |
| --- | --- | --- |
| Docker Desktop (ou Docker Engine + Compose v2) | recente | Único requisito para rodar |
| Memória livre | ~4 GB | Modelo de 3B parâmetros em CPU |
| Disco | ~4 GB | Imagem do Ollama + modelo |
| Python 3.11+ | opcional | Só para rodar os testes fora do Docker |
| Ollama | opcional | Só para rodar sem Docker |

## Com Docker (recomendado)

```bash
docker compose up
```

1. O serviço `ollama` sobe.
2. O serviço `baixar-modelo` baixa o modelo (só na primeira vez) e termina.
3. O serviço `app` constrói a imagem, gera o banco e abre a interface em http://localhost:8501.

Para trocar de modelo: `MODELO=qwen2.5-coder:7b docker compose up`.

Para parar: `Ctrl+C` e depois `docker compose down`. O modelo fica guardado no volume `ollama`.

## Sem Docker (desenvolvimento)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
ollama pull qwen2.5-coder:3b     # com o Ollama instalado e aberto
PYTHONPATH=src python -m text2sql.dados data/loja.db
streamlit run src/app.py
```

No Windows (PowerShell), troque `PYTHONPATH=src` por `$env:PYTHONPATH="src";` antes do comando.

## Variáveis de ambiente

Ver a tabela no [README](../README.md#variáveis-de-ambiente-opcionais) e o arquivo `.env.example`.
Não há chaves de API. O arquivo `.env` está no `.gitignore`.
