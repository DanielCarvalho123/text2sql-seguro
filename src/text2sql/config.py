"""Configuração lida de variáveis de ambiente (nenhuma chave fica no código)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Config:
    ollama_url: str
    modelo: str
    db_path: Path
    limite_linhas: int
    limite_instrucoes: int
    timeout_llm: int
    log_path: Path


def carregar() -> Config:
    return Config(
        ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
        modelo=os.getenv("MODELO", "qwen2.5-coder:3b"),
        db_path=Path(os.getenv("DB_PATH", RAIZ / "data" / "loja.db")),
        limite_linhas=int(os.getenv("LIMITE_LINHAS", "1000")),
        limite_instrucoes=int(os.getenv("LIMITE_INSTRUCOES", "20000000")),
        timeout_llm=int(os.getenv("TIMEOUT_LLM", "180")),
        log_path=Path(os.getenv("LOG_PATH", RAIZ / "logs" / "app.log")),
    )
