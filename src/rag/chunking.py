"""Etapa 2 do pipeline RAG: divisão em chunks (`RecursiveCharacterTextSplitter`).

Duas estratégias, ambas sobre o `RecursiveCharacterTextSplitter` do LangChain —
a diferença é o que entra no splitter e o que vai junto no chunk. As duas foram
avaliadas com RAGAS (ver `evals/SCORES_POR_ITERACAO.md` e `docs/relatorio_rag.md`):

- `recursivo_basico` (iteração 1, baseline): cada PÁGINA do PDF vai inteira para
  o splitter (`chunk_size=1000`, `chunk_overlap=0`). É o uso "de tutorial": o
  corte cai onde o tamanho mandar, então um chunk pode juntar o fim de uma seção
  com o começo de outra (ex.: tabela de postos tarifários + regra de frota).

- `por_secao` (iteração 2) e `por_secao_tabelas` (iteração 3, = `por_secao` com as
  tabelas do PDF preservadas linha a linha pelo loader): primeiro o texto do documento inteiro é
  cortado nas seções numeradas ("N. Título" — padrão garantido pelos PDFs
  gerados em `scripts/gerar_pdfs_base.py`); só então cada seção passa pelo
  splitter (`chunk_size=800`, `chunk_overlap=120`), e só é subdividida se for
  maior que isso. Cada chunk recebe um cabeçalho "[Documento — Seção]" no próprio
  texto, para o embedding saber de onde o trecho veio mesmo quando ele é um
  pedaço do meio de uma seção (técnica de "contextual chunk header").
  Repete a lição da Sprint 03 (relatório, Problema 4): fundir seções vizinhas num
  chunk só dilui o embedding e derruba o ranking do trecho certo.

Nas duas estratégias o chunk carrega `documento`, `titulo`, `secao` e `pagina`
nos metadados — é isso que permite citar "documento, seção, página" em toda
resposta.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

_TITULO_SECAO = re.compile(r"^(\d{1,2})\.\s+(\S.{0,110})$", re.MULTILINE)
_SECAO_INICIAL = "Introdução"


@dataclass(frozen=True)
class ConfigChunking:
    estrategia: str
    chunk_size: int
    chunk_overlap: int
    normalizar: bool = True  # Unicode NFKC no loader (src/rag/loader.py)
    tabelas: bool = False  # tabelas reescritas como linhas Markdown no loader


ESTRATEGIAS = {
    "recursivo_basico": ConfigChunking("recursivo_basico", 1000, 0, normalizar=False),
    "por_secao": ConfigChunking("por_secao", 800, 120),
    # Mesmo corte por seção, com as tabelas dos PDFs preservadas linha a linha.
    "por_secao_tabelas": ConfigChunking("por_secao_tabelas", 800, 120, tabelas=True),
}


def _agrupar_por_documento(paginas: list[Document]) -> dict[str, list[Document]]:
    grupos: dict[str, list[Document]] = {}
    for pagina in paginas:
        grupos.setdefault(pagina.metadata["documento"], []).append(pagina)
    for lista in grupos.values():
        lista.sort(key=lambda p: p.metadata.get("page", 0))
    return grupos


def _texto_com_paginas(paginas: list[Document]) -> tuple[str, list[tuple[int, int]]]:
    """Texto do documento inteiro + (offset_inicial, nº da página) de cada página."""
    partes, offsets, cursor = [], [], 0
    for pagina in paginas:
        offsets.append((cursor, pagina.metadata.get("page", 0) + 1))
        partes.append(pagina.page_content)
        cursor += len(pagina.page_content) + 1
    return "\n".join(partes), offsets


def _pagina_do_offset(offset: int, offsets: list[tuple[int, int]]) -> int:
    pagina = offsets[0][1]
    for inicio, numero in offsets:
        if offset >= inicio:
            pagina = numero
    return pagina


def _secoes(texto: str) -> list[tuple[int, str]]:
    """(offset, "N. Título") de cada título de seção encontrado no texto."""
    return [(m.start(), f"{m.group(1)}. {m.group(2).strip()}") for m in _TITULO_SECAO.finditer(texto)]


def _secao_do_offset(offset: int, secoes: list[tuple[int, str]]) -> str:
    atual = _SECAO_INICIAL
    for inicio, titulo in secoes:
        if offset >= inicio:
            atual = titulo
    return atual


def _metadados(base: dict, secao: str, pagina: int, config: ConfigChunking, indice: int) -> dict:
    return {
        "documento": base["documento"],
        "titulo": base["titulo"],
        "secao": secao,
        "pagina": pagina,
        "source": base.get("source", ""),
        "estrategia": config.estrategia,
        "chunk_id": f"{base['documento']}#{indice}",
    }


def _chunk_recursivo_basico(paginas: list[Document], config: ConfigChunking) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap, add_start_index=True
    )
    chunks: list[Document] = []
    for documento, paginas_doc in _agrupar_por_documento(paginas).items():
        texto, offsets = _texto_com_paginas(paginas_doc)
        secoes = _secoes(texto)
        for pagina, (inicio_pagina, _) in zip(paginas_doc, offsets):
            for pedaco in splitter.split_documents([pagina]):
                offset_global = inicio_pagina + pedaco.metadata["start_index"]
                chunks.append(
                    Document(
                        page_content=pedaco.page_content,
                        metadata=_metadados(
                            pagina.metadata,
                            _secao_do_offset(offset_global, secoes),
                            _pagina_do_offset(offset_global, offsets),
                            config,
                            len(chunks),
                        ),
                    )
                )
    return chunks


def _chunk_por_secao(paginas: list[Document], config: ConfigChunking) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap, add_start_index=True
    )
    chunks: list[Document] = []
    for documento, paginas_doc in _agrupar_por_documento(paginas).items():
        base = paginas_doc[0].metadata
        texto, offsets = _texto_com_paginas(paginas_doc)
        secoes = _secoes(texto)
        limites = [0] + [inicio for inicio, _ in secoes] + [len(texto)]
        for inicio, fim in zip(limites, limites[1:]):
            trecho = texto[inicio:fim].strip()
            if not trecho:
                continue
            secao = _secao_do_offset(inicio, secoes)
            for pedaco in splitter.create_documents([trecho]):
                offset_global = inicio + pedaco.metadata["start_index"]
                cabecalho = f"[{base['titulo']} — {secao}]\n"
                chunks.append(
                    Document(
                        page_content=cabecalho + pedaco.page_content,
                        metadata=_metadados(
                            base, secao, _pagina_do_offset(offset_global, offsets), config, len(chunks)
                        ),
                    )
                )
    return chunks


def dividir(paginas: list[Document], estrategia: str = "por_secao_tabelas") -> list[Document]:
    config = ESTRATEGIAS[estrategia]
    if estrategia == "recursivo_basico":
        return _chunk_recursivo_basico(paginas, config)
    return _chunk_por_secao(paginas, config)
