"""Funções de comparação usadas na avaliação experimental.

Acurácia por execução: a consulta gerada é considerada correta quando seu
resultado é igual ao da consulta de referência. Duas variantes:

- exata: mesmas linhas (ordem ignorada) e mesmo número de colunas;
- relaxada: cada coluna da referência aparece no resultado gerado, com as
  mesmas linhas. Aceita colunas extras (ex.: o modelo devolveu o nome do
  produto E o preço quando só o nome foi pedido).

Números são arredondados para 2 casas antes da comparação.
"""

from __future__ import annotations

import itertools
from collections import Counter


def _norm(valor):
    if isinstance(valor, float):
        return round(valor, 2)
    if isinstance(valor, int):
        return round(float(valor), 2)
    return valor


def _linhas(linhas) -> Counter:
    return Counter(tuple(_norm(v) for v in linha) for linha in linhas)


def igual_exato(ref: list[tuple], gerado: list[tuple]) -> bool:
    if len(ref) != len(gerado):
        return False
    if ref and gerado and len(ref[0]) != len(gerado[0]):
        return False
    return _linhas(ref) == _linhas(gerado)


def igual_relaxado(ref: list[tuple], gerado: list[tuple], max_combinacoes: int = 5000) -> bool:
    if igual_exato(ref, gerado):
        return True
    if len(ref) != len(gerado) or not ref:
        return False
    n_ref, n_ger = len(ref[0]), len(gerado[0])
    if n_ger < n_ref:
        return False
    col_ref = [Counter(_norm(linha[i]) for linha in ref) for i in range(n_ref)]
    col_ger = [Counter(_norm(linha[j]) for linha in gerado) for j in range(n_ger)]
    candidatos = [[j for j in range(n_ger) if col_ger[j] == col_ref[i]] for i in range(n_ref)]
    if any(not c for c in candidatos):
        return False
    alvo = _linhas(ref)
    for n, escolha in enumerate(itertools.product(*candidatos)):
        if n >= max_combinacoes:
            break
        if len(set(escolha)) != len(escolha):
            continue
        projetado = Counter(tuple(_norm(linha[j]) for j in escolha) for linha in gerado)
        if projetado == alvo:
            return True
    return False
