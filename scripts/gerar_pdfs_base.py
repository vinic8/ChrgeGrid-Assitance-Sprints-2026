"""Gera os PDFs da base de conhecimento a partir das fontes em Markdown.

A Sprint 04 exige o pipeline `PyMuPDFLoader -> RecursiveCharacterTextSplitter`,
ou seja, a base precisa estar em PDF. As fontes editáveis ficam em
`data/knowledge_base/fontes/*.md` (versionadas, fáceis de revisar em diff) e
este script renderiza cada uma em `data/knowledge_base/<nome>.pdf` com PyMuPDF
(`pymupdf.Story`), sem dependência extra.

Cada seção "## N. Título" do Markdown vira um título "N. Título" no PDF — é esse
padrão que `src/rag/chunking.py` usa para identificar a seção de cada chunk e
permitir citação "documento, seção" na resposta.

Uso:
    python -m scripts.gerar_pdfs_base
"""
from __future__ import annotations

import html
import re
from pathlib import Path

import pymupdf

from src.config import KNOWLEDGE_BASE_DIR

FONTES_DIR = KNOWLEDGE_BASE_DIR / "fontes"

_CSS = """
body { font-family: sans-serif; font-size: 10pt; line-height: 1.35; }
h1 { font-size: 17pt; color: #c8102e; margin-bottom: 6pt; }
h2 { font-size: 12.5pt; color: #1f2937; margin-top: 12pt; margin-bottom: 4pt; }
p { margin-top: 3pt; margin-bottom: 3pt; text-align: justify; }
li { margin-bottom: 2pt; }
table { border-collapse: collapse; margin-top: 4pt; margin-bottom: 6pt; }
th { background-color: #eeeeee; font-weight: bold; }
th, td { border: 0.5pt solid #999999; padding: 2pt 4pt; font-size: 9pt; vertical-align: top; }
code { font-family: monospace; }
"""


def _inline(texto: str) -> str:
    texto = html.escape(texto, quote=False)
    texto = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)
    texto = re.sub(r"`(.+?)`", r"<code>\1</code>", texto)
    return texto


def markdown_para_html(markdown: str) -> str:
    """Conversor mínimo para o subconjunto de Markdown usado nas fontes."""
    linhas = markdown.splitlines()
    partes: list[str] = []
    paragrafo: list[str] = []
    i = 0

    def fechar_paragrafo():
        if paragrafo:
            partes.append(f"<p>{_inline(' '.join(paragrafo))}</p>")
            paragrafo.clear()

    while i < len(linhas):
        linha = linhas[i].rstrip()
        if not linha.strip():
            fechar_paragrafo()
            i += 1
        elif linha.startswith("# "):
            fechar_paragrafo()
            partes.append(f"<h1>{_inline(linha[2:])}</h1>")
            i += 1
        elif linha.startswith("## "):
            fechar_paragrafo()
            partes.append(f"<h2>{_inline(linha[3:])}</h2>")
            i += 1
        elif linha.startswith("|"):
            fechar_paragrafo()
            tabela = []
            while i < len(linhas) and linhas[i].startswith("|"):
                tabela.append(linhas[i])
                i += 1
            celulas = [[c.strip() for c in t.strip().strip("|").split("|")] for t in tabela]
            cabecalho, corpo = celulas[0], [c for c in celulas[1:] if not set("".join(c)) <= set("-: ")]
            html_tabela = "<table><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in cabecalho) + "</tr>"
            for linha_tabela in corpo:
                html_tabela += "<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in linha_tabela) + "</tr>"
            partes.append(html_tabela + "</table>")
        elif linha.startswith("- "):
            fechar_paragrafo()
            itens = []
            while i < len(linhas) and (linhas[i].startswith("- ") or linhas[i].startswith("  ")):
                if linhas[i].startswith("- "):
                    itens.append(linhas[i][2:].strip())
                else:
                    itens[-1] += " " + linhas[i].strip()
                i += 1
            partes.append("<ul>" + "".join(f"<li>{_inline(item)}</li>" for item in itens) + "</ul>")
        else:
            paragrafo.append(linha.strip())
            i += 1
    fechar_paragrafo()
    return "\n".join(partes)


def gerar_pdf(fonte_md: Path, destino_pdf: Path) -> int:
    markdown = fonte_md.read_text(encoding="utf-8")
    titulo = markdown.splitlines()[0].lstrip("# ").strip()
    story = pymupdf.Story(html=markdown_para_html(markdown), user_css=_CSS)
    writer = pymupdf.DocumentWriter(str(destino_pdf))
    pagina = pymupdf.paper_rect("a4")
    area = pagina + (54, 54, -54, -54)
    paginas = 0
    mais = True
    while mais:
        dispositivo = writer.begin_page(pagina)
        mais, _ = story.place(area)
        story.draw(dispositivo)
        writer.end_page()
        paginas += 1
    writer.close()

    # Metadados do PDF: o PyMuPDFLoader expõe "title" em cada Document.
    doc = pymupdf.open(str(destino_pdf))
    doc.set_metadata({"title": titulo, "author": "ChargeGrid / GoodWe — FIAP Sprint 04"})
    doc.saveIncr()
    doc.close()
    return paginas


def main() -> None:
    for fonte in sorted(FONTES_DIR.glob("*.md")):
        destino = KNOWLEDGE_BASE_DIR / f"{fonte.stem}.pdf"
        paginas = gerar_pdf(fonte, destino)
        print(f"{destino.relative_to(KNOWLEDGE_BASE_DIR.parent.parent)}  ({paginas} pág.)")


if __name__ == "__main__":
    main()
