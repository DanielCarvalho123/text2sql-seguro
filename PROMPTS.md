# Registro de uso de IA na programação

Regra da disciplina: pelo menos 10 interações relevantes, cada uma com o prompt, um resumo da
resposta e o que foi **aceito**, **corrigido** ou **descartado**, com o motivo.

As interações 1 a 6 aconteceram na conversa com o Claude que gerou a primeira versão do projeto. As
interações 7 a 15 aconteceram na conversa usada para organizar os pull requests, testar o sistema,
rodar a avaliação e montar as evidências. Em todas, a decisão registrada é a do grupo.

---

## 1. Escolha do tema

- **Ferramenta:** Claude
- **Prompt (resumo):** enviamos o enunciado completo e pedimos o tema mais simples de realizar, a
  estrutura do projeto e o passo a passo para criar o repositório.
- **Resposta (resumo):** recomendou o Tema 9 (text-to-SQL seguro) por não precisar de GPU, ter
  avaliação objetiva (acurácia por execução) e baseline simples (modelo sem esquema). Alertou que o
  tema é atribuído pelo professor e que o prazo era curto.
- **Decisão:** aceito. Motivo: o Tema 9 foi a primeira opção indicada pelo grupo e o professor o
  atribuiu. Pesou também a avaliação objetiva (acurácia por execução), que permite comparar com um
  baseline sem depender de opinião.

## 2. Geração do projeto completo

- **Ferramenta:** Claude
- **Prompt (resumo):** pedimos o projeto completo, dividido depois em commits entre os integrantes.
- **Resposta (resumo):** gerou o código em `src/`, testes, Docker, CI, avaliação e documentação.
- **Decisão:** aceito, com revisão do grupo via pull request. O código foi dividido em 9 PRs, cada um
  revisado e aprovado por outro integrante, e só entrou na `main` com o CI verde. As correções feitas
  durante o desenvolvimento estão nas interações 4, 5, 6 e 9.

## 3. Troca de DuckDB por SQLite

- **Ferramenta:** Claude
- **Contexto:** a stack sugerida cita DuckDB e SQLGlot.
- **Resposta (resumo):** a IA usou SQLite (biblioteca padrão do Python) porque o autorizador do
  SQLite permite bloquear operações dentro do próprio motor, e a conexão `mode=ro` impede escrita.
  Ver [ADR-001](docs/decisoes/ADR-001-sqlite.md).
- **Decisão:** aceito. Motivo: o SQLite tem o autorizador, que bloqueia operações dentro do próprio
  motor, e abre em modo somente leitura (`mode=ro`). Isso deixa a defesa em camadas mais forte do que só
  analisar o texto da consulta. O SQLGlot ficou como trabalho futuro, porque o bloqueio feito pelo motor é
  mais difícil de contornar do que a análise do texto. Ver ADR-001.

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

## 7. Organização dos commits e teste das 9 etapas

- **Ferramenta:** Claude (Claude Code, aplicativo desktop)
- **Prompt (resumo):** enviamos o pacote com os 9 PRs e pedimos para executar as etapas do
  Integrante 1, criar o repositório e informar quais dados eram necessários.
- **Resposta (resumo):** aplicou os 9 PRs em sequência e rodou `ruff` e `pytest` depois de cada um
  (4 → 35 → 47 → 47 → 57 → 57 → 65 → 65 → 65 testes). Confirmou que o resultado final era idêntico ao
  projeto completo. Pediu o link do repositório e enviou a branch do PR #1 montada sobre a `main`
  que já existia no GitHub (só o `.gitignore` foi substituído).
- **Decisão:** aceito. Motivo: a verificação etapa por etapa garantiu que cada PR passaria no CI
  sozinho, condição para a `main` protegida aceitar o merge.

## 8. Pedido descartado: commits no nome dos outros integrantes

- **Ferramenta:** Claude
- **Prompt (resumo):** pedimos que a IA fizesse também os commits dos outros integrantes e, depois,
  perguntamos se ela poderia entrar nas contas deles com usuário e senha.
