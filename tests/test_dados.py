import sqlite3

from text2sql import dados


def contar(caminho, tabela):
    with sqlite3.connect(caminho) as conn:
        return conn.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]


def test_banco_tem_todas_as_tabelas(banco):
    assert contar(banco, "estados") == 27
    assert contar(banco, "clientes") == 500
    assert contar(banco, "pedidos") == 3000
    assert contar(banco, "produtos") > 30
    assert contar(banco, "itens_pedido") > 3000


def test_geracao_e_deterministica(tmp_path):
    a = dados.gerar_banco(tmp_path / "a.db")
    b = dados.gerar_banco(tmp_path / "b.db")
    consulta = "SELECT SUM(quantidade * preco_unitario) FROM itens_pedido"
    with sqlite3.connect(a) as ca, sqlite3.connect(b) as cb:
        assert ca.execute(consulta).fetchone() == cb.execute(consulta).fetchone()


def test_pedidos_nao_sao_anteriores_ao_cadastro(banco):
    with sqlite3.connect(banco) as conn:
        invalidos = conn.execute(
            "SELECT COUNT(*) FROM pedidos p JOIN clientes c ON c.id = p.cliente_id "
            "WHERE p.data_pedido < c.data_cadastro"
        ).fetchone()[0]
    assert invalidos == 0


def test_esquema_do_prompt_menciona_todas_as_tabelas():
    esquema = dados.esquema_para_prompt()
    for tabela in dados.TABELAS:
        assert f"CREATE TABLE {tabela}" in esquema
