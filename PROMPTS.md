# Registro de uso de IA na programação

Regra da disciplina: pelo menos 10 interações relevantes, cada uma com o prompt, um resumo da
resposta e o que foi **aceito**, **corrigido** ou **descartado**, com o motivo.

As interações 1 a 6 aconteceram de fato na conversa com o Claude que gerou a primeira versão do
projeto. **O grupo deve completar as colunas de decisão depois de revisar cada parte** e acrescentar
as próximas interações (revisões, correções, dúvidas) conforme o trabalho avança. Não registrem
interações que não aconteceram.

---

## 1. Escolha do tema

- **Ferramenta:** Claude
- **Prompt (resumo):** enviamos o enunciado completo e pedimos o tema mais simples de realizar, a
  estrutura do projeto e o passo a passo para criar o repositório.
- **Resposta (resumo):** recomendou o Tema 9 (text-to-SQL seguro) por não precisar de GPU, ter
  avaliação objetiva (acurácia por execução) e baseline simples (modelo sem esquema). Alertou que o
  tema é atribuído pelo professor e que o prazo era curto.
- **Decisão:** aceito. Motivo: _(completar)_

## 2. Geração do projeto completo

- **Ferramenta:** Claude
- **Prompt (resumo):** pedimos o projeto completo, dividido depois em commits entre os integrantes.
- **Resposta (resumo):** gerou o código em `src/`, testes, Docker, CI, avaliação e documentação.
- **Decisão:** _(aceito / corrigido — descrever o que o grupo revisou e mudou)_

## 3. Troca de DuckDB por SQLite

- **Ferramenta:** Claude
- **Contexto:** a stack sugerida cita DuckDB e SQLGlot.
- **Resposta (resumo):** a IA usou SQLite (biblioteca padrão do Python) porque o autorizador do
  SQLite permite bloquear operações dentro do próprio motor, e a conexão `mode=ro` impede escrita.
  Ver [ADR-001](docs/decisoes/ADR-001-sqlite.md).
- **Decisão:** _(completar)_

## 4. Erro da IA: CTEs bloqueadas pelo autorizador

- **Ferramenta:** Claude
- **O que aconteceu:** a primeira versão do autorizador só permitia ler as 5 tabelas conhecidas. O
  teste manual mostrou que consultas com `WITH t AS (...)` eram bloqueadas, porque o SQLite também
  gera eventos de leitura para nomes de CTE.
- **Correção:** a regra virou uma lista de prefixos proibidos (`sqlite_`, `pragma_`).
- **Decisão:** corrigido. Teste: `test_consultas_legitimas_nao_sao_bloqueadas`.

## 5. Erro da IA: comandos perigosos sem bloco de código não eram extraídos

- **Ferramenta:** Claude
- **O que aconteceu:** quando o modelo respondia só `DELETE FROM pedidos`, sem bloco ```sql, o
  extrator não reconhecia SQL e o caso aparecia como "erro", escondendo que o modelo gerou um comando
  destrutivo.
- **Correção:** o extrator passou a reconhecer qualquer comando SQL no início de uma linha, para que o
  validador bloqueie e registre o bloqueio.
- **Decisão:** corrigido. Teste: `test_extrai_comando_perigoso_para_o_validador_bloquear`.

## 6. Empate no conjunto de teste

- **Ferramenta:** Claude
- **O que aconteceu:** a pergunta "5 produtos mais vendidos" tinha empate no 5º lugar (dois produtos
  com 384 unidades), o que tornaria a resposta correta ambígua.
- **Correção:** a pergunta passou a pedir os 4 mais vendidos.
- **Decisão:** corrigido.

## 7. _(próxima interação do grupo)_

- **Ferramenta:**
- **Prompt:**
- **Resposta (resumo):**
- **Decisão e motivo:**

## 8. _(próxima interação do grupo)_

## 9. _(próxima interação do grupo)_

## 10. _(próxima interação do grupo)_
