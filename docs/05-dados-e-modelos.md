# 5. Dados e modelos

## Conjunto de dados

| Tabela | Linhas | Origem | Licença |
| --- | --- | --- | --- |
| `estados` | 27 | Pública: siglas, nomes, regiões e capitais das UFs (IBGE) | Informação pública |
| `clientes` | 500 | Sintética (nomes fictícios combinados aleatoriamente) | Gerada pelo projeto (MIT) |
| `produtos` | 38 | Sintética (catálogo inventado) | Gerada pelo projeto (MIT) |
| `pedidos` | 3.000 | Sintética, datas de 2024 a 2025 | Gerada pelo projeto (MIT) |
| `itens_pedido` | ~7.500 | Sintética, 1 a 4 itens por pedido, descontos de 10% e 15% | Gerada pelo projeto (MIT) |

**Tratamento.** Gerado por `src/text2sql/dados.py` com semente 42; o mesmo banco é recriado em
qualquer máquina. Distribuição de clientes por UF com pesos maiores nos estados mais populosos.
Status dos pedidos: ~70% entregue, 12% cancelado, 10% enviado, 8% pago.

**LGPD.** Nenhum dado pessoal real. Nomes de clientes são combinações de listas de nomes comuns e não
correspondem a pessoas.

### Ficha do conjunto de dados

| Campo | Valor |
| --- | --- |
| Finalidade | Demonstrar e avaliar text-to-SQL seguro |
| Limitações | Dados pequenos e regulares; não representam a sujeira de bases reais (nulos, grafias diferentes) |
| Vieses | Distribuição por UF definida à mão; não reflete população real |
| Atualização | Estático; regenerado a cada build |

## Modelo

### Ficha do modelo

| Campo | Valor |
| --- | --- |
| Modelo | Qwen2.5-Coder 3B Instruct (`qwen2.5-coder:3b` no Ollama) |
| Autor | Equipe Qwen (Alibaba Cloud) |
| Licença | Qwen Research License (uso não comercial) |
| Parâmetros | ~3,1 bilhões, quantizado pelo Ollama |
| Execução | Local, CPU ou GPU, temperatura 0, semente 42 |
| Uso no projeto | Gerar SQL, detectar ambiguidade, explicar consultas |
| Riscos | Gera SQL plausível porém errado; pode obedecer a injeções de prompt (mitigado pelo validador) |
| Não usar para | Decisões sem conferência humana; bancos com dados pessoais sem controles adicionais |

## Conjuntos de avaliação

| Arquivo | Conteúdo |
| --- | --- |
| `eval/perguntas.jsonl` | 50 perguntas (18 fáceis, 20 médias, 12 difíceis) com SQL de referência, escritas antes da avaliação do modelo |
| `eval/ambiguas.jsonl` | 10 perguntas ambíguas |
| `eval/ataques_prompt.jsonl` | 12 pedidos maliciosos em linguagem natural |
| `eval/ataques_sql.jsonl` | 34 consultas SQL (26 ataques e 8 legítimas) |
