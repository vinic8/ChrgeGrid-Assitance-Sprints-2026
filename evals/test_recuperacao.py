"""Teste de recuperação com perguntas fora do eval set (paráfrases), sem LLM.

O eval set do RAGAS (`evals/rag_eval_set.py`) foi usado para calibrar o pipeline, então
acertar nele não prova que a recuperação generaliza. Este teste usa 10 perguntas
NOVAS, escritas como um operador escreveria (sem o vocabulário do documento:
"quanto custa", "quanto cobrar", "bateria encheu"), e verifica se o trecho da seção
certa aparece entre os k recuperados, para cada modo de busca. Também confere,
no eval set, se o documento certo continua sendo recuperado e se a porta de
relevância continua separando as perguntas respondíveis das sem resposta.

Foi este teste que mostrou a falha corrigida na iteração 5: na busca `hibrida`,
"Quanto custa carregar às 19h?" não recuperava a tabela de postos tarifários.

Com `--com-llm`, roda também o pipeline completo (Gemma) nas paráfrases, que devem ser
RESPONDIDAS citando o documento certo, e em perguntas fora do domínio, que devem ser
RECUSADAS. Foi esse modo que mostrou que a porta de relevância de 0,69 recusava
perguntas legítimas curtas (corrigido na iteração 6).

Uso:
    python -m evals.test_recuperacao
    python -m evals.test_recuperacao --com-llm
"""
from __future__ import annotations

import argparse
import uuid
from datetime import datetime
from pathlib import Path

from evals.rag_eval_set import CASOS
from src.config import load_settings
from src.rag.retriever import recuperar

RESULTS_DIR = Path(__file__).resolve().parent / "results"

# (pergunta nova, documento esperado, prefixo da seção esperada; "" = qualquer seção)
PARAFRASES = [
    ("O carregador C11 fez uma recarga das 18:30 às 19:00, com consumo de 5 kWh. Quanto fica o faturamento?",
     "tabelas_tarifarias", "1."),
    ("Quanto custa carregar às 19h?", "tabelas_tarifarias", "1."),
    ("Quanto o cliente paga por 10 kWh carregados às 2 da manhã?", "tabelas_tarifarias", "1."),
    ("Qual o valor de uma recarga de 8 kWh às 15h?", "tabelas_tarifarias", "1."),
    ("Quanto cobrar de um carro que carregou 12 kWh entre 21h e 22h?", "tabelas_tarifarias", "1."),
    ("Qual o preço do kWh no horário de pico?", "tabelas_tarifarias", "1."),
    ("Carro da frota pagou quanto por 15 kWh?", "tabelas_tarifarias", "3."),
    ("Quanto tempo o morador pode ficar na vaga depois que a bateria encheu?", "regimento_recarga_condominial", "4."),
    ("O que fazer quando aparece falha de aterramento?", "mapa_modbus_hca_g2", ""),
    ("Qual registrador mostra se o carro está conectado?", "mapa_modbus_hca_g2", "4."),
]
MODOS = ("vetorial", "hibrida", "hibrida_expandida")

# Perguntas fora do domínio, também fora do eval set: devem ser recusadas.
FORA_DO_DOMINIO = [
    "Qual a capital da França?",
    "Quem ganhou a copa de 2022?",
    "Qual o melhor plano de celular?",
    "Como faço um bolo?",
    "Qual o preço da gasolina hoje?",
    "Qual a cotação do dólar?",
]