- **Resposta (resumo):** recusou. Fazer commits com o nome e o e-mail de outra pessoa falsificaria a
  autoria, que é avaliada (critério 7 da rubrica e defesa oral), e a IA não usa senha de terceiros.
  Recomendou não compartilhar senhas e propôs um script para cada integrante enviar o próprio PR.
- **Decisão:** a ideia original foi **descartada** e aceitamos a alternativa. Motivo: o histórico do
  Git precisa mostrar a contribuição real de cada integrante.

## 9. Script `enviar-pr.ps1` e um erro da IA corrigido no teste

- **Ferramenta:** Claude
- **Prompt (resumo):** "deixe tudo pronto para eles enviarem, o mais detalhado possível".
- **Resposta (resumo):** gerou um script PowerShell que clona o repositório, confere se o PR anterior
  já está na `main`, cria a branch, copia os arquivos, roda `ruff` e `pytest`, faz o commit e o push.
  Também gerou um guia por integrante.
- **Erro encontrado:** no teste com um repositório simulado, o PR2 falhou. A função auxiliar
  `Git-Ok add -A` não funcionava porque o PowerShell interpretava `-A` como abreviação do parâmetro
  `-a` da própria função. O teste também mostrou que rodar um PR que já estava na `main` gerava um
  erro confuso ("nothing to commit").
- **Correção:** a função passou a repassar os argumentos crus (`$args`), e foi incluída uma mensagem
  clara para "nada novo para enviar". Depois disso, os PRs 2 a 9 passaram no teste simulado, e a
  `main` final ficou idêntica ao projeto completo.
- **Decisão:** corrigido e aceito. Todos os integrantes enviaram seus PRs com o script.

## 10. Erro de login do Git em um dos computadores

- **Ferramenta:** Claude
- **Prompt (resumo):** "deu erro, apareceu que ele não está logado no git... não apareceu aquela aba
  de conectar".
- **Resposta (resumo):** explicou as causas prováveis (identidade do Git não configurada, gerenciador
  de credenciais desativado ou outra conta salva no Windows) e os comandos para cada caso:
  `git config --global user.name/user.email`, `git config --global credential.helper manager`,
  `git credential-manager github login` e `cmdkey /delete:git:https://github.com`.
- **Decisão:** aceito. O integrante conseguiu enviar o PR #3.

## 11. Teste com o modelo real revelou uma falha no exemplo da interface

- **Ferramenta:** Claude
- **Prompt (resumo):** "precisamos fazer os testes do programa rodando, como conseguimos?"
- **Resposta (resumo):** subiu o projeto com `docker compose up` (Ollama + `qwen2.5-coder:3b`) e testou
  7 perguntas no app e no pipeline. Seis deram certo: o `DELETE` foi gerado pelo modelo e **bloqueado
  pelo validador**, e "Qual é o melhor cliente?" pediu esclarecimento. A pergunta de exemplo
  "Quantos clientes temos em cada região?" deu **resposta errada**. Na 1ª tentativa o modelo usou a
  coluna `regiao` em `clientes`, que não existe. Na 2ª ele "corrigiu" contando *estados* por região,
  em vez de clientes.
- **Decisão:** a falha foi documentada como caso de falha e a pergunta foi trocada no roteiro do
  vídeo. O modelo e o prompt não foram alterados, porque as funcionalidades já estavam congeladas.
  Motivo: o caso mostra que a nova tentativa corrige erros de execução, mas não garante uma resposta
  certa. Por isso o usuário deve conferir o SQL e a explicação.

## 12. README detalhado com a contribuição de cada integrante

- **Ferramenta:** Claude
- **Prompt (resumo):** pedimos um README explicando o aplicativo com bastante detalhe e a parte de
  cada integrante.
- **Resposta (resumo):** reescreveu o README com funcionalidades, fluxo interno, camadas de segurança,
  banco, como rodar e usar, testes, avaliação e uma seção por integrante. Os resultados esperados
  das perguntas de exemplo vieram do teste real da interação 11.
