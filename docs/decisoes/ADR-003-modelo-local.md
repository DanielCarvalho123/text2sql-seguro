# ADR-003: Modelo local Qwen2.5-Coder 3B via Ollama

**Contexto.** Regra de custo zero; os integrantes usam notebooks sem GPU dedicada.

**Decisão.** `qwen2.5-coder:3b` no Ollama, com temperatura 0 e semente fixa, para reprodutibilidade.

**Alternativas descartadas.**
- *APIs pagas:* proibidas pela regra de custo.
- *Modelos de 7B ou mais:* melhores, porém 2 a 3 vezes mais lentos em CPU. Podem ser usados trocando
  a variável `MODELO`, o que permite comparar tamanhos na avaliação.
- *Modelos de propósito geral (ex.: llama3.2:3b):* em geral piores em SQL do que modelos de código.

**Consequências.** Licença Qwen Research (uso não comercial), compatível com o trabalho acadêmico.
