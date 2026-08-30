"""Contagem de tokens (aula 04 — medição de tokens / context engineering).

gpt-oss e qwen3.5 não têm um tokenizer público no tiktoken (que só cobre a família
OpenAI). Usamos `o200k_base` (tokenizer do GPT-4o) como aproximação — é a mesma
prática usada no mercado para "orçar" tokens de modelos open-weight sem tokenizer
próprio disponível em Python. Documentado aqui para não virar suposição escondida:
o número é uma estimativa de custo/orçamento, não a contagem exata do provider.
"""
from __future__ import annotations

from functools import lru_cache

import tiktoken


@lru_cache(maxsize=1)
def _encoder() -> tiktoken.Encoding:
    return tiktoken.get_encoding("o200k_base")


def contar_tokens(texto: str) -> int:
    if not texto:
        return 0
    return len(_encoder().encode(texto))
