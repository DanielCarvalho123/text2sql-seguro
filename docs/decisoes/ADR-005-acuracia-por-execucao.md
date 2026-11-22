# ADR-005: Métrica de acurácia por execução

**Contexto.** Duas consultas diferentes podem ser igualmente corretas; comparar o texto do SQL seria
injusto.

**Decisão.** Comparar o **resultado** da consulta gerada com o da consulta de referência, ignorando a
ordem das linhas e arredondando números para 2 casas. Duas variantes:
- **exata:** mesmas colunas e linhas;
- **relaxada:** aceita colunas extras (ex.: devolver nome e preço quando só o nome foi pedido).

**Consequências.** Arredondamentos diferentes do pedido (ex.: 1 casa decimal) contam como erro. As
duas variantes são relatadas separadamente.
