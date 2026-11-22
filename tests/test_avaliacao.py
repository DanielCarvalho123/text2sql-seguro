from eval.avaliar import resumir_ataques_sql, rodar_ataques_sql
from text2sql.avaliacao import igual_exato, igual_relaxado


def test_exato_ignora_ordem_e_arredonda():
    assert igual_exato([("a", 1.004), ("b", 2)], [("b", 2.0), ("a", 1.0)])


def test_exato_diferencia_valores():
    assert not igual_exato([("a", 1)], [("a", 2)])


def test_exato_exige_mesmo_numero_de_colunas():
    assert not igual_exato([("Monitor",)], [("Monitor", 899.0)])


def test_relaxado_aceita_coluna_extra():
    assert igual_relaxado([("Monitor",)], [("Monitor", 899.0)])


def test_relaxado_aceita_colunas_em_outra_ordem():
    assert igual_relaxado([("SP", 115), ("RJ", 50)], [(50, "RJ", "x"), (115, "SP", "y")])


def test_relaxado_exige_mesmas_linhas():
    assert not igual_relaxado([("SP",)], [("SP",), ("RJ",)])


def test_relaxado_verifica_alinhamento_das_linhas():
    ref = [("a", 1), ("b", 2)]
    trocado = [("a", 2), ("b", 1)]
    assert not igual_relaxado(ref, trocado)


def test_catalogo_de_ataques_sql_passa_inteiro(banco):
    linhas = rodar_ataques_sql(banco)
    resumo = resumir_ataques_sql(linhas)
    falhas = [linha for linha in linhas if not linha["acertou"]]
    assert not falhas, falhas
    assert resumo["ataques_contidos"] == resumo["ataques"]
    assert resumo["legitimas_bloqueadas"] == 0
