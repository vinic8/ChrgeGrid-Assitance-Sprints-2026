"""Núcleo conversacional em LCEL: prompt RAG | llm | parser (Sprint 04).

Pipeline completo de uma pergunta (`conversar`):

    guardrails (escopo, jailbreak)                        src/guardrails/
      -> recuperação top-k no ChromaDB + sanitização        src/rag/retriever.py
      -> prompt RAG versionado (persona v7 + regras RAG vN) src/rag/prompt_rag.py
      -> LLM (Gemma via Ollama Cloud | Qwen via Groq)
      -> PydanticOutputParser (ConsultaRecarga)            src/schemas/
      -> citações resolvidas pelos metadados dos chunks    (documento, seção, página)

Multi-provider: a mesma chain roda sobre dois providers, selecionados por `provider`:
- **Provider A** — Ollama Cloud, modelo `MODEL_PRIMARY` (`gemma4:cloud`).
- **Provider B** — Groq, modelo `MODEL_GROQ` (`qwen/qwen3.8-27b`).

Parâmetros de geração (documentados em `docs/relatorio_modelos.md`):
`temperature` (padrão 0), `top_p`, `max_tokens` e `k` (top-k da recuperação), todos
vindos do .env e sobrescrevíveis por chamada (usado pelo eval e pela UI).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from src.chain.memoria import mensagens_para_prompt, obter_historico, registrar_turno, total_tokens
from src.config import load_settings
from src.guardrails.moderation import MENSAGEM_RECUSA_PADRAO, checar_jailbreak
from src.guardrails.scope_validator import checar_escopo
from src.rag.prompt_rag import formatar_contexto, montar_prompt
from src.rag.retriever import ChunkRecuperado, recuperar
from src.schemas import ConsultaRecarga, Decisao
from src.tokens import contar_tokens

_parser = PydanticOutputParser(pydantic_object=ConsultaRecarga)

PROVIDERS = {
    "ollama": "Gemma 4 — Ollama Cloud",
    "groq": "Qwen 3.8 — Groq",
}


@dataclass
class RespostaChat:
    resultado: ConsultaRecarga
    latencia_s: float
    tokens_entrada: int
    tokens_saida: int
    bloqueado_por_guardrail: bool
    provider: str = "ollama"
    modelo: str = ""
    prompt_rag_version: str = ""
    chunks: list[ChunkRecuperado] = field(default_factory=list)  # tudo o que foi recuperado
    citacoes: list[ChunkRecuperado] = field(default_factory=list)  # o que o modelo citou (ids válidos)

    @property
    def fontes_rag(self) -> list[str]:
        """Nomes dos documentos citados (compatível com a Sprint 03)."""
        vistos: list[str] = []
        for c in self.citacoes:
            if c.documento not in vistos:
                vistos.append(c.documento)
        return vistos

    @property
    def contextos(self) -> list[str]:
        """Textos recuperados enviados ao modelo (entrada do RAGAS)."""
        return [c.texto for c in self.chunks]


def modelo_padrao(provider: str, settings=None) -> str:
    """Modelo default de cada provider, conforme o .env."""
    settings = settings or load_settings()
    return settings.model_groq if provider == "groq" else settings.model_primary


_TIMEOUT_S = 90  # sem timeout, uma chamada travada no provider prendia a UI/eval
# indefinidamente (achado real da Sprint 03, relatório Problema 6).


def montar_llm(
    model: str | None = None,
    provider: str = "ollama",
    temperature: float | None = None,
    top_p: float | None = None,
    max_tokens: int | None = None,
) -> BaseChatModel:
    settings = load_settings()
    temperature = settings.temperature if temperature is None else temperature
    top_p = settings.top_p if top_p is None else top_p
    max_tokens = max_tokens or settings.max_tokens
    if provider == "groq":
        return ChatGroq(
            model=model or settings.model_groq,
            api_key=settings.groq_api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            model_kwargs={"top_p": top_p},
            request_timeout=_TIMEOUT_S,
            # Groq (plano gratuito) limita a 8.000 tokens/min; o cliente espera e
            # tenta de novo em HTTP 429 em vez de derrubar a conversa.
            max_retries=6,
        )
    return ChatOllama(
        model=model or settings.model_primary,
        base_url=settings.ollama_host,
        temperature=temperature,
        top_p=top_p,
        num_predict=max_tokens,
        client_kwargs={
            "headers": {"Authorization": f"Bearer {settings.ollama_api_key}"},
            "timeout": _TIMEOUT_S,
        },
    )


def _resposta_bloqueio(justificativa: str) -> ConsultaRecarga:
    return ConsultaRecarga(decisao=Decisao.NAO_APLICAVEL, justificativa=justificativa)


def construir_chain(llm: BaseChatModel, prompt_rag_version: str | None = None):
    """Chain LCEL `prompt RAG | llm | parser`.

    Entrada: {"entrada", "historico", "contexto"} — o `contexto` já vem recuperado e
    formatado por `conversar` (assim a mesma lista de chunks alimenta o prompt, a UI
    e o eval, sem recuperar duas vezes). O último passo tenta validar contra
    `ConsultaRecarga` e, se a saída vier malformada, pede uma correção pontual ao
    próprio LLM antes de desistir (Sprint 03, relatório Problema 1).
    """
    prompt = montar_prompt(prompt_rag_version, _parser.get_format_instructions())

    def _parse_com_correcao(ai_message: AIMessage) -> ConsultaRecarga:
        texto = ai_message.content
        try:
            return _parser.parse(texto)
        except Exception as primeiro_erro:  # noqa: BLE001 - queremos capturar qualquer falha de parsing
            prompt_correcao = (
                "A saída abaixo deveria ser um JSON válido conforme as instruções de "
                f"formato, mas falhou na validação com o erro: {primeiro_erro}\n\n"
                f"Instruções de formato:\n{_parser.get_format_instructions()}\n\n"
                f"Saída original:\n{texto}\n\n"
                "Responda APENAS com o JSON corrigido, sem texto adicional."
            )
            correcao = llm.invoke(prompt_correcao)
            return _parser.parse(correcao.content)

    # Retry com backoff exponencial: a Ollama Cloud responde HTTP 429 ("too many
    # concurrent requests") quando há chamadas simultâneas acima do limite do plano
    # (ex.: modo multi-provider) e a Groq responde 429 ao estourar tokens/minuto.
    llm_com_retry = llm.with_retry(stop_after_attempt=5, wait_exponential_jitter=True)
    return prompt | llm_com_retry | RunnableLambda(_parse_com_correcao)


def _consulta_de_busca(entrada: str, historico) -> str:
    """Pergunta usada na busca vetorial.

    Perguntas de follow-up curtas ("e para frota?", "e se for às 19h?") não têm
    vocabulário suficiente para recuperar o trecho certo sozinhas; nesses casos a
    busca usa também a última pergunta do operador.
    """
    if len(entrada.split()) >= 8 or historico is None:
        return entrada
    anteriores = [m.content for m in historico.chat_memory.messages if isinstance(m, HumanMessage)]
    return f"{anteriores[-1]} {entrada}" if anteriores else entrada


def _resolver_citacoes(resultado: ConsultaRecarga, chunks: list[ChunkRecuperado]) -> list[ChunkRecuperado]:
    por_id = {c.n: c for c in chunks}
    citados, vistos = [], set()
    for n in resultado.fontes_citadas:
        if n in por_id and n not in vistos:
            citados.append(por_id[n])
            vistos.add(n)
    return citados


def conversar(
    session_id: str,
    entrada: str,
    model: str | None = None,
    provider: str = "ollama",
    ignorar_guardrails: bool = False,
    prompt_rag_version: str | None = None,
    k: int | None = None,
    estrategia: str | None = None,
    busca: str | None = None,
    limiar: float | None = None,
    chunks: list[ChunkRecuperado] | None = None,
) -> RespostaChat:
    """Ponto de entrada usado pela UI, pelo eval RAGAS e pelo modo multi-provider.

    `chunks` permite injetar uma recuperação já feita (o modo multi-provider recupera
    uma vez para todas as combinações; o teste de prompt injection injeta um
    documento adulterado).
    """
    settings = load_settings()
    prompt_rag_version = prompt_rag_version or settings.rag_prompt_version
    modelo = model or modelo_padrao(provider, settings)
    llm = montar_llm(modelo, provider)
    historico = obter_historico(session_id, settings.memoria_limite_tokens, llm)
    inicio = time.perf_counter()

    def _bloqueio(justificativa: str) -> RespostaChat:
        resultado = _resposta_bloqueio(justificativa)
        registrar_turno(historico, entrada, resultado.justificativa)
        return RespostaChat(
            resultado=resultado,
            latencia_s=time.perf_counter() - inicio,
            tokens_entrada=contar_tokens(entrada),
            tokens_saida=contar_tokens(resultado.justificativa),
            bloqueado_por_guardrail=True,
            provider=provider,
            modelo=modelo,
            prompt_rag_version=prompt_rag_version,
        )

    if not ignorar_guardrails:
        if not checar_jailbreak(entrada).seguro:
            return _bloqueio(MENSAGEM_RECUSA_PADRAO)
        escopo = checar_escopo(entrada)
        if not escopo.dentro_do_escopo:
            return _bloqueio(
                f"{escopo.motivo} Posso ajudar com orquestração de potência, faturamento "
                "ou diagnóstico de carregadores GoodWe."
            )

    if chunks is None:
        chunks = recuperar(
            _consulta_de_busca(entrada, historico), k=k, estrategia=estrategia, limiar=limiar, busca=busca
        )
    contexto = formatar_contexto(chunks, prompt_rag_version)
    mensagens_historico = mensagens_para_prompt(historico)
    tokens_contexto_previo = total_tokens(historico) + contar_tokens(contexto)

    chain = construir_chain(llm, prompt_rag_version)
    resultado: ConsultaRecarga = chain.invoke(
        {"entrada": entrada, "historico": mensagens_historico, "contexto": contexto}
    )
    registrar_turno(historico, entrada, resultado.justificativa)

    return RespostaChat(
        resultado=resultado,
        latencia_s=time.perf_counter() - inicio,
        tokens_entrada=contar_tokens(entrada) + tokens_contexto_previo,
        tokens_saida=contar_tokens(resultado.justificativa),
        bloqueado_por_guardrail=False,
        provider=provider,
        modelo=modelo,
        prompt_rag_version=prompt_rag_version,
        chunks=chunks,
        citacoes=_resolver_citacoes(resultado, chunks),
    )
