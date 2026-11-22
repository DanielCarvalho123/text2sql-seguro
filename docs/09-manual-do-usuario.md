# 9. Manual do usuário

> Substituir os marcadores `![...]` pelas capturas reais tiradas da aplicação (pasta `evidencias/prints/`).

## 1. Abrir

Rode `docker compose up` e acesse http://localhost:8501. Espere a barra lateral mostrar
**"Modelo pronto"**.

![Tela inicial](../evidencias/prints/01-tela-inicial.png)

## 2. Fazer uma pergunta

Digite em português, por exemplo *"Quantos clientes há em cada região?"*, e clique em **Perguntar**.

![Pergunta com resultado](../evidencias/prints/02-resultado.png)

A resposta mostra:
- a **consulta SQL** gerada;
- **o que a consulta faz**, em linguagem simples;
- a **tabela** de resultados e, quando faz sentido, um **gráfico**;
- tempo, número de tentativas e tokens.

## 3. Quando o assistente pede esclarecimento

Para perguntas vagas, como *"Qual é o melhor cliente?"*, o assistente pergunta o critério. Reformule,
por exemplo: *"Qual cliente mais gastou em pedidos não cancelados?"*.

![Pedido de esclarecimento](../evidencias/prints/03-ambigua.png)

## 4. Quando a consulta é bloqueada

Pedidos para apagar ou alterar dados são recusados ou bloqueados, com o motivo.

![Consulta bloqueada](../evidencias/prints/04-bloqueada.png)

## 5. Dicas

- Seja específico sobre período ("em 2025") e status ("pedidos não cancelados").
- Confira o SQL e a explicação: o assistente pode errar.
- Abra **Esquema do banco** na barra lateral para ver as tabelas disponíveis.
- Abra **Plano de execução** para ver como o banco executou a consulta.
