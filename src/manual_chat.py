"""Reconstrução do núcleo "manual" das Sprints 1/2 — a versão "antes" do comparativo.

Propositalmente SEM LangChain, SEM schema Pydantic, SEM limite de tokens e SEM
guardrail dedicado — é fiel ao que existia nas Sprints 1/2 (lista de mensagens
concatenada à mão + system prompt em texto corrido), só trocando o SDK da Groq
pelo client da Ollama para que o comparativo do Bloco D isole a variável certa
(arquitetura do código), não o modelo por trás.

Usado por `evals/run_eval.py` como baseline "Sprints 1/2 (legado)".
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from ollama import Client

from src.config import PROMPTS_DIR, load_settings
from src.tokens import contar_tokens

_SYSTEM_PROMPT_V1 = None


def _carregar_system_prompt_v1() -> str:
    global _SYSTEM_PROMPT_V1
    if _SYSTEM_PROMPT_V1 is None:
        conteudo = (PROMPTS_DIR / "system_prompt_v1.md").read_text(encoding="utf-8")
        inicio = conteudo.index("```text") + len("```text")
        fim = conteudo.index("```", inicio)
        _SYSTEM_PROMPT_V1 = conteudo[inicio:fim].strip()
    return _SYSTEM_PROMPT_V1


@dataclass
class RespostaLegada:
    texto: str
    latencia_s: float
    tokens_entrada: int
    tokens_saida: int


# Histórico cru por sessão, exatamente como nas Sprints 1/2: lista de dicts
# {"role": ..., "content": ...} sem nenhuma poda por tamanho/tokens.
_HISTORICOS: dict[str, list[dict]] = {}


def _obter_cliente() -> Client:
    settings = load_settings()
    return Client(
        host=settings.ollama_host,
        headers={"Authorization": f"Bearer {settings.ollama_api_key}"},
    )


def conversar_legado(session_id: str, entrada: str, model: str | None = None) -> RespostaLegada:
    settings = load_settings()
    modelo = model or settings.model_primary

    historico = _HISTORICOS.setdefault(session_id, [])
    if not historico:
        historico.append({"role": "system", "content": _carregar_system_prompt_v1()})

    historico.append({"role": "user", "content": entrada})

    cliente = _obter_cliente()
    inicio = time.perf_counter()
    resposta = cliente.chat(
        model=modelo,
        messages=historico,
        options={"temperature": settings.temperature, "num_predict": settings.max_tokens},
    )
    latencia = time.perf_counter() - inicio

    texto = resposta["message"]["content"]
    historico.append({"role": "assistant", "content": texto})

    tokens_entrada = sum(contar_tokens(m["content"]) for m in historico[:-1])
    tokens_saida = contar_tokens(texto)

    return RespostaLegada(
        texto=texto,
        latencia_s=latencia,
        tokens_entrada=tokens_entrada,
        tokens_saida=tokens_saida,
    )


def limpar_sessao_legada(session_id: str) -> None:
    _HISTORICOS.pop(session_id, None)
