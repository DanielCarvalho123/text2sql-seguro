# 4. Referência da interface e dos módulos

O projeto não expõe API HTTP própria; a interface é a aplicação Streamlit e os módulos Python.

## Interface (http://localhost:8501)

| Elemento | Função |
| --- | --- |
| Campo **Pergunta** e botão **Perguntar** | Envia a pergunta |
| Lista **Exemplos** | Preenche perguntas prontas (incluindo uma ambígua e uma maliciosa) |
| Barra lateral | Estado do modelo, limite de linhas, esquema do banco |
| Cartão de resposta | SQL, explicação, tabela, gráfico (quando há 1 coluna de rótulo e 1 numérica), plano de execução, tempo, tentativas e tokens |

Estados possíveis de uma resposta:

| Status | Significado |
| --- | --- |
| `ok` | Consulta executada |
| `ambigua` | O modelo pediu esclarecimento |
| `recusada` | O modelo recusou um pedido de alteração de dados |
| `bloqueada` | O validador bloqueou (camada `léxica`, `autorizador` ou `custo`) |
| `erro` | Modelo indisponível ou consulta inválida após 2 tentativas |

## Uso como biblioteca

```python
from text2sql.llm import ClienteOllama
from text2sql.pipeline import Assistente

assistente = Assistente(ClienteOllama("http://localhost:11434", "qwen2.5-coder:3b"), "data/loja.db")
r = assistente.responder("Quantos clientes há em cada região?")
print(r.status, r.sql, r.linhas, r.explicacao)
```

| Função | Descrição |
| --- | --- |
| `dados.gerar_banco(caminho, semente=42)` | Cria o banco de demonstração |
| `validador.validar(sql)` | Validação léxica; levanta `ConsultaBloqueada` |
| `validador.executar(db, sql, limite_linhas, limite_instrucoes, validar_sql=True)` | Executa com todas as camadas |
| `gerador.montar_prompt(pergunta, esquema, sql_anterior, erro_anterior)` | Monta o prompt |
| `gerador.extrair_sql(texto)` | Interpreta a resposta do modelo |
| `explicador.explicar(cliente, pergunta, sql)` | Explicação (modelo ou regras) |
| `avaliacao.igual_exato / igual_relaxado` | Comparação de resultados |

## Linha de comando

| Comando | Função |
| --- | --- |
| `python -m text2sql.dados data/loja.db` | Recria o banco |
| `python eval/avaliar.py [--limite N] [--configs ...]` | Avaliação experimental |
| `python eval/avaliar.py --somente-ataques-sql` | Só o catálogo de ataques (sem modelo) |
