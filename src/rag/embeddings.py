"""Etapa 3 do pipeline RAG: embeddings `nomic-embed-text`.

O enunciado da Sprint 04 pede `nomic-embed-text` servido pela Ollama Cloud. Na
prática, a Ollama Cloud **não serve modelos de embedding pela API**: testamos
`nomic-embed-text` e `embeddinggemma` em `https://ollama.com/api/embed` com a
mesma API key que funciona para o chat (`gemma4:cloud`) e as duas chamadas
retornam HTTP 401 (o catálogo cloud só lista modelos de chat — mesmo achado da
Sprint 03). Por isso há dois backends, escolhidos por `EMBEDDINGS_BACKEND`:

- `fastembed` (padrão): o MESMO modelo — `nomic-ai/nomic-embed-text-v1.5`, que é
  o que a Ollama distribui como `nomic-embed-text` — rodando localmente em ONNX
  via FastEmbed (CPU, sem API key; ~520 MB baixados uma única vez para
  `data/.fastembed_cache/`).
- `ollama`: `OllamaEmbeddings(model="nomic-embed-text")` apontando para
  `OLLAMA_EMBEDDINGS_HOST` (ex.: um Ollama local com `ollama pull
  nomic-embed-text`, ou a Ollama Cloud caso o endpoint seja liberado para a
  chave). Mesmo modelo e mesma dimensão (768) — só muda quem executa.

Os dois backends ficam em coleções Chroma separadas (ver `vector_store.py`), para
nunca misturar vetores gerados por runtimes diferentes.

Detalhe do nomic-embed-text: o modelo foi treinado com prefixos de tarefa —
`search_document: ` para os textos indexados e `search_query: ` para a pergunta.
Sem eles, a similaridade pergunta↔trecho cai visivelmente (é a recomendação
oficial do modelo). `EmbeddingsNomic` aplica os prefixos nos dois backends.
"""
from __future__ import annotations

from functools import lru_cache

from langchain_core.embeddings import Embeddings

from src.config import FASTEMBED_CACHE_DIR, load_settings

MODELO_FASTEMBED = "nomic-ai/nomic-embed-text-v1.5"


class EmbeddingsNomic(Embeddings):
    """Aplica os prefixos de tarefa do nomic-embed-text sobre qualquer backend."""

    def __init__(self, base: Embeddings, nome: str):
        self.base = base
        self.nome = nome

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.base.embed_documents([f"search_document: {t}" for t in texts])

    def embed_query(self, text: str) -> list[float]:
        return self.base.embed_query(f"search_query: {text}")


def _fastembed() -> Embeddings:
    from langchain_community.embeddings import FastEmbedEmbeddings

    FASTEMBED_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return FastEmbedEmbeddings(model_name=MODELO_FASTEMBED, cache_dir=str(FASTEMBED_CACHE_DIR))


def _ollama() -> Embeddings:
    from langchain_ollama import OllamaEmbeddings

    settings = load_settings()
    headers = {"Authorization": f"Bearer {settings.ollama_api_key}"} if settings.ollama_api_key else {}
    return OllamaEmbeddings(
        model=settings.embeddings_model,
        base_url=settings.ollama_embeddings_host,
        client_kwargs={"headers": headers, "timeout": 60},
    )


@lru_cache(maxsize=2)
def obter_embeddings(backend: str | None = None) -> EmbeddingsNomic:
    backend = backend or load_settings().embeddings_backend
    if backend == "ollama":
        return EmbeddingsNomic(_ollama(), nome=f"ollama/{load_settings().embeddings_model}")
    return EmbeddingsNomic(_fastembed(), nome=f"fastembed/{MODELO_FASTEMBED}")
