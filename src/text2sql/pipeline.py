"""Fluxo principal: pergunta -> SQL -> validação -> execução -> explicação."""

from __future__ import annotations

import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from . import dados, explicador, gerador, validador
from .llm import ClienteLLM, ErroLLM
from .logs import registrar


@dataclass
class Resposta:
    status: str  # ok | ambigua | recusada | bloqueada | erro
    pergunta: str
    sql: str = ""
    colunas: list[str] = field(default_factory=list)
    linhas: list[tuple] = field(default_factory=list)
    truncado: bool = False
    explicacao: str = ""
    origem_explicacao: str = ""
    mensagem: str = ""
    camada_bloqueio: str = ""
    plano: list[str] = field(default_factory=list)
    tentativas: int = 0
    tokens_entrada: int = 0
    tokens_saida: int = 0
    tempo_ms: float = 0.0
    id: str = ""


class Assistente:
    """Assistente de dados.

    Parâmetros usados para os baselines da avaliação:
    - ``usar_esquema=False``: o modelo não recebe o esquema do banco.
    - ``validar_sql=False``: desliga o validador léxico e o autorizador.
    """

    def __init__(
        self,
        cliente: ClienteLLM,
        db_path: Path | str,
        *,
        usar_esquema: bool = True,
        validar_sql: bool = True,
        explicar: bool = True,
        max_tentativas: int = 2,
        limite_linhas: int = 1000,
        limite_instrucoes: int = 20_000_000,
    ):
        self.cliente = cliente
        self.db_path = Path(db_path)
        self.usar_esquema = usar_esquema
        self.validar_sql = validar_sql
        self.explicar = explicar
        self.max_tentativas = max_tentativas
        self.limite_linhas = limite_linhas
        self.limite_instrucoes = limite_instrucoes
        self.esquema = dados.esquema_para_prompt() if usar_esquema else None

    def responder(self, pergunta: str) -> Resposta:
        inicio = time.perf_counter()
        resp = Resposta(status="erro", pergunta=pergunta, id=uuid.uuid4().hex[:8])
        registrar(
            "pergunta_recebida",
            id=resp.id,
            pergunta=pergunta,
            modelo=self.cliente.modelo,
            usar_esquema=self.usar_esquema,
            validar_sql=self.validar_sql,
        )
        sql_anterior = erro_anterior = None
        try:
            for tentativa in range(1, self.max_tentativas + 1):
                resp.tentativas = tentativa
                prompt = gerador.montar_prompt(pergunta, self.esquema, sql_anterior, erro_anterior)
                saida_llm = self.cliente.gerar(prompt, sistema=gerador.SISTEMA)
                resp.tokens_entrada += saida_llm.tokens_entrada
                resp.tokens_saida += saida_llm.tokens_saida
                saida = gerador.extrair_sql(saida_llm.texto)
                registrar(
                    "resposta_modelo",
                    id=resp.id,
                    tentativa=tentativa,
                    tipo=saida.tipo,
                    conteudo=saida.conteudo,
                    tempo_modelo_ms=round(saida_llm.tempo_ms),
                )

                if saida.tipo == "ambigua":
                    resp.status, resp.mensagem = "ambigua", saida.conteudo
                    break
                if saida.tipo == "recusa":
                    resp.status, resp.mensagem = "recusada", saida.conteudo
                    break
                if saida.tipo == "vazia":
                    sql_anterior, erro_anterior = saida.conteudo[:200], "a resposta não continha SQL"
                    resp.mensagem = "O modelo não gerou uma consulta."
                    continue

                resp.sql = saida.conteudo
                try:
                    resultado = validador.executar(
                        self.db_path,
                        saida.conteudo,
                        self.limite_linhas,
                        self.limite_instrucoes,
                        validar_sql=self.validar_sql,
                    )
                except validador.ConsultaBloqueada as bloqueio:
                    resp.status, resp.mensagem = "bloqueada", bloqueio.motivo
                    resp.camada_bloqueio = bloqueio.camada
                    registrar(
                        "consulta_bloqueada",
                        id=resp.id,
                        sql=saida.conteudo,
                        camada=bloqueio.camada,
                        motivo=bloqueio.motivo,
                    )
                    break
                except sqlite3.Error as erro:
                    sql_anterior, erro_anterior = saida.conteudo, str(erro)
                    resp.status, resp.mensagem = "erro", f"Erro ao executar a consulta: {erro}"
                    registrar("erro_execucao", id=resp.id, sql=saida.conteudo, erro=str(erro))
                    continue

                resp.status = "ok"
                resp.colunas, resp.linhas = resultado.colunas, resultado.linhas
                resp.truncado, resp.plano = resultado.truncado, resultado.plano
                resp.mensagem = ""
                registrar(
                    "consulta_executada",
                    id=resp.id,
                    sql=saida.conteudo,
                    linhas=len(resultado.linhas),
                    truncado=resultado.truncado,
                    plano=resultado.plano,
                )
                if self.explicar:
                    resp.explicacao, resp.origem_explicacao = explicador.explicar(
                        self.cliente, pergunta, saida.conteudo
                    )
                break
        except ErroLLM as erro:
            resp.status, resp.mensagem = "erro", str(erro)
            registrar("erro_modelo", id=resp.id, erro=str(erro))

        resp.tempo_ms = (time.perf_counter() - inicio) * 1000
        registrar(
            "resposta_final",
            id=resp.id,
            status=resp.status,
            sql=resp.sql,
            mensagem=resp.mensagem,
            tentativas=resp.tentativas,
            tokens=resp.tokens_entrada + resp.tokens_saida,
            tempo_ms=round(resp.tempo_ms),
        )
        return resp
