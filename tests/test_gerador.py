import pytest

from text2sql import gerador


def test_extrai_bloco_sql():
    s = gerador.extrair_sql("Claro!\n```sql\nSELECT 1;\n```\nPronto.")
    assert s.tipo == "sql" and s.conteudo == "SELECT 1;"


def test_extrai_bloco_sem_linguagem():
    assert gerador.extrair_sql("```\nSELECT 2\n```").conteudo == "SELECT 2"


def test_extrai_sql_sem_bloco():
    s = gerador.extrair_sql("Aqui está:\nSELECT nome FROM clientes")
    assert s.conteudo == "SELECT nome FROM clientes"


def test_extrai_comando_perigoso_para_o_validador_bloquear():
    s = gerador.extrair_sql("DELETE FROM pedidos")
    assert s.tipo == "sql" and s.conteudo == "DELETE FROM pedidos"


def test_palavra_select_no_meio_do_texto_nao_vira_sql():
    assert gerador.extrair_sql("Não consigo selecionar isso, select é ambíguo").tipo == "vazia"


@pytest.mark.parametrize("texto", ["AMBIGUA: qual critério?", "ambígua: qual critério?"])
def test_detecta_ambiguidade(texto):
    s = gerador.extrair_sql(texto)
    assert s.tipo == "ambigua" and s.conteudo == "qual critério?"


def test_detecta_recusa():
    assert gerador.extrair_sql("RECUSA: não altero dados").tipo == "recusa"


def test_ignora_trecho_de_raciocinio():
    s = gerador.extrair_sql("<think>talvez DELETE?</think>```sql\nSELECT 3\n```")
    assert s.conteudo == "SELECT 3"


def test_resposta_sem_sql():
    assert gerador.extrair_sql("Não sei.").tipo == "vazia"


def test_prompt_com_e_sem_esquema():
    com = gerador.montar_prompt("Quantos clientes?", "CREATE TABLE clientes (id INTEGER)")
    sem = gerador.montar_prompt("Quantos clientes?", None)
    assert "CREATE TABLE clientes" in com and "CREATE TABLE" not in sem
    assert "Quantos clientes?" in com and "Quantos clientes?" in sem


def test_prompt_de_correcao_inclui_erro():
    p = gerador.montar_prompt("x", None, "SELECT y FROM z", "no such table: z")
    assert "no such table: z" in p and "SELECT y FROM z" in p
