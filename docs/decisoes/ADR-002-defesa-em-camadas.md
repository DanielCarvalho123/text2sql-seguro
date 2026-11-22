# ADR-002: Validação em camadas

**Contexto.** O SQL vem de um modelo que pode errar ou ser manipulado por injeção de prompt.

**Decisão.** Cinco camadas independentes; qualquer uma bloqueia sozinha:

1. **Léxica:** uma instrução, começando com `SELECT`/`WITH`, sem palavras-chave de escrita. Strings e
   comentários são removidos antes da busca (`esqueleto()`), para evitar falsos positivos
   (`WHERE nome = 'DROP'`) e truques (`DR/**/OP`).
2. **Autorizador do SQLite:** só permite `SELECT`, `READ`, `FUNCTION` e `RECURSIVE`; nega tabelas
   internas (`sqlite_*`, `pragma_*`) e funções como `load_extension`.
3. **Conexão somente leitura.**
4. **Limite de custo:** interrompe após N instruções da máquina virtual (padrão 20 milhões, ~0,2 s).
5. **Limite de linhas** (padrão 1000).

**Alternativas descartadas.** Lista de comandos permitidos só por expressão regular (fácil de
contornar); executar em transação e fazer *rollback* (a escrita chegaria a acontecer).

**Consequências.** Consultas legítimas muito pesadas também são interrompidas; o limite é configurável.
