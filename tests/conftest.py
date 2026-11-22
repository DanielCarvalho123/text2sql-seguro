from __future__ import annotations

import pytest

from text2sql import dados


@pytest.fixture(scope="session")
def banco(tmp_path_factory):
    return dados.gerar_banco(tmp_path_factory.mktemp("db") / "loja.db")


class LLMFalso:
    """Modelo simulado: devolve respostas pré-definidas, em ordem."""

    modelo = "falso"

    def __init__(self, respostas: list[str] | None = None, falhar: bool = False):
        self.respostas = list(respostas or [])
        self.falhar = falhar
        self.prompts: list[str] = []

    def gerar(self, prompt: str, sistema: str = ""):
        # Import local: assim o conftest funciona mesmo antes de llm.py existir.
        from text2sql.llm import ErroLLM, RespostaLLM

        self.prompts.append(prompt)
        if self.falhar:
            raise ErroLLM("modelo fora do ar")
        texto = self.respostas.pop(0) if self.respostas else ""
        return RespostaLLM(texto=texto, tokens_entrada=10, tokens_saida=5, tempo_ms=1)


@pytest.fixture
def llm_falso():
    return LLMFalso
