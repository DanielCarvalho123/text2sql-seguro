"""Logs estruturados (JSON por linha, com data e hora) para as evidências."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

_LOGGER = "text2sql"


class _FormatoJSON(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        dados = {
            "data_hora": datetime.now(UTC).astimezone().isoformat(timespec="milliseconds"),
            "nivel": record.levelname,
            "evento": record.getMessage(),
        }
        dados.update(getattr(record, "dados", {}))
        return json.dumps(dados, ensure_ascii=False, default=str)


def configurar(caminho: Path | str | None = None) -> logging.Logger:
    logger = logging.getLogger(_LOGGER)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    logger.propagate = False
    saida = logging.StreamHandler()
    saida.setFormatter(_FormatoJSON())
    logger.addHandler(saida)
    if caminho:
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        arquivo = logging.FileHandler(caminho, encoding="utf-8")
        arquivo.setFormatter(_FormatoJSON())
        logger.addHandler(arquivo)
    return logger


def registrar(evento: str, **dados) -> None:
    logging.getLogger(_LOGGER).info(evento, extra={"dados": dados})
