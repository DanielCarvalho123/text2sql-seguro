"""Cliente mínimo para o Ollama (modelo aberto rodando localmente, custo zero)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Protocol

import requests


class ErroLLM(Exception):
    """Falha ao falar com o modelo (Ollama fora do ar, modelo ausente, timeout)."""


@dataclass
class RespostaLLM:
    texto: str
    tokens_entrada: int = 0
    tokens_saida: int = 0
    tempo_ms: float = 0.0


class ClienteLLM(Protocol):
    modelo: str

    def gerar(self, prompt: str, sistema: str = "") -> RespostaLLM: ...


class ClienteOllama:
    def __init__(self, url: str, modelo: str, timeout: int = 180):
        self.url = url.rstrip("/")
        self.modelo = modelo
        self.timeout = timeout

    def gerar(self, prompt: str, sistema: str = "") -> RespostaLLM:
        inicio = time.perf_counter()
        try:
            r = requests.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.modelo,
                    "prompt": prompt,
                    "system": sistema,
                    "stream": False,
                    "options": {"temperature": 0, "seed": 42},
                },
                timeout=self.timeout,
            )
        except requests.RequestException as erro:
            raise ErroLLM(f"não foi possível falar com o Ollama em {self.url}: {erro}") from erro
        if r.status_code != 200:
            raise ErroLLM(f"Ollama respondeu {r.status_code}: {r.text[:200]}")
        dados = r.json()
        return RespostaLLM(
            texto=dados.get("response", ""),
            tokens_entrada=int(dados.get("prompt_eval_count", 0) or 0),
            tokens_saida=int(dados.get("eval_count", 0) or 0),
            tempo_ms=(time.perf_counter() - inicio) * 1000,
        )

    def disponivel(self) -> bool:
        try:
            r = requests.get(f"{self.url}/api/tags", timeout=5)
            nomes = {m.get("name") for m in r.json().get("models", [])}
            return self.modelo in nomes or f"{self.modelo}:latest" in nomes
        except (requests.RequestException, ValueError):
            return False
