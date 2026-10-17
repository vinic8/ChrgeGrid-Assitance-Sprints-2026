"""Compatibilidade do RAGAS 0.4.x com o LangChain 1.x deste projeto.

`ragas.llms.base` importa `ChatVertexAI`/`VertexAI` de módulos do
`langchain_community` que foram removidos na linha 0.4 do community (o VertexAI
foi para o pacote `langchain-google-vertexai`). O import falha antes de
qualquer métrica rodar (`ModuleNotFoundError: langchain_community.chat_models.vertexai`),
mesmo sem usar VertexAI. Como o RAGAS só usa essas classes em checagens de
`isinstance`, registrar módulos vazios com classes "dummy" é suficiente — e
nenhuma chamada passa por elas aqui (o juiz é o Gemma via `ChatOllama`).

Importar este módulo ANTES de `import ragas`.
"""
from __future__ import annotations

import sys
import types
import warnings

for _modulo, _classe in (
    ("langchain_community.chat_models.vertexai", "ChatVertexAI"),
    ("langchain_community.llms.vertexai", "VertexAI"),
):
    try:
        __import__(_modulo)
    except ImportError:
        _fake = types.ModuleType(_modulo)
        setattr(_fake, _classe, type(_classe, (), {}))
        sys.modules[_modulo] = _fake

# Avisos de depreciação do próprio RAGAS (métricas legadas) poluem o log do eval.
warnings.filterwarnings("ignore", category=DeprecationWarning, module="ragas")
