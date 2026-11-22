"""Validação e execução segura de SQL gerado por IA.

Defesa em camadas (qualquer camada bloqueia sozinha):

1. Análise léxica: uma única instrução, começando por SELECT ou WITH, sem
   palavras-chave de escrita (strings e comentários são ignorados na busca).
2. Autorizador do SQLite: durante a compilação, o próprio motor só permite
   leitura das tabelas conhecidas e nega funções perigosas.
3. Conexão somente leitura (``mode=ro``): mesmo que algo passe, o arquivo não
   pode ser alterado.
4. Limite de custo: a execução é interrompida após um número máximo de
   instruções da máquina virtual do SQLite (protege contra consultas caras,
   como produtos cartesianos ou CTEs recursivas infinitas).
5. Limite de linhas devolvidas.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

PALAVRAS_PROIBIDAS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "ATTACH",
    "DETACH",
    "PRAGMA",
    "VACUUM",
    "REINDEX",
    "ANALYZE",
    "TRUNCATE",
    "GRANT",
    "REVOKE",
    "BEGIN",
    "COMMIT",
    "ROLLBACK",
    "SAVEPOINT",
    "RELEASE",
    "UPSERT",
]
# REPLACE é proibido como comando, mas replace(...) é uma função de texto válida.
_RE_REPLACE_COMANDO = re.compile(r"\bREPLACE\b(?!\s*\()", re.IGNORECASE)
_RE_PROIBIDAS = re.compile(r"\b(" + "|".join(PALAVRAS_PROIBIDAS) + r")\b", re.IGNORECASE)

FUNCOES_PROIBIDAS = {
    "load_extension",
    "readfile",
    "writefile",
    "edit",
    "fts3_tokenizer",
    "zipfile",
    "sqlar_uncompress",
}

_SQLITE_RECURSIVE = getattr(sqlite3, "SQLITE_RECURSIVE", 33)
_ACOES_PERMITIDAS = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, _SQLITE_RECURSIVE}


class ConsultaBloqueada(Exception):
    """A consulta foi recusada por uma regra de segurança ou de custo."""

    def __init__(self, motivo: str, camada: str):
        super().__init__(motivo)
        self.motivo = motivo
        self.camada = camada


@dataclass
class ResultadoConsulta:
    colunas: list[str]
    linhas: list[tuple]
    truncado: bool
    plano: list[str] = field(default_factory=list)


def esqueleto(sql: str) -> str:
    """Substitui strings, identificadores entre aspas e comentários por espaços.

    Assim a busca por palavras proibidas e por ';' não é enganada por
    conteúdo dentro de literais (ex.: WHERE nome = 'DROP TABLE').
    """
    saida: list[str] = []
    i, n = 0, len(sql)
    while i < n:
        c = sql[i]
        if c == "-" and sql.startswith("--", i):
            fim = sql.find("\n", i)
            fim = n if fim == -1 else fim
            saida.append(" " * (fim - i))
            i = fim
        elif c == "/" and sql.startswith("/*", i):
            fim = sql.find("*/", i + 2)
            fim = n if fim == -1 else fim + 2
            saida.append(" " * (fim - i))
            i = fim
        elif c in ("'", '"', "`", "["):
            fecha = "]" if c == "[" else c
            j = i + 1
            while j < n:
                if sql[j] == fecha:
                    if fecha != "]" and j + 1 < n and sql[j + 1] == fecha:
                        j += 2  # aspas duplicadas = escape
                        continue
                    break
                j += 1
            j = min(j + 1, n)
            saida.append(c + " " * max(j - i - 2, 0) + (fecha if j - i >= 2 else ""))
            i = j
        else:
            saida.append(c)
            i += 1
    return "".join(saida)


def normalizar(sql: str) -> str:
    """Remove espaços e ponto e vírgula finais."""
    sql = sql.strip()
    while sql.endswith(";"):
        sql = sql[:-1].rstrip()
    return sql


def motivos_de_bloqueio(sql: str) -> list[str]:
    """Lista os problemas léxicos da consulta (lista vazia = aprovada)."""
    motivos = []
    sql = normalizar(sql)
    if not sql:
        return ["consulta vazia"]
    esq = esqueleto(sql)
    if ";" in esq:
        motivos.append("mais de uma instrução SQL")
    primeira = esq.strip().split(None, 1)[0].upper() if esq.strip() else ""
    if primeira not in ("SELECT", "WITH"):
        motivos.append(f"a consulta precisa começar com SELECT ou WITH (começa com {primeira!r})")
    proibidas = sorted({m.upper() for m in _RE_PROIBIDAS.findall(esq)})
    if _RE_REPLACE_COMANDO.search(esq):
        proibidas.append("REPLACE")
    if proibidas:
        motivos.append("comando de escrita ou administração: " + ", ".join(proibidas))
    return motivos


def validar(sql: str) -> str:
    """Valida lexicamente e devolve a consulta normalizada, ou levanta ConsultaBloqueada."""
    motivos = motivos_de_bloqueio(sql)
    if motivos:
        raise ConsultaBloqueada("; ".join(motivos), camada="léxica")
    return normalizar(sql)


def _tabela_proibida(nome: str | None) -> bool:
    """Tabelas internas do SQLite e funções pragma_* não podem ser lidas.

    Nomes de CTE (WITH x AS ...) também geram eventos de leitura, por isso a
    regra é uma lista de prefixos proibidos, e não uma lista de permitidos.
    """
    nome = (nome or "").lower()
    return nome.startswith(("sqlite_", "pragma_"))


def _autorizador(negados: list[str]):
    def autorizar(acao, arg1, arg2, _db, _gatilho):
        if acao not in _ACOES_PERMITIDAS:
            negados.append(f"operação não permitida (código {acao})")
            return sqlite3.SQLITE_DENY
        if acao == sqlite3.SQLITE_READ and _tabela_proibida(arg1):
            negados.append(f"leitura da tabela {arg1!r} não permitida")
            return sqlite3.SQLITE_DENY
        if acao == sqlite3.SQLITE_FUNCTION and (arg2 or "").lower() in FUNCOES_PROIBIDAS:
            negados.append(f"função {arg2!r} não permitida")
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    return autorizar


def conectar_somente_leitura(db_path: Path | str) -> sqlite3.Connection:
    uri = Path(db_path).resolve().as_uri() + "?mode=ro"
    return sqlite3.connect(uri, uri=True)


def executar(
    db_path: Path | str,
    sql: str,
    limite_linhas: int = 1000,
    limite_instrucoes: int = 20_000_000,
    validar_sql: bool = True,
) -> ResultadoConsulta:
    """Executa a consulta com todas as camadas de proteção.

    ``validar_sql=False`` desliga as camadas 1 e 2 (usado só no baseline da
    avaliação); a conexão continua somente leitura.
    """
    sql = validar(sql) if validar_sql else normalizar(sql)
    conn = conectar_somente_leitura(db_path)
    negados: list[str] = []
    passos = {"n": 0}
    intervalo = 1000

    def progresso():
        passos["n"] += intervalo
        return 1 if passos["n"] > limite_instrucoes else 0

    try:
        if validar_sql:
            conn.set_authorizer(_autorizador(negados))
        conn.set_progress_handler(progresso, intervalo)
        try:
            plano = [linha[-1] for linha in conn.execute("EXPLAIN QUERY PLAN " + sql)]
            cur = conn.execute(sql)
            colunas = [d[0] for d in cur.description or []]
            linhas = cur.fetchmany(limite_linhas + 1)
        except sqlite3.DatabaseError as erro:
            if negados:
                raise ConsultaBloqueada("; ".join(dict.fromkeys(negados)), camada="autorizador") from erro
            if passos["n"] > limite_instrucoes:
                raise ConsultaBloqueada(
                    f"custo excedido (mais de {limite_instrucoes:,} instruções)".replace(",", "."),
                    camada="custo",
                ) from erro
            raise
    finally:
        conn.close()
    truncado = len(linhas) > limite_linhas
    return ResultadoConsulta(colunas, linhas[:limite_linhas], truncado, plano)