def ponta_a_ponta() -> list[str]:
    """Pipeline completo com a configuração do .env (chama o LLM)."""
    from src.chain.builder import conversar
    from src.chain.memoria import limpar_sessao

    def perguntar(pergunta):
        sessao = f"rec-{uuid.uuid4()}"
        try:
            return conversar(sessao, pergunta)
        finally:
            limpar_sessao(sessao)

    respondidas, falhas_resp = 0, []
    for pergunta, documento, _ in PARAFRASES:
        r = perguntar(pergunta)
        ok = not r.resultado.fora_da_base and any(c.documento == documento for c in r.citacoes)
        respondidas += ok
        if not ok:
            falhas_resp.append(f'"{pergunta}" → {r.resultado.justificativa[:120]}')
    recusadas, falhas_rec = 0, []
    for pergunta in FORA_DO_DOMINIO:
        r = perguntar(pergunta)
        ok = r.bloqueado_por_guardrail or r.resultado.fora_da_base or not r.citacoes
        recusadas += ok
        if not ok:
            falhas_rec.append(f'"{pergunta}" → {r.resultado.justificativa[:120]}')
    s = load_settings()
    linhas = [
        "", f"## Pipeline completo (`{s.model_primary}`, busca `{s.rag_busca}`, k={s.rag_k}, "
        f"porta {s.rag_limiar_relevancia}, prompt RAG {s.rag_prompt_version})", "",
        "| Teste | Resultado |", "|---|---|",
        f"| Paráfrases respondidas citando o documento certo | {respondidas}/{len(PARAFRASES)} |",
        f"| Perguntas fora do domínio recusadas | {recusadas}/{len(FORA_DO_DOMINIO)} |",
    ]
    for f in falhas_resp + falhas_rec:
        linhas.append(f"- falha: {f}")
    return linhas


def avaliar(modo: str, k: int) -> dict:
    estrategia = load_settings().rag_estrategia_chunking
    falhas = []
    for pergunta, documento, secao in PARAFRASES:
        chunks = recuperar(pergunta, k=k, estrategia=estrategia, limiar=0, busca=modo)
        if not any(c.documento == documento and c.secao.startswith(secao) for c in chunks):
            falhas.append(pergunta)
    respondiveis = [c for c in CASOS if c.tipo == "respondivel"]
    acertos_eval = sum(
        bool({c.documento for c in recuperar(caso.pergunta, k=k, estrategia=estrategia, limiar=0, busca=modo)}
             & set(caso.documentos))
        for caso in respondiveis
    )
    melhor = {
        caso.id: max(c.score for c in recuperar(caso.pergunta, k=k, estrategia=estrategia, limiar=0, busca=modo))
        for caso in CASOS
    }
    return {
        "modo": modo,
        "parafrases": f"{len(PARAFRASES) - len(falhas)}/{len(PARAFRASES)}",
        "eval_set": f"{acertos_eval}/{len(respondiveis)}",
        "menor_respondivel": min(melhor[c.id] for c in respondiveis),
        "maior_recusa": max(melhor[c.id] for c in CASOS if c.tipo == "recusa"),
        "falhas": falhas,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--com-llm", action="store_true", help="roda também o pipeline completo (chama o LLM)")
    args = parser.parse_args()
    settings = load_settings()
    resultados = [avaliar(modo, settings.rag_k) for modo in MODOS]
    linhas = [
        "# Teste de recuperação com paráfrases (sem LLM)", "",
        f"Gerado em {datetime.now().isoformat(timespec='seconds')} por `python -m evals.test_recuperacao`. "
        f"Chunking `{settings.rag_estrategia_chunking}`, k={settings.rag_k}. Paráfrases: perguntas novas, fora do "
        "eval set, escritas sem o vocabulário dos documentos.", "",
        "| Busca | Paráfrases com a seção certa no top-k | Eval set: doc. certo no top-k | "
        "Melhor score da respondível mais fraca | Melhor score da recusa mais forte |",
        "|---|---|---|---|---|",
    ]
    for r in resultados:
        linhas.append(
            f"| `{r['modo']}` | {r['parafrases']} | {r['eval_set']} | {r['menor_respondivel']:.3f} | {r['maior_recusa']:.3f} |"
        )
    linhas += ["", "## Paráfrases que falharam", ""]
    for r in resultados:
        linhas.append(f"- `{r['modo']}`: " + ("; ".join(f'"{f}"' for f in r["falhas"]) or "nenhuma"))
    if args.com_llm:
        linhas += ponta_a_ponta()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    destino = RESULTS_DIR / "teste_recuperacao.md"
    destino.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("\n".join(linhas))


if __name__ == "__main__":
    main()
