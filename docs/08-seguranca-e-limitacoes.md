# 8. Segurança, privacidade e limitações

## Riscos tratados

| Risco | Tratamento |
| --- | --- |
| SQL destrutivo gerado pelo modelo | 5 camadas ([ADR-002](decisoes/ADR-002-defesa-em-camadas.md)) |
| Injeção de prompt ("ignore as instruções...") | O modelo pode obedecer, mas o validador bloqueia o SQL resultante |
| Leitura de metadados internos | Autorizador nega `sqlite_*` e `pragma_*` |
| Consulta cara (negação de serviço) | Limite de instruções e de linhas |
| Vazamento de segredos | Não há chaves; `.env` no `.gitignore` |
| Container com privilégios | A aplicação roda com usuário sem privilégios |

## O que o sistema **não** faz

- Não altera dados (por projeto).
- Não garante que a resposta está certa: a consulta pode ser válida e segura, mas responder outra
  pergunta. Por isso o SQL e a explicação são sempre mostrados.
- Não autentica usuários nem controla acesso por linha/coluna.
- Não funciona com outros bancos sem adaptar o esquema e as dicas do prompt.
- Não foi testado com bases grandes nem com dados reais "sujos".

## Privacidade e LGPD

- Apenas dados públicos (UFs) e sintéticos; nenhum dado pessoal real em dados, prompts ou logs.
- O modelo roda localmente: as perguntas não saem da máquina.
- Os logs guardam perguntas e SQL. Em uso real com dados pessoais, seria preciso definir prazo de
  retenção, anonimizar os logs e informar o titular.

## Limitações conhecidas

- Modelos pequenos erram junções com várias tabelas e filtros implícitos (ex.: excluir cancelados).
- A detecção de ambiguidade depende do modelo e pode pedir esclarecimento sem necessidade.
- O limite de custo é medido em instruções do SQLite, não em tempo de relógio.
- A validação léxica pode bloquear consultas legítimas que usem nomes de coluna iguais a comandos
  (ex.: uma coluna chamada `update` sem aspas).