- **Correção feita pelo grupo:** incluímos o nome do Integrante 1, que ficou como `[SEU NOME]` na
  primeira versão, e conferimos os nomes dos demais.
- **Decisão:** aceito e revisado pelo grupo via PR #10.

## 13. Guia de Docker para quem nunca usou

- **Ferramenta:** Claude
- **Prompt (resumo):** "como o pessoal faz o teste no PC deles... bem detalhado, como se fosse a
  primeira vez com Docker".
- **Resposta (resumo):** guia passo a passo: instalação do Docker Desktop com WSL 2, teste com
  `hello-world`, clone, `docker compose up`, perguntas de teste com os resultados esperados,
  desligamento e uma tabela de problemas comuns (WSL, virtualização na BIOS, porta em uso, memória).
- **Decisão:** aceito. Usado pelos integrantes para rodar o projeto no próprio computador.

## 14. Conferência do projeto contra o enunciado e a rubrica

- **Ferramenta:** Claude
- **Prompt (resumo):** enviamos o enunciado completo com a rubrica e pedimos para verificar se estava
  tudo correto e gerar os relatórios que faltavam.
- **Resposta (resumo):** conferiu item por item a estrutura do repositório, o CI, a documentação e as
  evidências. Mediu a cobertura (89%) e listou as pendências: avaliação experimental com o modelo,
  casos de falha, índice de evidências, decisões das interações 1 a 6, notas humanas das explicações,
  vídeo, pesquisa ABNT e tag `v1.0`. Rodou a avaliação e preencheu as evidências **só com números
  gerados pelo sistema**.
- **Decisão:** aceito, pendências executadas. O grupo revisou e mergeou o PR das evidências (#11),
  tirou os prints e decidiu, na interação 15, como tratar a avaliação das explicações.

## 15. Avaliação da amostra de explicações

- **Ferramenta:** Claude
- **Prompt (resumo):** pedimos para preencher as notas da amostra de explicações exigida no enunciado
  ("explicação … avaliada em amostra").
- **Resposta (resumo):** a IA não preencheu as colunas de nota humana (`nota_avaliador_1/2`), porque
  isso atribuiria ao grupo uma avaliação que não fizemos. Propôs avaliar a amostra ela mesma, com o
  critério de 1 a 5 da ficha, identificando a avaliação como feita por IA. Também mediu de forma
  automática o uso de termos técnicos. Resultado: média 3,6; 2 de 15 abaixo de 3; 3 de 15 com palavras
  proibidas pela instrução (SELECT, JOIN, GROUP BY, WHERE). Arquivo: `eval/resultados/explicacoes_avaliadas_ia.csv`.
- **Decisão:** aceito, com a ressalva registrada na pesquisa (seções 4.4 e 5.1) de que a avaliação não
  é humana. As colunas de nota humana continuam vazias no CSV original.

## 16. Rascunho do trabalho de pesquisa ABNT

- **Ferramenta:** Claude
- **Prompt (resumo):** pedimos um rascunho da pesquisa em padrão ABNT com os resultados da avaliação.
- **Resposta (resumo):** a IA conferiu na web 14 referências (artigos do EMNLP, NeurIPS, VLDB, ICSE e
  AISec, a LGPD, a OWASP e a documentação do SQLite e do Python) e escreveu os capítulos 1 a 5 usando só
  números gerados pelo sistema. Gerou o documento no Word, com formatação ABNT, e o PDF. Quando não
  conseguiu confirmar a lista completa de autores de dois artigos, usou "et al." em vez de arriscar.
- **Correções do grupo:** informamos os nomes completos, os RAs, o curso, o professor, a instituição e
  a cidade. Decidimos não fazer as notas humanas das explicações, e a avaliação passou a ser feita por
  IA, com a limitação registrada (interação 15).
- **Decisão:** aceito como base do texto final. A IA é permitida pelo enunciado para revisar e organizar
  o texto, e cada referência deve ser conferida pelo grupo na fonte original antes da defesa.

