"""Explicação da consulta em linguagem simples, para quem não sabe SQL."""

from __future__ import annotations

import re

from .llm import ClienteLLM, ErroLLM
from .validador import esqueleto

SISTEMA_EXPLICACAO = """Você explica consultas SQL para pessoas que não sabem programar.
Escreva em português, em no máximo 4 frases curtas, sem jargão técnico
(não use as palavras SELECT, JOIN, GROUP BY, WHERE). Diga quais dados foram
usados, que filtros foram aplicados e como o resultado foi organizado."""

_AGREGACOES = {"COUNT": "contagem", "SUM": "soma", "AVG": "média", "MAX": "maior valor", "MIN": "menor valor"}
_NOMES_TABELAS = {
    "clientes": "clientes",
    "pedidos": "pedidos",
    "produtos": "produtos",
    "itens_pedido": "itens dos pedidos",
    "estados": "estados",
}


def explicar_regras(sql: str) -> str:
    """Explicação determinística (não depende do modelo; usada como reserva)."""
    esq = esqueleto(sql)
    tabelas = re.findall(r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)", esq, re.IGNORECASE)
    tabelas = [_NOMES_TABELAS.get(t.lower(), t) for t in dict.fromkeys(t.lower() for t in tabelas)]
    frases = []
    if tabelas:
        frases.append("Os dados vêm de: " + ", ".join(tabelas) + ".")
    if len(tabelas) > 1:
        frases.append("As informações dessas tabelas foram cruzadas entre si.")
    if re.search(r"\bWHERE\b", esq, re.IGNORECASE):
        frases.append("Só entram os registros que atendem às condições da pergunta.")
    calc = [nome for fn, nome in _AGREGACOES.items() if re.search(rf"\b{fn}\s*\(", esq, re.IGNORECASE)]
    if calc:
        frases.append("Foi calculado(a): " + ", ".join(calc) + ".")
    if re.search(r"\bGROUP\s+BY\b", esq, re.IGNORECASE):
        frases.append("Os resultados foram agrupados por categoria antes do cálculo.")
    ordem = re.search(r"\bORDER\s+BY\b(.*?)(\bLIMIT\b|$)", esq, re.IGNORECASE | re.DOTALL)
    if ordem:
        sentido = (
            "do maior para o menor"
            if re.search(r"\bDESC\b", ordem.group(1), re.IGNORECASE)
            else "do menor para o maior"
        )
        frases.append(f"O resultado está ordenado {sentido}.")
    limite = re.search(r"\bLIMIT\s+(\d+)", esq, re.IGNORECASE)
    if limite:
        frases.append(f"São mostrados no máximo {limite.group(1)} resultados.")
    return " ".join(frases) or "Consulta simples de leitura dos dados."


def explicar(cliente: ClienteLLM | None, pergunta: str, sql: str) -> tuple[str, str]:
    """Devolve (explicação, origem). Usa o modelo e, se falhar, as regras."""
    if cliente is not None:
        try:
            r = cliente.gerar(
                f"Pergunta do usuário: {pergunta}\nConsulta:\n{sql}", sistema=SISTEMA_EXPLICACAO
            )
            texto = r.texto.strip()
            if texto:
                return texto, "modelo"
        except ErroLLM:
            pass
    return explicar_regras(sql), "regras"
