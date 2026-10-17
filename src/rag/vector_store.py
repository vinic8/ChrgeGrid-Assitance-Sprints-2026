"""Etapa 4 do pipeline RAG: vector store persistente (ChromaDB).

Substitui o FAISS da Sprint 03. O Chroma persiste em `data/chroma_db/` (SQLite +
índice HNSW) e é reaberto entre execuções sem reindexar. Distância: cosseno
(`hnsw:space=cosine`), então o score de relevância devolvido pelo LangChain é
`1 - distância`, no intervalo [0, 1] — é sobre ele que o retriever aplica o
limiar de relevância (`RAG_LIMIAR_RELEVANCIA`).

Uma coleção por combinação (estratégia de chunking × backend de embeddings), ex.:
`chargegrid_por_secao_fastembed`. Assim as iterações do eval (que comparam
estratégias) convivem no mesmo diretório sem uma sobrescrever a outra.

Reindexação automática: cada coleção guarda nos metadados uma "impressão
digital" (hash dos PDFs + parâmetros de chunking). Se um PDF da base mudar, a
próxima chamada a `obter_vector_store` detecta a diferença e reconstrói a
coleção sozinha — sem passo manual esquecido.

Uso direto:
    python -m src.rag.vector_store            # indexa só a coleção usada pela interface (.env)
    python -m src.rag.vector_store --todas    # indexa também as coleções das iterações 1 e 2
"""
from __future__ import annotations

import argparse
import hashlib
import json

from langchain_chroma import Chroma

from src.config import CHROMA_DIR, load_settings
from src.rag.chunking import ESTRATEGIAS, dividir
from src.rag.embeddings import obter_embeddings
from src.rag.loader import carregar_pdfs, listar_pdfs

_CACHE: dict[str, Chroma] = {}


def nome_colecao(estrategia: str, backend: str) -> str:
    return f"chargegrid_{estrategia}_{backend}"


def _impressao_digital(estrategia: str) -> str:
    h = hashlib.sha256()
    for pdf in listar_pdfs():
        h.update(pdf.name.encode())
        h.update(pdf.read_bytes())
    h.update(json.dumps(ESTRATEGIAS[estrategia].__dict__, sort_keys=True).encode())
    return h.hexdigest()[:16]


def _abrir(colecao: str, backend: str, impressao_digital: str | None = None) -> Chroma:
    metadata = {"hnsw:space": "cosine"}
    if impressao_digital:
        metadata["impressao_digital"] = impressao_digital
    return Chroma(
        collection_name=colecao,
        embedding_function=obter_embeddings(backend),
        persist_directory=str(CHROMA_DIR),
        collection_metadata=metadata,
    )


def indexar(estrategia: str | None = None, backend: str | None = None) -> Chroma:
    """(Re)constrói a coleção a partir dos PDFs de `data/knowledge_base/`."""
    settings = load_settings()
    estrategia = estrategia or settings.rag_estrategia_chunking
    backend = backend or settings.embeddings_backend
    colecao = nome_colecao(estrategia, backend)
    config = ESTRATEGIAS[estrategia]

    store = _abrir(colecao, backend)
    store.delete_collection()
    store = _abrir(colecao, backend, _impressao_digital(estrategia))

    chunks = dividir(carregar_pdfs(normalizar=config.normalizar, tabelas=config.tabelas), estrategia)
    store.add_documents(chunks, ids=[c.metadata["chunk_id"] for c in chunks])
    _CACHE[colecao] = store
    return store


def obter_vector_store(estrategia: str | None = None, backend: str | None = None) -> Chroma:
    """Coleção pronta para busca; indexa na primeira vez ou se a base mudou."""
    settings = load_settings()
    estrategia = estrategia or settings.rag_estrategia_chunking
    backend = backend or settings.embeddings_backend
    colecao = nome_colecao(estrategia, backend)
    if colecao in _CACHE:
        return _CACHE[colecao]

    store = _abrir(colecao, backend)
    atual = (store._collection.metadata or {}).get("impressao_digital")
    if store._collection.count() == 0 or atual != _impressao_digital(estrategia):
        return indexar(estrategia, backend)
    _CACHE[colecao] = store
    return store


def colecao_pronta(estrategia: str | None = None, backend: str | None = None) -> bool:
    """True se a coleção já está indexada e atualizada.

    Não carrega o modelo de embeddings: a interface usa isso só para avisar o usuário de
    que a primeira pergunta vai demorar (download do modelo e indexação).
    """
    import chromadb

    settings = load_settings()
    estrategia = estrategia or settings.rag_estrategia_chunking
    backend = backend or settings.embeddings_backend
    if not CHROMA_DIR.exists():
        return False
    try:
        colecao = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(nome_colecao(estrategia, backend))
    except Exception:  # noqa: BLE001 - coleção inexistente
        return False
    atual = (colecao.metadata or {}).get("impressao_digital")
    return colecao.count() > 0 and atual == _impressao_digital(estrategia)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indexa a base de conhecimento no ChromaDB.")
    parser.add_argument("--todas", action="store_true", help="indexa as coleções de todas as estratégias de chunking")
    args = parser.parse_args()
    s = load_settings()
    estrategias = list(ESTRATEGIAS) if args.todas else [s.rag_estrategia_chunking]
    for estrategia in estrategias:
        store = indexar(estrategia, s.embeddings_backend)
        print(f"{nome_colecao(estrategia, s.embeddings_backend)}: {store._collection.count()} chunks em {CHROMA_DIR}")
