"""Etapa 5 do pipeline RAG: recuperação (top-k + porta de relevância + sanitização).

`recuperar()` devolve os `k` trechos mais relevantes como `ChunkRecuperado`, numerados
a partir de 1. O número é o id que o LLM usa em `fontes_citadas`; a UI resolve o id de
volta para documento, seção e página pelos METADADOS do chunk, então o modelo não
consegue citar uma fonte que não foi recuperada.

Modos de busca (`RAG_BUSCA`), um por fase da avaliação (números em
`docs/relatorio_rag.md` §5):

- `vetorial` (it1, it2): cosseno com o nomic-embed-text.
- `hibrida` (it3, it4): ranking vetorial + BM25 fundidos por Reciprocal Rank Fusion.
  Em português, o nomic dá peso demais a palavras frequentes ("recarga"); o BM25 pesa
  termos raros e exatos ("tarifa", "0x0002", "FROTA-").
- `hibrida_expandida` (it5, padrão): a híbrida com expansão de consulta só no lado
  BM25 (`EXPANSOES`: "quanto custa / faturamento" → "tarifa posto tarifário") e com
  o melhor chunk do BM25 garantido no top-k. A expansão não entra no lado vetorial
  porque é o score vetorial que a porta de relevância usa.

Porta de relevância (`RAG_LIMIAR_RELEVANCIA`): se nem o melhor trecho alcança o limiar
de cosseno, nada vai para o prompt. Usada com 0,69 nas iterações 3 a 5 e **desligada
(0) a partir da iteração 6**: calibrada só com as perguntas longas do eval set, ela
recusava 4 de 10 perguntas legítimas curtas (scores 0,630–0,686, sobrepostos aos das
perguntas fora do domínio, 0,599–0,667). A recusa fora do contexto fica com o guardrail
de escopo e com a regra FORA DO CONTEXTO do prompt RAG.
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache

from src.config import load_settings
from src.rag.sanitizacao import sanitizar
from src.rag.vector_store import obter_vector_store

_RRF_K = 60
_STOPWORDS = set(
    "a o as os de da do das dos e em no na nos nas um uma uns umas por para com sem que se ao aos "
    "qual quais quanto quantos como onde quando ou mais menos ja eu meu minha seu sua isso esse essa "
    "este esta ele ela eles elas foi ser ter tem sao pelo pela pelos pelas me nao sim muito depois "
    "antes entre sobre ate apos fica faco posso pode existe".split()
)


# Vocabulário do operador -> vocabulário dos documentos (só para o BM25).
EXPANSOES = [
    (re.compile(r"\b(fatur\w*|cobr\w*|custa\w*|custo\w*|pag[aoue]\w*|pre[cç]o\w*|valor\w*)\b", re.I),
     "tarifa posto tarifário R$/kWh"),
    (re.compile(r"\b\d{1,2}\s*(:\s*\d{2}|h\b)|\b(manh[aã]|tarde|noite|madrugada|pico)\b", re.I),
     "posto horário ponta fora de ponta"),
]


def expandir_consulta(pergunta: str) -> str:
    extras = [termos for padrao, termos in EXPANSOES if padrao.search(pergunta)]
    return " ".join([pergunta, *extras])


@dataclass
class ChunkRecuperado:
    n: int
    documento: str
    titulo: str
    secao: str
    pagina: int
    texto: str
    score: float
    suspeito: bool = False
    texto_original: str = field(default="", repr=False)

    @property
    def citacao(self) -> str:
        return f"{self.titulo} — {self.secao} (p. {self.pagina})"


def _tokens(texto: str) -> list[str]:
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    return [t for t in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", texto) if t not in _STOPWORDS and len(t) > 1]


class _BM25:
    def __init__(self, documentos: list[str], k1: float = 1.5, b: float = 0.75):
        self.docs = [_tokens(d) for d in documentos]
        self.k1, self.b = k1, b
        self.media = sum(len(d) for d in self.docs) / max(len(self.docs), 1)
        df = Counter(t for d in self.docs for t in set(d))
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        self.tf = [Counter(d) for d in self.docs]

    def scores(self, consulta: str) -> list[float]:
        termos = _tokens(consulta)
        saida = []
        for tf, doc in zip(self.tf, self.docs):
            s = 0.0
            for t in termos:
                if t in tf:
                    f = tf[t]
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * len(doc) / self.media))
            saida.append(s)
        return saida


@lru_cache(maxsize=8)
def _indice_lexical(estrategia: str, total_chunks: int):
    """BM25 sobre todos os chunks da coleção (recriado se a coleção mudar de tamanho)."""
    dados = obter_vector_store(estrategia)._collection.get(include=["documents"])
    return dados["ids"], _BM25(dados["documents"])


def _busca_hibrida(
    store, estrategia: str, pergunta: str, k: int, consulta_lexical: str | None = None, garantia_lexical: int = 0
):
    """RRF entre o ranking vetorial e o BM25.

    `garantia_lexical` reserva as primeiras vagas do top-k para os melhores chunks do
    BM25 (no RRF puro, um chunk 1º num ranking e 41º no outro perde para chunks medianos
    nos dois). Nesse modo o lado vetorial pontua todos os chunks; no modo `hibrida`
    continua com os 40 mais próximos, como foi medido nas iterações 3 e 4.
    """
    total = store._collection.count()
    candidatos = total if garantia_lexical else min(total, 40)
    vetoriais = store.similarity_search_with_relevance_scores(pergunta, k=candidatos)
    ids, bm25 = _indice_lexical(estrategia, total)
    lexicais = [
        (cid, s) for cid, s in sorted(zip(ids, bm25.scores(consulta_lexical or pergunta)), key=lambda x: x[1], reverse=True)
        if s > 0
    ]

    fusao: dict[str, float] = {}
    por_id = {}
    for rank, (doc, score) in enumerate(vetoriais):
        cid = doc.metadata.get("chunk_id")
        por_id[cid] = (doc, score)
        fusao[cid] = fusao.get(cid, 0.0) + 1 / (_RRF_K + rank + 1)
    for rank, (cid, _) in enumerate(lexicais):
        fusao[cid] = fusao.get(cid, 0.0) + 1 / (_RRF_K + rank + 1)

    garantidos = [cid for cid, _ in lexicais[:garantia_lexical]]
    restantes = [cid for cid in sorted(fusao, key=fusao.get, reverse=True) if cid not in garantidos]
    return [por_id[cid] for cid in [*garantidos, *restantes] if cid in por_id][:k]


def recuperar(
    pergunta: str,
    k: int | None = None,
    estrategia: str | None = None,
    limiar: float | None = None,
    busca: str | None = None,
) -> list[ChunkRecuperado]:
    settings = load_settings()
    k = k or settings.rag_k
    estrategia = estrategia or settings.rag_estrategia_chunking
    limiar = settings.rag_limiar_relevancia if limiar is None else limiar
    busca = busca or settings.rag_busca
    store = obter_vector_store(estrategia)

    if busca == "hibrida_expandida":
        resultados = _busca_hibrida(store, estrategia, pergunta, k, expandir_consulta(pergunta), garantia_lexical=1)
    elif busca == "hibrida":
        resultados = _busca_hibrida(store, estrategia, pergunta, k)
    else:
        resultados = store.similarity_search_with_relevance_scores(pergunta, k=k)

    if not resultados or max(score for _, score in resultados) < limiar:
        return []

    chunks: list[ChunkRecuperado] = []
    for doc, score in resultados:
        limpo = sanitizar(doc.page_content)
        chunks.append(
            ChunkRecuperado(
                n=len(chunks) + 1,
                documento=doc.metadata.get("documento", "?"),
                titulo=doc.metadata.get("titulo", doc.metadata.get("documento", "?")),
                secao=doc.metadata.get("secao", "?"),
                pagina=int(doc.metadata.get("pagina", 0)),
                texto=limpo.texto,
                score=round(float(score), 4),
                suspeito=limpo.suspeito,
                texto_original=doc.page_content,
            )
        )
    return chunks
