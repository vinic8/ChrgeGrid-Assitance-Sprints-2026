"""Chamada multi-provider (bônus da Sprint 04): mais de um modelo × mais de um prompt.

Para uma mesma pergunta, consulta em paralelo todas as combinações de
{Gemma 4 via Ollama Cloud, Qwen 3.8 via Groq} × {versões do prompt RAG}. A
recuperação é feita UMA vez e o mesmo conjunto de trechos é entregue a todas as
combinações — assim, a diferença entre as respostas vem só do modelo e do prompt,
não da busca. Cada combinação roda numa sessão descartável (sem memória), para
uma não contaminar a outra.

Usado pela aba "Multi-provider" da interface (`app/streamlit_app.py`) e pela linha
de comando:

    python -m src.chain.multi_provider "Quanto custa recarregar às 19h?"
"""
from __future__ import annotations

import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from src.chain.builder import PROVIDERS, RespostaChat, classificar_erro, conversar, modelo_padrao
from src.chain.memoria import limpar_sessao
from src.guardrails import checar_escopo, checar_jailbreak
from src.rag.retriever import ChunkRecuperado, recuperar

VERSOES_PADRAO = ("v2", "v4")


@dataclass
class ResultadoMulti:
    provider: str
    modelo: str
    prompt_rag_version: str
    resposta: RespostaChat | None = None
    erro: str | None = None
    tipo_erro: str | None = None  # ver classificar_erro()

    @property
    def rotulo(self) -> str:
        return f"{PROVIDERS[self.provider]} · prompt RAG {self.prompt_rag_version}"


def _rodar(pergunta: str, provider: str, versao: str, chunks: list[ChunkRecuperado]) -> ResultadoMulti:
    sessao = f"multi-{uuid.uuid4()}"
    resultado = ResultadoMulti(provider, modelo_padrao(provider), versao)
    try:
        resultado.resposta = conversar(sessao, pergunta, provider=provider, prompt_rag_version=versao, chunks=chunks)
    except Exception as exc:  # noqa: BLE001 - uma combinação com erro não derruba as outras
        resultado.erro = str(exc)
        resultado.tipo_erro = classificar_erro(exc)
    finally:
        limpar_sessao(sessao)
    return resultado


def consultar_multi(
    pergunta: str,
    providers: tuple[str, ...] = tuple(PROVIDERS),
    versoes_prompt: tuple[str, ...] = VERSOES_PADRAO,
    k: int | None = None,
    busca: str | None = None,
) -> tuple[list[ChunkRecuperado], list[ResultadoMulti]]:
    bloqueada = not checar_jailbreak(pergunta).seguro or not checar_escopo(pergunta).dentro_do_escopo
    chunks = [] if bloqueada else recuperar(pergunta, k=k, busca=busca)
    combinacoes = [(p, v) for p in providers for v in versoes_prompt]
    with ThreadPoolExecutor(max_workers=len(combinacoes)) as executor:
        futuros = [executor.submit(_rodar, pergunta, p, v, chunks) for p, v in combinacoes]
        return chunks, [f.result() for f in futuros]


if __name__ == "__main__":
    pergunta = " ".join(sys.argv[1:]) or "Qual a tarifa para veículos de frota?"
    chunks, resultados = consultar_multi(pergunta)
    print(f"Pergunta: {pergunta}\nTrechos recuperados: {[c.citacao for c in chunks]}\n")
    for r in resultados:
        print(f"=== {r.rotulo} ({r.modelo})")
        if r.erro:
            print(f"ERRO: {r.erro}\n")
            continue
        print(r.resposta.resultado.justificativa)
        print(f"Fontes: {[c.citacao for c in r.resposta.citacoes]} · {r.resposta.latencia_s:.1f}s\n")
