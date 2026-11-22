import sqlite3

import pytest

from text2sql import validador as v

ATAQUES_LEXICOS = [
    "DROP TABLE clientes",
    "DELETE FROM pedidos",
    "UPDATE produtos SET preco = 0",
    "INSERT INTO clientes VALUES (999, 'x', 'SP', '2025-01-01')",
    "SELECT 1; DROP TABLE clientes",
    "SELECT * FROM clientes; DELETE FROM clientes",
    "WITH x AS (SELECT 1) DELETE FROM clientes",
    "ATTACH DATABASE '/tmp/x.db' AS x",
    "PRAGMA writable_schema = 1",
    "REPLACE INTO produtos VALUES (1, 'x', 'y', 0)",
    "CREATE TABLE copia AS SELECT * FROM clientes",
    "VACUUM",
    "   ",
]


@pytest.mark.parametrize("sql", ATAQUES_LEXICOS)
def test_ataques_lexicos_sao_bloqueados(sql, banco):
    with pytest.raises(v.ConsultaBloqueada):
        v.executar(banco, sql)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM sqlite_master",
        "SELECT name FROM sqlite_schema",
        "SELECT * FROM pragma_table_info('clientes')",
        "SELECT load_extension('/tmp/malicioso')",
    ],
)
def test_autorizador_bloqueia_tabelas_internas_e_funcoes(sql, banco):
    with pytest.raises(v.ConsultaBloqueada) as erro:
        v.executar(banco, sql)
    assert erro.value.camada == "autorizador"


def test_limite_de_custo_interrompe_produto_cartesiano(banco):
    with pytest.raises(v.ConsultaBloqueada) as erro:
        v.executar(
            banco,
            "SELECT COUNT(*) FROM itens_pedido a, itens_pedido b, itens_pedido c",
            limite_instrucoes=1_000_000,
        )
    assert erro.value.camada == "custo"


def test_limite_de_custo_interrompe_recursao_infinita(banco):
    sql = "WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM c) SELECT COUNT(*) FROM c"
    with pytest.raises(v.ConsultaBloqueada):
        v.executar(banco, sql, limite_instrucoes=1_000_000)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM clientes WHERE nome = 'DROP TABLE clientes'",
        "SELECT replace(nome, 'a', 'b') FROM clientes LIMIT 1",
        "SELECT nome FROM clientes -- DELETE no comentário\nLIMIT 2",
        "WITH t AS (SELECT uf FROM clientes) SELECT uf, COUNT(*) FROM t GROUP BY uf",
        "select count(*) from pedidos;",
        "SELECT data_cadastro AS updated FROM clientes LIMIT 1",
    ],
)
def test_consultas_legitimas_nao_sao_bloqueadas(sql, banco):
    assert v.executar(banco, sql).colunas


def test_palavra_dentro_de_identificador_nao_bloqueia():
    assert v.motivos_de_bloqueio("SELECT updated_at, created FROM t") == []


def test_limite_de_linhas(banco):
    r = v.executar(banco, "SELECT * FROM clientes", limite_linhas=10)
    assert len(r.linhas) == 10 and r.truncado


def test_resultado_tem_plano(banco):
    r = v.executar(banco, "SELECT COUNT(*) FROM pedidos")
    assert r.linhas == [(3000,)]
    assert r.plano


def test_conexao_e_somente_leitura(banco):
    conn = v.conectar_somente_leitura(banco)
    with pytest.raises(sqlite3.OperationalError):
        conn.execute("DELETE FROM clientes")
    conn.close()


def test_sem_validacao_ainda_protege_o_arquivo(banco):
    with pytest.raises(sqlite3.Error):
        v.executar(banco, "DELETE FROM clientes", validar_sql=False)
    assert v.executar(banco, "SELECT COUNT(*) FROM clientes").linhas == [(500,)]


def test_esqueleto_preserva_tamanho_e_remove_literais():
    sql = "SELECT 'a;b' , \"x\" FROM t /* drop */ -- delete"
    esq = v.esqueleto(sql)
    assert len(esq) == len(sql)
    assert ";" not in esq and "drop" not in esq and "delete" not in esq
