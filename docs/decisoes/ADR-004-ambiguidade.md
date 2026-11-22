# ADR-004: Tratamento de perguntas ambíguas

**Contexto.** O tema pede que o sistema pergunte quando a pergunta é ambígua.

**Decisão.** O prompt instrui o modelo a responder `AMBIGUA: <pergunta>` em vez de SQL. O pipeline
reconhece o prefixo e devolve a pergunta de esclarecimento ao usuário.

**Alternativas descartadas.** Um classificador separado (mais uma chamada ao modelo por pergunta,
dobrando a latência); regras fixas por palavras como "melhor" (não generalizam).

**Consequências.** O modelo pode pedir esclarecimento sem necessidade. Por isso a avaliação mede as
duas coisas: perguntas ambíguas detectadas e esclarecimentos desnecessários nas 50 perguntas normais.
