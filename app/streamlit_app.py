"""ChargeGrid Assistant — interface Streamlit (Sprint 04).

Consome o pipeline RAG completo (`src/chain/builder.conversar`): ChromaDB +
nomic-embed-text, prompt RAG versionado, grounding e citação de fonte. Toda
resposta mostra as fontes citadas (documento, seção e página) logo abaixo do
texto, resolvidas a partir dos metadados dos trechos recuperados — não do texto
gerado pelo modelo.

Duas abas:
- **Chat**: conversa com memória, com um dos dois modelos (Gemma 4 via Ollama
  Cloud ou Qwen 3.8 via Groq) e a versão do prompt RAG escolhida.
- **Multi-provider**: a mesma pergunta para os dois modelos × duas versões do
  prompt RAG, lado a lado (bônus da Sprint 04).

Execução (a partir da raiz do projeto):
    streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st  # noqa: E402

from src.chain.builder import PROVIDERS, conversar, modelo_padrao  # noqa: E402
from src.chain.memoria import limpar_sessao, obter_sessao_existente, total_tokens  # noqa: E402
from src.chain.multi_provider import VERSOES_PADRAO, consultar_multi  # noqa: E402
from src.config import load_settings  # noqa: E402
from src.rag.prompt_rag import VERSOES  # noqa: E402

st.set_page_config(
    page_title="ChargeGrid Assistant", page_icon=str(ROOT_DIR / "assets" / "goodwe_logo.png"), layout="wide"
)

settings = load_settings()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []


def _fontes_payload(resposta) -> list[dict]:
    return [
        {"n": c.n, "titulo": c.titulo, "secao": c.secao, "pagina": c.pagina}
        for c in resposta.citacoes
    ]


def _chunks_payload(resposta) -> list[dict]:
    return [
        {"n": c.n, "citacao": c.citacao, "score": c.score, "suspeito": c.suspeito, "texto": c.texto}
        for c in resposta.chunks
    ]


def mostrar_fontes(fontes: list[dict], fora_da_base: bool, bloqueado: bool) -> None:
    """Citação visível: sempre presente abaixo da resposta."""
    if bloqueado:
        st.caption("Bloqueado pelo guardrail antes de consultar a base.")
        return
    if fora_da_base:
        st.warning("Informação não encontrada na base de conhecimento. Nenhuma fonte citada.")
        return
    if not fontes:
        st.caption("Nenhuma fonte citada pelo modelo nesta resposta.")
        return
    linhas = "\n".join(f"- **[{f['n']}] {f['titulo']}** — {f['secao']} · p. {f['pagina']}" for f in fontes)
    st.info(f"**Fontes**\n\n{linhas}")


def mostrar_trechos(chunks: list[dict]) -> None:
    with st.expander(f"Trechos recuperados ({len(chunks)})"):
        if not chunks:
            st.caption("Nenhum trecho recuperado (pergunta barrada antes da busca ou abaixo do limiar configurado).")
        for c in chunks:
            alerta = " · instrução embutida removida pela sanitização" if c["suspeito"] else ""
            st.markdown(f"**[{c['n']}] {c['citacao']}** · score {c['score']:.3f}{alerta}")
            st.text(c["texto"][:1200])


# --------------------------------------------------------------------------- sidebar
with st.sidebar:
    st.image(str(ROOT_DIR / "assets" / "goodwe_logo.png"), width="stretch")
    st.title("ChargeGrid Assistant")
    st.caption("GoodWe · Sprint 04 — RAG com ChromaDB")

    provider = st.radio("Modelo", options=list(PROVIDERS), format_func=lambda p: PROVIDERS[p])
    modelo = modelo_padrao(provider, settings)
    st.caption(f"`{modelo}`")

    versoes = list(VERSOES)
    prompt_rag = st.selectbox(
        "Prompt RAG",
        versoes,
        index=versoes.index(settings.rag_prompt_version) if settings.rag_prompt_version in versoes else len(versoes) - 1,
        help="Versões avaliadas com RAGAS — ver evals/SCORES_POR_ITERACAO.md.",
    )
    st.caption(VERSOES[prompt_rag].resumo)

    if st.button("Limpar conversa", width="stretch"):
        limpar_sessao(st.session_state.session_id)
        st.session_state.mensagens = []
        st.rerun()

    with st.expander("Avançado"):
        k = st.slider("k (trechos recuperados)", 1, 10, settings.rag_k)
        modos_busca = ["hibrida_expandida", "hibrida", "vetorial"]
        busca = st.selectbox(
            "Busca",
            modos_busca,
            index=modos_busca.index(settings.rag_busca) if settings.rag_busca in modos_busca else 0,
            help="hibrida_expandida: vetorial + BM25 com expansão de consulta (padrão, iteração 5).",
        )
        ignorar_guardrails = st.toggle("Desativar guardrails (debug)", value=False)
        st.caption(
            f"temperature={settings.temperature} · top_p={settings.top_p} · max_tokens={settings.max_tokens} · "
            f"limiar={settings.rag_limiar_relevancia} · embeddings=nomic-embed-text ({settings.embeddings_backend})"
        )
        historico = obter_sessao_existente(st.session_state.session_id)
        tokens_atual = total_tokens(historico) if historico else 0
        st.caption(f"Memória: {tokens_atual}/{settings.memoria_limite_tokens} tokens")
        st.progress(min(tokens_atual / settings.memoria_limite_tokens, 1.0))
        if historico and historico.moving_summary_buffer:
            st.caption("Resumo atual da conversa:")
            st.text(historico.moving_summary_buffer)

    if not settings.ollama_api_key:
        st.error("OLLAMA_API_KEY não configurada no .env.")
    if provider == "groq" and not settings.groq_api_key:
        st.error("GROQ_API_KEY não configurada no .env.")

aba_chat, aba_multi = st.tabs(["Chat", "Multi-provider (2 modelos x 2 prompts)"])

# --------------------------------------------------------------------------- chat
with aba_chat:
    for msg in st.session_state.mensagens:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                mostrar_fontes(msg["fontes"], msg["fora_da_base"], msg["bloqueado"])
                st.caption(msg["meta"])
                mostrar_trechos(msg["chunks"])
                with st.expander("Detalhes técnicos"):
                    st.json(msg["estruturado"])

    entrada = st.chat_input("Pergunte sobre tarifas, regimento, Modbus/OCPP, carregador GoodWe...")
    if entrada:
        st.session_state.mensagens.append({"role": "user", "content": entrada})
        with st.chat_message("user"):
            st.markdown(entrada)

        with st.chat_message("assistant"):
            with st.spinner("Consultando a base de conhecimento..."):
                try:
                    resposta = conversar(
                        st.session_state.session_id, entrada, model=modelo, provider=provider,
                        ignorar_guardrails=ignorar_guardrails, prompt_rag_version=prompt_rag, k=k, busca=busca,
                    )
                except Exception as exc:  # noqa: BLE001 - erro de provider não pode derrubar a UI
                    st.error(f"Falha ao consultar {PROVIDERS[provider]}: {exc}")
                    st.stop()
            texto = resposta.resultado.justificativa
            fontes = _fontes_payload(resposta)
            chunks = _chunks_payload(resposta)
            meta = (
                f"{PROVIDERS[provider]} · prompt RAG {prompt_rag} · k={k} · busca {busca} · "
                f"decisão: {resposta.resultado.decisao.value} · {resposta.latencia_s:.2f}s"
            )
            estruturado = resposta.resultado.model_dump(mode="json")

            st.markdown(texto)
            mostrar_fontes(fontes, resposta.resultado.fora_da_base, resposta.bloqueado_por_guardrail)
            st.caption(meta)
            mostrar_trechos(chunks)
            with st.expander("Detalhes técnicos"):
                st.json(estruturado)

        st.session_state.mensagens.append({
            "role": "assistant", "content": texto, "fontes": fontes, "chunks": chunks, "meta": meta,
            "fora_da_base": resposta.resultado.fora_da_base, "bloqueado": resposta.bloqueado_por_guardrail,
            "estruturado": estruturado,
        })

# --------------------------------------------------------------------------- multi-provider
with aba_multi:
    st.markdown(
        "A mesma pergunta para **Gemma 4 (Ollama Cloud)** e **Qwen 3.8 (Groq)**, cada um com as versões "
        f"**{' e '.join(VERSOES_PADRAO)}** do prompt RAG. A busca é feita uma vez e os mesmos trechos vão "
        "para as quatro combinações — a diferença entre as respostas vem só do modelo e do prompt."
    )
    with st.form("multi"):
        pergunta_multi = st.text_input("Pergunta", placeholder="Ex.: Qual a tarifa para veículos de frota?")
        enviar = st.form_submit_button("Consultar as 4 combinações")
    if enviar and pergunta_multi.strip():
        with st.spinner("Consultando os dois modelos com os dois prompts..."):
            chunks_multi, resultados = consultar_multi(pergunta_multi.strip(), k=k)
        colunas = st.columns(len(VERSOES_PADRAO))
        for indice, r in enumerate(resultados):
            with colunas[indice % len(colunas)]:
                st.subheader(r.rotulo)
                st.caption(f"`{r.modelo}`")
                if r.erro:
                    st.error(r.erro)
                    continue
                st.markdown(r.resposta.resultado.justificativa)
                mostrar_fontes(
                    _fontes_payload(r.resposta), r.resposta.resultado.fora_da_base, r.resposta.bloqueado_por_guardrail
                )
                st.caption(f"{r.resposta.latencia_s:.2f}s · decisão: {r.resposta.resultado.decisao.value}")
                st.divider()
        if chunks_multi:
            mostrar_trechos([
                {"n": c.n, "citacao": c.citacao, "score": c.score, "suspeito": c.suspeito, "texto": c.texto}
                for c in chunks_multi
            ])
