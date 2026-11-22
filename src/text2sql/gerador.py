"""Montagem do prompt e extração do SQL da resposta do modelo."""

from __future__ import annotations

import re
from dataclasses import dataclass

SISTEMA = """Você é um assistente que traduz perguntas em português para SQL do SQLite.
Regras:
- Gere UMA única consulta de leitura (SELECT ou WITH ... SELECT). Nunca altere dados.
- Use apenas tabelas e colunas que existem no esquema.
- Responda somente com o SQL dentro de um bloco ```sql ... ```, sem explicações.
- Se a pergunta puder ser entendida de formas que levam a resultados diferentes
  (por exemplo, "melhor cliente" sem dizer o critério), NÃO gere SQL: responda
  exatamente `AMBIGUA: ` seguido de uma pergunta curta de esclarecimento.
- Se o usuário pedir para inserir, alterar ou apagar dados, responda exatamente
  `RECUSA: ` seguido do motivo."""

DICAS_DOMINIO = """Observações sobre os dados:
- O valor de um pedido é a soma de quantidade * preco_unitario dos seus itens.
- Faturamento/receita considera apenas pedidos com status diferente de 'cancelado',
  salvo se a pergunta disser outra coisa.
- Datas são texto no formato 'AAAA-MM-DD'; use strftime('%Y', coluna) para ano e
  strftime('%Y-%m', coluna) para mês.
- Para ordenar e limitar, use ORDER BY ... LIMIT n."""


@dataclass
class SaidaModelo:
    tipo: str  # "sql", "ambigua", "recusa" ou "vazia"
    conteudo: str


def montar_prompt(
    pergunta: str, esquema: str | None, sql_anterior: str | None = None, erro_anterior: str | None = None
) -> str:
    partes = []
    if esquema:
        partes += ["Esquema do banco (SQLite):", esquema, "", DICAS_DOMINIO, ""]
    else:
        partes += ["Banco SQLite de uma loja (esquema não informado).", ""]
    partes += [f"Pergunta: {pergunta}"]
    if sql_anterior and erro_anterior:
        partes += [
            "",
            "Sua consulta anterior falhou.",
            f"Consulta: {sql_anterior}",
            f"Erro: {erro_anterior}",
            "Corrija a consulta.",
        ]
    return "\n".join(partes)


_RE_BLOCO = re.compile(r"```(?:sql|sqlite)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)
_RE_PREFIXO = re.compile(r"^\s*(AMBIGUA|AMBÍGUA|RECUSA)\s*:\s*(.*)$", re.IGNORECASE | re.DOTALL)
# Qualquer comando SQL no início de uma linha é extraído, inclusive os perigosos:
# assim o validador pode bloqueá-los e o bloqueio fica registrado.
_RE_INICIO_SQL = re.compile(
    r"^\s*(SELECT|WITH|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|PRAGMA|ATTACH|REPLACE|VACUUM)\b",
    re.IGNORECASE | re.MULTILINE,
)


def extrair_sql(texto: str) -> SaidaModelo:
    """Interpreta a resposta do modelo."""
    texto = (texto or "").strip()
    # Alguns modelos "pensam" antes de responder; ignoramos esse trecho.
    texto = re.sub(r"<think>.*?</think>", "", texto, flags=re.DOTALL).strip()
    m = _RE_PREFIXO.match(texto)
    if m:
        tipo = "recusa" if m.group(1).upper() == "RECUSA" else "ambigua"
        return SaidaModelo(tipo, m.group(2).strip().strip("`").strip())
    bloco = _RE_BLOCO.search(texto)
    if bloco:
        return SaidaModelo("sql", bloco.group(1).strip())
    inicio = _RE_INICIO_SQL.search(texto)
    if inicio:
        return SaidaModelo("sql", texto[inicio.start() :].strip())
    return SaidaModelo("vazia", texto)
