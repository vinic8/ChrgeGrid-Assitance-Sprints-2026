"""RAG — indexação e recuperação da base de conhecimento técnico (knowledge/).

Cobre o que o chatbot não pode confiar só na memória parametrica do LLM:
referência de protocolo OCPP, códigos de exceção Modbus/RS485, a política de
tarifação dinâmica e as especificações reais do EV Charger GoodWe (linha HCA G2)
(ver `knowledge/*.md`). Sem RAG, o modelo "inventa" códigos de erro ou aplica
uma tarifa fixa genérica; com RAG, a resposta é ancorada em documento real.

Vetor store: FAISS (`langchain-community` + `faiss-cpu`), local e persistido
em `data/faiss_index/` — não depende de serviço externo. Embeddings: FastEmbed
(`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, ONNX, roda em
CPU) em vez de embeddings via Ollama Cloud, porque a API key atual não tem
acesso ao endpoint de embeddings da Ollama Cloud (HTTP 401 - testado). Ficar
preso a um provider de chat para gerar embeddings acoplaria RAG a Provider
A/B; um embedder local e gratuito evita essa dependência.
"""
from __future__ import annotations

from pathlib import Path

from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = ROOT_DIR / "knowledge"
INDEX_DIR = ROOT_DIR / "data" / "faiss_index"

_EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_TAMANHO_MAX_SECAO = 1500  # so entra na sub-divisao por caracteres se a secao passar disso

_vectorstore: FAISS | None = None


def _embeddings() -> FastEmbedEmbeddings:
    return FastEmbedEmbeddings(model_name=_EMBED_MODEL)


def _dividir_por_secao(caminho) -> list[Document]:
    """Um chunk por seção "## " (nunca funde seções vizinhas).

    Testamos primeiro com RecursiveCharacterTextSplitter usando um chunk_size
    grande o bastante para manter cada tabela inteira - o problema não era a
    tabela ser cortada, era o splitter FUNDIR 2-3 seções pequenas adjacentes
    num chunk só sempre que cabiam juntas no chunk_size. O embedding resultante
    ficava "diluído" (intro genérica + tabela especifica + outro assunto no
    mesmo vetor) e o chunk com a linha exata que a pergunta precisava (ex.:
    "18:00-20:59") passou a rankear pior que chunks totalmente irrelevantes.
    Cada "## " vira um chunk isolado e semanticamente coeso; só se uma seção
    sozinha passar de _TAMANHO_MAX_SECAO ela é sub-dividida por caracteres.
    """
    texto = caminho.read_text(encoding="utf-8")
    titulo = texto.split("\n", 1)[0].lstrip("# ").strip()
    partes = texto.split("\n## ")
    secoes = [partes[0]] + [f"## {p}" for p in partes[1:]]

    fallback = RecursiveCharacterTextSplitter(chunk_size=_TAMANHO_MAX_SECAO, chunk_overlap=150)
    documentos = []
    for secao in secoes:
        secao = secao.strip()
        if not secao:
            continue
        conteudo = secao if secao.startswith(titulo) else f"{titulo}\n\n{secao}"
        if len(conteudo) <= _TAMANHO_MAX_SECAO:
            documentos.append(Document(page_content=conteudo, metadata={"fonte": caminho.stem}))
        else:
            for pedaco in fallback.split_text(conteudo):
                documentos.append(Document(page_content=pedaco, metadata={"fonte": caminho.stem}))
    return documentos


def _carregar_documentos() -> list[Document]:
    documentos = []
    for caminho in sorted(KNOWLEDGE_DIR.glob("*.md")):
        documentos.extend(_dividir_por_secao(caminho))
    return documentos


def _construir_indice() -> FAISS:
    chunks = _carregar_documentos()
    indice = FAISS.from_documents(chunks, _embeddings())
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    indice.save_local(str(INDEX_DIR))
    return indice


def obter_vectorstore() -> FAISS:
    """Carrega o índice do disco se existir; senão, constrói a partir de knowledge/."""
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    if (INDEX_DIR / "index.faiss").exists():
        _vectorstore = FAISS.load_local(
            str(INDEX_DIR), _embeddings(), allow_dangerous_deserialization=True
        )
    else:
        _vectorstore = _construir_indice()
    return _vectorstore


def obter_retriever(k: int = 3):
    """Retriever LCEL-compatível: `retriever.invoke(pergunta) -> list[Document]`."""
    return obter_vectorstore().as_retriever(search_kwargs={"k": k})


def reindexar() -> FAISS:
    """Força a reconstrução do índice (usar depois de editar knowledge/*.md)."""
    global _vectorstore
    _vectorstore = _construir_indice()
    return _vectorstore


def formatar_contexto(documentos: list[Document]) -> str:
    """Formata os chunks recuperados para injeção no prompt, com a fonte citável."""
    if not documentos:
        return "Nenhum documento tecnico relevante encontrado na base de conhecimento."
    blocos = [f"[Fonte: {doc.metadata.get('fonte', 'desconhecida')}]\n{doc.page_content}" for doc in documentos]
    return "\n\n---\n\n".join(blocos)


if __name__ == "__main__":
    reindexar()
    print(f"Indice reconstruido em {INDEX_DIR}")
