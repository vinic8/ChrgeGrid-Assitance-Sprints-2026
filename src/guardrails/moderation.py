"""Guardrail anti-jailbreak / prompt injection.

Também roda antes da chain, por padrão de regex sobre a mensagem do usuário.
Não substitui o bloco <seguranca> do system prompt ativo — é uma segunda camada
("defesa em profundidade"): mesmo que o modelo eventualmente ceda a uma injeção
bem elaborada, esta checagem barra os padrões mais comuns antes da chamada ao LLM.
Na prática, o próprio prompt (a partir da v3) já resiste bem sozinho — ver os
testes documentados em `docs/RELATORIO_EVOLUCAO.txt` — mas este regex continua
valendo como primeira camada, mais barata (zero chamada ao LLM) para os padrões
mais óbvios e previsíveis de jailbreak.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

PADROES_JAILBREAK = [
    r"ignore (as|todas as|suas) instru[cç][aã]o",
    r"esque[çc]a (o|as) (seu papel|instru[cç][oõ]es|regras)",
    r"modo desenvolvedor",
    r"\bdan\b.{0,20}(mode|modo)",
    r"finja (ser|que [ée])",
    r"aja como (se|um)(?! operador)",
    r"revele (o|seu) (system prompt|prompt (interno|do sistema)|suas instru[cç][oõ]es)",
    r"mostre (o|seu) (system prompt|prompt (interno|do sistema))",
    r"desative (suas|os) (regras|restri[cç][oõ]es|guardrails)",
]

_PADROES_COMPILADOS = [re.compile(p, re.IGNORECASE) for p in PADROES_JAILBREAK]


@dataclass
class ResultadoModeracao:
    seguro: bool
    padrao_detectado: str | None = None


def checar_jailbreak(mensagem: str) -> ResultadoModeracao:
    for padrao in _PADROES_COMPILADOS:
        if padrao.search(mensagem):
            return ResultadoModeracao(seguro=False, padrao_detectado=padrao.pattern)
    return ResultadoModeracao(seguro=True)


MENSAGEM_RECUSA_PADRAO = (
    "Não posso ignorar minhas diretrizes de operação nem revelar instruções internas. "
    "Posso ajudar com orquestração de potência, faturamento ou diagnóstico de carregadores GoodWe — "
    "como posso ajudar dentro desse escopo?"
)
