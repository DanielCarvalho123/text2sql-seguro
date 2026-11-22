# 1. Visão geral e arquitetura

## Componentes

```mermaid
flowchart TB
    subgraph Docker Compose
        subgraph app [container app]
            UI[app.py<br/>Streamlit]
            PIPE[pipeline.py]
            GER[gerador.py]
            VAL[validador.py]
            EXP[explicador.py]
            LLM[llm.py]
            DB[(data/loja.db<br/>SQLite)]
        end
        OLL[container ollama<br/>qwen2.5-coder:3b]
        PULL[container baixar-modelo<br/>roda uma vez]
    end
    UI --> PIPE --> GER --> LLM -->|HTTP /api/generate| OLL
    PIPE --> VAL --> DB
    PIPE --> EXP --> LLM
    PULL -.->|ollama pull| OLL
```

| Módulo | Responsabilidade |
| --- | --- |
| `dados.py` | Cria o banco (UFs públicas + loja sintética, semente 42) e fornece o esquema do prompt |
| `gerador.py` | Monta o prompt (regras, esquema, dicas do domínio) e interpreta a resposta: SQL, `AMBIGUA:` ou `RECUSA:` |
| `llm.py` | Cliente HTTP do Ollama, com temperatura 0 e contagem de tokens |
| `validador.py` | Defesa em 5 camadas e execução com limite de linhas e de custo |
| `explicador.py` | Explicação em linguagem simples (modelo, com reserva baseada em regras) |
| `pipeline.py` | Orquestra o fluxo, faz 1 nova tentativa em caso de erro de execução e grava logs |
| `avaliacao.py` | Comparação de resultados (acurácia exata e relaxada) |
| `logs.py` | Logs JSON por linha com data e hora |

## Fluxo de dados

```mermaid
sequenceDiagram
    participant U as Usuário
    participant P as Pipeline
    participant M as Modelo (Ollama)
    participant V as Validador
    participant B as SQLite (somente leitura)
    U->>P: pergunta em português
    P->>M: regras + esquema + pergunta
    M-->>P: ```sql ...``` / AMBIGUA: ... / RECUSA: ...
    alt ambígua ou recusa
        P-->>U: pergunta de esclarecimento ou recusa
    else SQL
        P->>V: validar (léxico)
        V->>B: executar com autorizador, limite de custo e de linhas
        alt bloqueada
            V-->>P: ConsultaBloqueada (camada, motivo)
            P-->>U: aviso de bloqueio
        else erro do banco (ex.: coluna inexistente)
            P->>M: nova tentativa com a mensagem de erro (máx. 2)
        else ok
            B-->>P: linhas
            P->>M: pedir explicação
            P-->>U: SQL, explicação, tabela e gráfico
        end
    end
```
