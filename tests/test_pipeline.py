from text2sql import explicador
from text2sql.pipeline import Assistente


def test_fluxo_ok(banco, llm_falso):
    llm = llm_falso(["```sql\nSELECT COUNT(*) AS total FROM clientes\n```", "Conta os clientes."])
    r = Assistente(llm, banco).responder("Quantos clientes?")
    assert r.status == "ok"
    assert r.linhas == [(500,)] and r.colunas == ["total"]
    assert r.explicacao == "Conta os clientes." and r.origem_explicacao == "modelo"
    assert r.tokens_entrada == 10 and r.tentativas == 1  # só a geração do SQL


def test_corrige_apos_erro_de_execucao(banco, llm_falso):
    llm = llm_falso(["SELECT nome FROM cliente", "SELECT nome FROM clientes LIMIT 1"])
    r = Assistente(llm, banco, explicar=False).responder("Um cliente")
    assert r.status == "ok" and r.tentativas == 2
    assert "no such table" in llm.prompts[1]


def test_desiste_apos_tentativas(banco, llm_falso):
    llm = llm_falso(["SELECT x FROM nada", "SELECT y FROM nada"])
    r = Assistente(llm, banco, explicar=False).responder("?")
    assert r.status == "erro" and r.tentativas == 2


def test_bloqueia_sql_destrutivo_sem_nova_tentativa(banco, llm_falso):
    llm = llm_falso(["```sql\nDELETE FROM pedidos\n```", "SELECT 1"])
    r = Assistente(llm, banco).responder("Apague os pedidos")
    assert r.status == "bloqueada" and r.camada_bloqueio == "léxica"
    assert r.tentativas == 1


def test_pergunta_ambigua(banco, llm_falso):
    r = Assistente(llm_falso(["AMBIGUA: melhor por valor gasto ou por número de pedidos?"]), banco).responder(
        "Qual o melhor cliente?"
    )
    assert r.status == "ambigua" and "valor gasto" in r.mensagem


def test_recusa_do_modelo(banco, llm_falso):
    r = Assistente(llm_falso(["RECUSA: não posso alterar dados"]), banco).responder("Apague tudo")
    assert r.status == "recusada"


def test_modelo_fora_do_ar(banco, llm_falso):
    r = Assistente(llm_falso(falhar=True), banco).responder("Quantos clientes?")
    assert r.status == "erro" and "fora do ar" in r.mensagem


def test_baseline_sem_esquema_nao_envia_esquema(banco, llm_falso):
    llm = llm_falso(["SELECT 1"])
    Assistente(llm, banco, usar_esquema=False, explicar=False).responder("x")
    assert "CREATE TABLE" not in llm.prompts[0]


def test_explicacao_por_regras():
    texto = explicador.explicar_regras(
        "SELECT e.regiao, COUNT(*) FROM clientes c JOIN estados e ON e.sigla = c.uf "
        "WHERE c.uf <> 'SP' GROUP BY e.regiao ORDER BY 2 DESC LIMIT 3"
    )
    assert "clientes" in texto and "estados" in texto
    assert "contagem" in texto and "maior para o menor" in texto and "3" in texto


def test_explicacao_cai_para_regras_se_modelo_falha(llm_falso):
    texto, origem = explicador.explicar(llm_falso(falhar=True), "x", "SELECT COUNT(*) FROM pedidos")
    assert origem == "regras" and "pedidos" in texto
