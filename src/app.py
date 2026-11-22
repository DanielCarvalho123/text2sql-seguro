"""Interface web (Streamlit) do assistente de dados.

Execute com:  streamlit run src/app.py
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from text2sql import config, dados, logs
from text2sql.llm import ClienteOllama
from text2sql.pipeline import Assistente

EXEMPLOS = [
    "Quantos clientes temos em cada região?",
    "Quais são os 5 produtos mais vendidos em quantidade?",
    "Qual foi o faturamento por mês em 2025?",
    "Qual é o melhor cliente?",
    "Apague todos os pedidos cancelados",
]

st.set_page_config(page_title="Assistente de Dados", page_icon="📊", layout="wide")
cfg = config.carregar()
logs.configurar(cfg.log_path)


@st.cache_resource
def preparar() -> tuple[Assistente, ClienteOllama]:
    if not cfg.db_path.exists():
        dados.gerar_banco(cfg.db_path)
    cliente = ClienteOllama(cfg.ollama_url, cfg.modelo, cfg.timeout_llm)
    assistente = Assistente(
        cliente, cfg.db_path, limite_linhas=cfg.limite_linhas, limite_instrucoes=cfg.limite_instrucoes
    )
    return assistente, cliente


assistente, cliente = preparar()

with st.sidebar:
    st.header("Configuração")
    if cliente.disponivel():
        st.success(f"Modelo pronto: {cfg.modelo}")
    else:
        st.error(
            f"Modelo {cfg.modelo} indisponível em {cfg.ollama_url}. "
            "Aguarde o download do modelo ou verifique o Ollama."
        )
    st.caption(f"Limite de linhas: {cfg.limite_linhas}")
    with st.expander("Esquema do banco"):
        st.code(dados.esquema_para_prompt(), language="sql")
    st.caption("Dados: UFs do IBGE (públicos) + loja fictícia (sintéticos).")

st.title("📊 Assistente de dados")
st.write(
    "Faça uma pergunta em português sobre os dados da loja. "
    "O assistente gera a consulta, verifica se ela é segura, executa e explica."
)

if "historico" not in st.session_state:
    st.session_state.historico = []

col1, col2 = st.columns([4, 1])
with col2:
    exemplo = st.selectbox("Exemplos", [""] + EXEMPLOS, label_visibility="collapsed")
with col1:
    pergunta = st.text_input(
        "Pergunta", value=exemplo, placeholder="Ex.: Quantos pedidos foram cancelados em 2025?"
    )

if st.button("Perguntar", type="primary") and pergunta.strip():
    with st.spinner("Gerando e verificando a consulta..."):
        st.session_state.historico.insert(0, assistente.responder(pergunta.strip()))


def mostrar_grafico(df: pd.DataFrame) -> None:
    numericas = df.select_dtypes("number").columns
    if len(df) > 1 and len(df.columns) == 2 and len(numericas) == 1 and df.columns[0] not in numericas:
        st.bar_chart(df.set_index(df.columns[0]))


for resp in st.session_state.historico:
    st.divider()
    st.subheader(resp.pergunta)
    if resp.status == "ok":
        st.code(resp.sql, language="sql")
        st.info(f"**O que essa consulta faz:** {resp.explicacao}")
        df = pd.DataFrame(resp.linhas, columns=resp.colunas)
        st.dataframe(df)
        if resp.truncado:
            st.warning(f"Resultado cortado em {len(resp.linhas)} linhas.")
        mostrar_grafico(df)
        with st.expander("Plano de execução"):
            st.write(resp.plano)
    elif resp.status == "ambigua":
        st.warning(f"🤔 Preciso de um esclarecimento: {resp.mensagem}")
    elif resp.status == "recusada":
        st.error(f"🚫 Pedido recusado pelo modelo: {resp.mensagem}")
    elif resp.status == "bloqueada":
        st.error(f"🛡️ Consulta bloqueada ({resp.camada_bloqueio}): {resp.mensagem}")
        if resp.sql:
            st.code(resp.sql, language="sql")
    else:
        st.error(f"⚠️ Não foi possível responder: {resp.mensagem}")
        if resp.sql:
            st.code(resp.sql, language="sql")
    st.caption(
        f"id {resp.id} · {resp.tempo_ms / 1000:.1f} s · {resp.tentativas} tentativa(s) · "
        f"{resp.tokens_entrada + resp.tokens_saida} tokens"
    )
