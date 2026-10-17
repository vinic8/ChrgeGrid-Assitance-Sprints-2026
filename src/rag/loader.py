"""Etapa 1 do pipeline RAG: carregamento dos PDFs da base (`PyMuPDFLoader`).

Lê todos os `data/knowledge_base/*.pdf` com o `PyMuPDFLoader` do LangChain (um
`Document` por página, com `source`, `page` e `title` nos metadados) e acrescenta
o metadado `documento` (nome do arquivo sem extensão), usado na citação.

Duas melhorias opcionais, ligadas conforme a iteração (ver docs/relatorio_rag.md):

- `normalizar=True` (a partir da iteração 2): Unicode NFKC no texto extraído. O
  PyMuPDF devolve ligaduras tipográficas como um único caractere — "oﬁcial",
  "ﬁxa", "reﬂetindo" usam U+FB01/U+FB02 — e o embedding e o BM25 tratam "ﬁxa" e
  "fixa" como palavras diferentes. NFKC desfaz as ligaduras. Também junta palavras
  hifenizadas na quebra de linha ("sub-\\nperíodo" -> "sub-período").

- `tabelas=True` (a partir da iteração 3): a extração de texto padrão do PDF
  devolve cada CÉLULA de tabela numa linha própria, então a linha "0x0002 |
  Illegal Data Address | causa | ação" vira 4+ linhas soltas no meio das outras
  linhas da tabela. Na iteração 2, o modelo associou o código 0x0002 à causa e à
  ação da linha de baixo (0x0003) por causa disso. Com `tabelas=True`, as tabelas
  da página são detectadas com `page.find_tables()` do PyMuPDF e reescritas como
  linhas Markdown (`| 0x0002 | Illegal Data Address | ... |`) no lugar das células
  soltas, preservando a associação dentro de cada linha.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pymupdf
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document

from src.config import KNOWLEDGE_BASE_DIR

# Sem isso, find_tables() imprime uma recomendação do pacote opcional pymupdf_layout,
# que o projeto não usa e que parece erro para quem está rodando.
pymupdf.no_recommend_layout()

_HIFEN_QUEBRA = re.compile(r"(\w)-\n(\w)")


def normalizar_texto(texto: str) -> str:
    texto = unicodedata.normalize("NFKC", texto)
    return _HIFEN_QUEBRA.sub(r"\1-\2", texto)


def listar_pdfs(diretorio: Path = KNOWLEDGE_BASE_DIR) -> list[Path]:
    return sorted(diretorio.glob("*.pdf"))


def _contido(interno: pymupdf.Rect, externo: pymupdf.Rect) -> bool:
    return interno != externo and externo.contains(interno)


def _linhas_markdown(tabela) -> str:
    linhas = []
    for linha in tabela.extract():
        celulas = [" ".join((c or "").split()) for c in linha]
        linhas.append("| " + " | ".join(celulas) + " |")
    return "\n".join(linhas)


def _texto_com_tabelas(pagina: pymupdf.Page) -> str:
    """Texto da página com cada tabela reescrita como linhas Markdown, na posição original."""
    tabelas = list(pagina.find_tables().tables)
    caixas = [pymupdf.Rect(t.bbox) for t in tabelas]
    # find_tables também "acha" tabelas falsas dentro de células de cabeçalho com
    # quebra de linha (ex.: "Causa provável"); elas ficam contidas na tabela real.
    tabelas = [t for t, c in zip(tabelas, caixas) if not any(_contido(c, o) for o in caixas)]
    caixas = [pymupdf.Rect(t.bbox) for t in tabelas]

    pedacos: list[tuple[float, str]] = []
    for x0, y0, x1, y1, texto, *_ in pagina.get_text("blocks"):
        bloco = pymupdf.Rect(x0, y0, x1, y1)
        if not any(caixa.intersects(bloco) for caixa in caixas):
            pedacos.append((y0, texto.strip()))
    for tabela, caixa in zip(tabelas, caixas):
        pedacos.append((caixa.y0, _linhas_markdown(tabela)))
    return "\n".join(texto for _, texto in sorted(pedacos, key=lambda p: p[0]) if texto)


def carregar_pdfs(
    diretorio: Path = KNOWLEDGE_BASE_DIR, normalizar: bool = True, tabelas: bool = False
) -> list[Document]:
    """Uma lista de `Document` (uma página cada) de todos os PDFs da base."""
    paginas: list[Document] = []
    for caminho in listar_pdfs(diretorio):
        documentos = PyMuPDFLoader(str(caminho)).load()
        pdf = pymupdf.open(str(caminho)) if tabelas else None
        for pagina in documentos:
            if pdf is not None:
                pagina.page_content = _texto_com_tabelas(pdf[pagina.metadata["page"]])
            if normalizar:
                pagina.page_content = normalizar_texto(pagina.page_content)
            pagina.metadata["documento"] = caminho.stem
            pagina.metadata["titulo"] = pagina.metadata.get("title") or caminho.stem
            paginas.append(pagina)
        if pdf is not None:
            pdf.close()
    return paginas
