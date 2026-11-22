# ADR-001: SQLite como banco de dados

**Contexto.** A stack sugerida cita PostgreSQL ou DuckDB e SQLGlot. Precisávamos de um banco que
rodasse sem servidor, sem custo, e que permitisse impedir escrita de forma confiável.

**Decisão.** Usar SQLite, que já vem no Python. Ele oferece (1) conexão somente leitura
(`mode=ro`), (2) um *autorizador* chamado pelo próprio motor para cada operação durante a
compilação da consulta e (3) um *progress handler* que interrompe consultas caras.

**Alternativas descartadas.**
- *DuckDB:* ótimo para análise, mas sem autorizador equivalente; a segurança dependeria só da análise do texto.
- *PostgreSQL:* permitiria um usuário somente leitura, mas exige mais um container e mais configuração.
- *SQLGlot para validar:* a análise sintática continua útil, mas o bloqueio feito pelo motor é mais
  difícil de contornar do que qualquer análise de texto. Fica como trabalho futuro somar as duas.

**Consequências.** Dialeto SQLite (datas como texto, `strftime`). Volume de dados pequeno, suficiente
para o objetivo do trabalho.
