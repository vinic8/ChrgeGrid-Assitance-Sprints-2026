"""ChargeGrid Assistant — interface Streamlit (Sprint 03).

Roda a chain LCEL (src/chain/builder.py) sobre dois providers (Ollama Cloud e
Groq — ver `src/chain/builder.PROVIDERS`), com RAG sobre `knowledge/*.md`
(src/rag/indexer.py) para respostas ancoradas em documento real (OCPP, Modbus,
tarifação dinâmica, specs do charger). A interface fica enxuta por padrão: só
o chat e o essencial; detalhes técnicos (JSON estruturado, guardrails,
comparação com a versão legada, memória) ficam atrás de expanders.
"""
from __future__ import annotations

import uuid

import streamlit as st

from src.chain.builder import PROVIDERS, conversar, modelo_padrao
from src.chain.memoria import limpar_sessao, obter_sessao_existente, total_tokens
from src.config import load_settings
from src.manual_chat import conversar_legado, limpar_sessao_legada

st.set_page_config(page_title="ChargeGrid Assistant", page_icon="⚡", layout="centered")

settings = load_settings()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []  # [{"role", "content", "estruturado"?, "meta"?, "legado"?}]

with st.sidebar:
    st.image("assets/goodwe_logo.png", width="stretch")
    st.title("⚡ ChargeGrid Assistant")
    st.caption("GoodWe · Sprint 03 — LangChain LCEL")

    provider = st.radio(
        "Modelo",
        options=list(PROVIDERS.keys()),
        format_func=lambda p: PROVIDERS[p],
        help="Comparativo multi-provider do Bloco B: Ollama Cloud vs. Groq.",
    )
    modelo = modelo_padrao(provider, settings)
    st.caption(f"`{modelo}`")

    if st.button("Limpar conversa", width="stretch"):
        limpar_sessao(st.session_state.session_id)
        limpar_sessao_legada(st.session_state.session_id)
        st.session_state.mensagens = []
        st.rerun()

    with st.expander("Avançado"):
        modo_comparativo = st.toggle(
            "Comparar com versão legada (Sprints 1/2)",
            value=False,
            help="Roda a mesma mensagem na chain LCEL e na versão manual (f-strings, sem schema).",
        )
        ignorar_guardrails = st.toggle("Desativar guardrails (debug)", value=False)

        historico = obter_sessao_existente(st.session_state.session_id)
        tokens_atual = total_tokens(historico) if historico else 0
        st.caption(
            f"Memória: ConversationSummaryBufferMemory (LangChain) · "
            f"{tokens_atual}/{settings.memoria_limite_tokens} tokens"
        )
        st.progress(min(tokens_atual / settings.memoria_limite_tokens, 1.0))
        resumo_atual = historico.moving_summary_buffer if historico else ""
        if resumo_atual:
            st.caption("Resumo atual da conversa:")
            st.text(resumo_atual)

    if provider == "ollama" and not settings.ollama_api_key:
        st.error("OLLAMA_API_KEY não configurada no .env.")
    if provider == "groq" and not settings.groq_api_key:
        st.error("GROQ_API_KEY não configurada no .env.")

for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("meta"):
            st.caption(msg["meta"])
        if msg.get("fontes_rag"):
            st.caption("📚 " + ", ".join(msg["fontes_rag"]))
        if msg.get("estruturado") is not None:
            with st.expander("Detalhes técnicos"):
                st.json(msg["estruturado"])
        if msg.get("legado") is not None:
            with st.expander("Versão legada (Sprints 1/2)"):
                st.markdown(msg["legado"]["texto"])

entrada = st.chat_input("Pergunte sobre potência, faturamento ou diagnóstico de um carregador...")

if entrada:
    st.session_state.mensagens.append({"role": "user", "content": entrada})
    with st.chat_message("user"):
        st.markdown(entrada)

    with st.chat_message("assistant"):
        with st.spinner("Consultando ChargeGrid Assistant..."):
            resposta = conversar(
                st.session_state.session_id,
                entrada,
                model=modelo,
                provider=provider,
                ignorar_guardrails=ignorar_guardrails,
            )
        st.markdown(resposta.resultado.justificativa)

        badge = "🚫 guardrail" if resposta.bloqueado_por_guardrail else f"✅ {PROVIDERS[provider]}"
        meta = f"{badge} · decisão: {resposta.resultado.decisao.value} · {resposta.latencia_s:.2f}s"
        st.caption(meta)
        if resposta.fontes_rag:
            st.caption("📚 " + ", ".join(resposta.fontes_rag))

        estruturado = resposta.resultado.model_dump(mode="json")
        with st.expander("Detalhes técnicos"):
            st.json(estruturado)
            st.caption(
                f"tokens entrada≈{resposta.tokens_entrada} · tokens saída≈{resposta.tokens_saida}"
            )

        legado_dict = None
        if modo_comparativo:
            # A versão legada sempre roda via Ollama (settings.model_primary) — ela
            # reconstrói a arquitetura das Sprints 1/2, não o provider selecionado no
            # chat atual. Passar o modelo do Provider B (Groq) aqui quebraria (o
            # cliente interno é sempre o da Ollama Cloud).
            with st.spinner("Rodando versão legada (Sprints 1/2) para comparação..."):
                legado = conversar_legado(f"{st.session_state.session_id}-legado", entrada)
            legado_dict = {"texto": legado.texto}
            with st.expander("Versão legada (Sprints 1/2)"):
                st.caption(f"Sempre via Ollama Cloud (`{settings.model_primary}`), independente do provider acima.")
                st.markdown(legado.texto)
                st.caption(
                    f"latência: {legado.latencia_s:.2f}s · "
                    f"tokens entrada: {legado.tokens_entrada} · tokens saída: {legado.tokens_saida}"
                )

    st.session_state.mensagens.append(
        {
            "role": "assistant",
            "content": resposta.resultado.justificativa,
            "meta": meta,
            "fontes_rag": resposta.fontes_rag,
            "estruturado": estruturado,
            "legado": legado_dict,
        }
    )
