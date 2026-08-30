"""Guardrail de escopo: recusa perguntas fora do domínio ChargeGrid/GoodWe.

Roda ANTES da chain (barato, sem chamada ao LLM) — evita gastar tokens/latência
em algo que já sabemos que deve ser recusado. Isso é intencionalmente uma
heurística leve de palavras-chave, não um classificador: o objetivo é filtrar
os casos óbvios; ambiguidades ficam para o próprio LLM decidir usando o bloco
<escopo> do system prompt ativo (ver `SYSTEM_PROMPT_VERSION` no .env).
"""
from __future__ import annotations

from dataclasses import dataclass

PALAVRAS_DOMINIO = {
    "carregador", "carga", "recarga", "potencia", "potência", "kw", "kwh",
    "rede", "disjuntor", "modbus", "rs485", "faturamento", "tarifa", "fatura",
    "load balancing", "balanceamento", "eletroposto", "veiculo", "veículo",
    "sessao", "sessão", "ciclo", "goodwe", "chargegrid", "operador",
}

# Tópicos claramente fora de escopo que às vezes aparecem em pedidos de teste
# de guardrail — usados só para reforçar a recusa com um motivo mais específico.
# NOTA: "política" (bare) foi removido daqui de propósito - colidia com termos
# legítimos do próprio domínio ("política de tarifação", "política de preços",
# "política de descontos" - ver knowledge/politica_tarifaria.md), bloqueando por
# engano perguntas de faturamento (achado real do eval, caso R3). "eleição" já
# cobre o caso mais comum de conteúdo político genérico sem essa ambiguidade.
TOPICOS_BLOQUEADOS = {
    "receita", "piada", "poema", "código python genérico", "futebol",
    "eleição", "religião", "conselho médico", "conselho jurídico",
}


@dataclass
class ResultadoEscopo:
    dentro_do_escopo: bool
    motivo: str | None = None


def checar_escopo(mensagem: str) -> ResultadoEscopo:
    texto = mensagem.lower()

    # Palavra de domínio tem precedência sobre o blocklist: uma mensagem que já
    # menciona vocabulário do produto (ex.: "tarifa", "faturamento") dificilmente
    # é o tipo de pedido genérico fora de escopo que o blocklist quer capturar -
    # e checar isso primeiro evita falsos positivos como o de "política" acima.
    if any(palavra in texto for palavra in PALAVRAS_DOMINIO):
        return ResultadoEscopo(dentro_do_escopo=True)

    if any(topico in texto for topico in TOPICOS_BLOQUEADOS):
        return ResultadoEscopo(
            dentro_do_escopo=False,
            motivo="Pedido fora do domínio ChargeGrid/GoodWe (assunto bloqueado por escopo).",
        )

    # Sem palavra-chave de domínio nem tópico bloqueado: ambíguo (ex.: saudação,
    # pergunta de follow-up curta como "e agora?"). Deixa passar para o LLM,
    # que tem o system prompt completo para decidir com mais contexto.
    return ResultadoEscopo(dentro_do_escopo=True)
