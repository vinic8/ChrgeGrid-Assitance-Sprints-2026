"""Avaliação do RAG por iteração: RAGAS (faithfulness, answer_relevancy) + rubrica de fallback.

Cada iteração é uma configuração completa do pipeline (chunking, k, tipo de
busca, versão do prompt RAG) rodada contra o MESMO eval set
(`evals/rag_eval_set.py`). O resultado de cada execução vai para
`evals/results/ragas_<iteracao>_<provider>.{json,md}` e a tabela consolidada de
todas as execuções é regenerada em `evals/SCORES_POR_ITERACAO.md`.

Uso:
    python -m evals.run_ragas --iteracao it1
    python -m evals.run_ragas --iteracao it3 --provider groq      # comparativo de modelos
    python -m evals.run_ragas --iteracao legado                    # Sprints 1/2 (sem RAG)
    python -m evals.run_ragas --respostas evals/results/respostas_sprint03.json --rotulo sprint03
    python -m evals.run_ragas --respostas evals/results/ragas_it1_ollama.json --metodo rubrica   # repontua só a rubrica
    python -m evals.run_ragas --tabela                             # só regenera SCORES_POR_ITERACAO.md

Juiz (RAGAS e rubrica): Gemma (`gemma4:cloud`, Ollama Cloud), temperature 0, fixo
em todas as execuções — ver limitações em `docs/relatorio_rag.md`.
"""
from __future__ import annotations

import evals.ragas_compat  # noqa: F401  (precisa vir antes de qualquer import do ragas)

import argparse
import json
import math
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from evals.rag_eval_set import CASOS, RESPONDIVEIS, CasoRag
from evals.rubrica_manual import avaliar as avaliar_rubrica
from src.chain.builder import PROVIDERS, conversar, modelo_padrao, montar_llm
from src.chain.memoria import limpar_sessao
from src.config import load_settings
from src.rag.retriever import recuperar

RESULTS_DIR = Path(__file__).resolve().parent / "results"
SCORES_MD = Path(__file__).resolve().parent / "SCORES_POR_ITERACAO.md"

_FRASES_RECUSA = (
    "não consta", "nao consta", "não encontr", "nao encontr", "não está disponível",
    "não há informação", "não possuo", "não tenho informação", "fora do domínio",
    "fora do escopo", "não está na base", "não disponho",
)


@dataclass(frozen=True)
class Iteracao:
    rotulo: str
    descricao: str
    tipo: str = "rag"  # "rag" | "legado"
    estrategia: str = "por_secao"
    k: int = 5
    prompt: str = "v2"
    busca: str = "vetorial"
    limiar: float = 0.0


ITERACOES: dict[str, Iteracao] = {
    "legado": Iteracao(
        "legado", "Sprints 1/2: sem RAG, prompt v1 em texto corrido, saída em texto livre", tipo="legado"
    ),
    "it1": Iteracao(
        "it1", "Baseline Sprint 04: chunk por página (1000/0), sem normalização, k=3, prompt RAG v1",
        estrategia="recursivo_basico", k=3, prompt="v1",
    ),
    "it2": Iteracao(
        "it2", "Chunk por seção (800/120) + NFKC + cabeçalho, k=5, prompt RAG v2 (grounding + citação)",
        estrategia="por_secao", k=5, prompt="v2",
    ),
    "it3": Iteracao(
        "it3", "Tabelas linha a linha + busca híbrida (vetorial + BM25) + limiar 0,69, k=5, prompt RAG v3",
        estrategia="por_secao_tabelas", k=5, prompt="v3", busca="hibrida", limiar=0.69,
    ),
    "it4": Iteracao(
        "it4", "Recuperação da it3 + prompt RAG v4 (resposta direta que retoma o sujeito da pergunta)",
        estrategia="por_secao_tabelas", k=5, prompt="v4", busca="hibrida", limiar=0.69,
    ),
    "it5": Iteracao(
        "it5", "it4 + expansão de consulta no BM25 com 1 vaga garantida ao BM25 (busca hibrida_expandida), k=6",
        estrategia="por_secao_tabelas", k=6, prompt="v4", busca="hibrida_expandida", limiar=0.69,
    ),
    "it6": Iteracao(
        "it6", "it5 sem a porta de relevância + base sem os 2 trechos escritos sob medida para o eval set",
        estrategia="por_secao_tabelas", k=6, prompt="v4", busca="hibrida_expandida", limiar=0.0,
    ),
    # Ablação (não é uma iteração): recuperação da it3 com o prompt RAG v2, para isolar
    # quanto do ganho it2 -> it3 vem do prompt v3 e quanto vem da recuperação.
    "it3_prompt_v2": Iteracao(
        "it3_prompt_v2", "Ablação: recuperação da it3 (tabelas + híbrida + limiar) com o prompt RAG v2",
        estrategia="por_secao_tabelas", k=5, prompt="v2", busca="hibrida", limiar=0.69,
    ),
}
ORDEM = ["legado", "sprint03", *[k for k in ITERACOES if k.startswith("it")]]


def _recusou(item: dict) -> bool:
    texto = item["resposta"].lower()
    return item["bloqueado"] or item["fora_da_base"] or any(f in texto for f in _FRASES_RECUSA)


def _gerar_item(caso: CasoRag, it: Iteracao, provider: str) -> dict:
    sessao = f"ragas-{it.rotulo}-{provider}-{caso.id}"
    inicio = time.perf_counter()
    if it.tipo == "legado":
        from src.manual_chat import conversar_legado, limpar_sessao_legada

        r = conversar_legado(sessao, caso.pergunta)
        limpar_sessao_legada(sessao)
        # O legado não recupera nada; para o RAGAS medir se o que ele afirma bate com a
        # base oficial, o contexto de referência são os 5 trechos que a busca híbrida
        # recupera da base completa para a mesma pergunta (configuração fixa, para a
        # medição ser reproduzível mesmo que o padrão do .env mude).
        referencia = recuperar(caso.pergunta, k=5, estrategia="por_secao", limiar=0, busca="hibrida")
        return {
            "id": caso.id, "tipo": caso.tipo, "pergunta": caso.pergunta, "resposta": r.texto,
            "contextos": [c.texto for c in referencia], "docs_recuperados": [],
            "docs_citados": [], "fora_da_base": False, "bloqueado": False,
            "latencia_s": round(r.latencia_s, 2), "tokens": r.tokens_entrada + r.tokens_saida,
        }

    r = conversar(
        sessao, caso.pergunta, provider=provider, prompt_rag_version=it.prompt, k=it.k,
        estrategia=it.estrategia, busca=it.busca, limiar=it.limiar,
    )
    limpar_sessao(sessao)
    return {
        "id": caso.id, "tipo": caso.tipo, "pergunta": caso.pergunta, "resposta": r.resultado.justificativa,
        "contextos": r.contextos, "docs_recuperados": [c.documento for c in r.chunks],
        "secoes_recuperadas": [f"{c.documento} | {c.secao} | {c.score}" for c in r.chunks],
        "docs_citados": [c.documento for c in r.citacoes],
        "citacoes": [c.citacao for c in r.citacoes],
        "fora_da_base": r.resultado.fora_da_base, "bloqueado": r.bloqueado_por_guardrail,
        "latencia_s": round(time.perf_counter() - inicio, 2), "tokens": r.tokens_entrada + r.tokens_saida,
    }


def gerar_respostas(it: Iteracao, provider: str) -> list[dict]:
    itens = []
    for caso in CASOS:
        print(f"  [{it.rotulo}/{provider}] {caso.id}...", flush=True)
        try:
            itens.append(_gerar_item(caso, it, provider))
        except Exception as exc:  # noqa: BLE001 - um caso com erro não derruba a rodada
            itens.append({
                "id": caso.id, "tipo": caso.tipo, "pergunta": caso.pergunta, "resposta": "",
                "contextos": [], "docs_recuperados": [], "docs_citados": [], "fora_da_base": False,
                "bloqueado": False, "latencia_s": 0.0, "tokens": 0, "erro": str(exc),
            })
    return itens


def _ragas(itens: list[dict], juiz, embeddings) -> list[dict]:
    from ragas import EvaluationDataset, evaluate
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import answer_relevancy, faithfulness
    from ragas.run_config import RunConfig

    dataset = EvaluationDataset.from_list([
        {"user_input": i["pergunta"], "response": i["resposta"] or "(sem resposta)",
         "retrieved_contexts": i["contextos"] or ["(nenhum trecho recuperado)"]}
        for i in itens
    ])
    resultado = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy],
        llm=LangchainLLMWrapper(juiz),
        embeddings=LangchainEmbeddingsWrapper(embeddings),
        # 1 worker: a Ollama Cloud recusa requisições simultâneas acima do limite do
        # plano (HTTP 429 "too many concurrent requests") e o RAGAS transforma cada
        # falha em NaN — achado da 1ª rodada desta sprint.
        run_config=RunConfig(max_workers=1, timeout=240, max_retries=6, max_wait=60),
        show_progress=False,
    )
    return resultado.to_pandas()[["faithfulness", "answer_relevancy"]].to_dict("records")


def _media(valores) -> float | None:
    validos = [v for v in valores if v is not None and not (isinstance(v, float) and math.isnan(v))]
    return round(statistics.mean(validos), 3) if validos else None


def pontuar(itens: list[dict], metodo: str = "ambos") -> dict:
    from src.rag.embeddings import obter_embeddings

    juiz = montar_llm(provider="ollama", temperature=0, max_tokens=2000)
    casos = {c.id: c for c in CASOS}
    respondiveis = [i for i in itens if i["tipo"] == "respondivel"]

    if metodo in ("ambos", "ragas", "auto"):
        try:
            print("  RAGAS (faithfulness, answer_relevancy)...", flush=True)
            for item, notas in zip(respondiveis, _ragas(respondiveis, juiz, obter_embeddings())):
                item["ragas"] = notas
        except Exception as exc:  # noqa: BLE001
            print(f"  RAGAS falhou ({exc}); usando a rubrica de fallback.", flush=True)
            metodo = "rubrica"
    if metodo in ("ambos", "rubrica"):
        print("  Rubrica de fallback...", flush=True)
        for item in respondiveis:
            try:
                item["rubrica"] = avaliar_rubrica(juiz, item["pergunta"], item["contextos"], item["resposta"])
            except Exception as exc:  # noqa: BLE001
                item["rubrica"] = {"faithfulness": None, "answer_relevancy": None, "motivo": f"erro: {exc}"}

    for item in itens:
        caso = casos[item["id"]]
        item["acerto_factual"] = caso.checar(item["resposta"]) if caso.tipo == "respondivel" else None
        item["recusou"] = _recusou(item)

    def _taxa(predicado, base):
        return round(100 * sum(1 for i in base if predicado(i)) / len(base), 1) if base else None

    recusas = [i for i in itens if i["tipo"] == "recusa"]
    return {
        "faithfulness_ragas": _media(i.get("ragas", {}).get("faithfulness") for i in respondiveis),
        "answer_relevancy_ragas": _media(i.get("ragas", {}).get("answer_relevancy") for i in respondiveis),
        "faithfulness_rubrica": _media(i.get("rubrica", {}).get("faithfulness") for i in respondiveis),
        "answer_relevancy_rubrica": _media(i.get("rubrica", {}).get("answer_relevancy") for i in respondiveis),
        "hit_documento_pct": _taxa(lambda i: set(i["docs_recuperados"]) & set(casos[i["id"]].documentos), respondiveis),
        "citacao_presente_pct": _taxa(lambda i: bool(i["docs_citados"]), respondiveis),
        "citacao_correta_pct": _taxa(lambda i: set(i["docs_citados"]) & set(casos[i["id"]].documentos), respondiveis),
        "acerto_factual_pct": _taxa(lambda i: i["acerto_factual"], respondiveis),
        "recusa_indevida_pct": _taxa(lambda i: i["recusou"], respondiveis),
        "recusa_correta_pct": _taxa(lambda i: i["recusou"], recusas),
        "latencia_media_s": _media(i["latencia_s"] for i in itens if i["latencia_s"]),
        "tokens_medios": _media(i["tokens"] for i in itens if i["tokens"]),
        "erros": [i["id"] for i in itens if i.get("erro")],
    }


def _salvar(rotulo: str, provider: str, modelo: str, descricao: str, config: dict, itens: list[dict], resumo: dict):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    dados = {
        "rotulo": rotulo, "provider": provider, "modelo": modelo, "descricao": descricao,
        "gerado_em": datetime.now().isoformat(timespec="seconds"), "config": config,
        "resumo": resumo, "itens": itens,
    }
    base = RESULTS_DIR / f"ragas_{rotulo}_{provider}"
    base.with_suffix(".json").write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")

    linhas = [
        f"# RAGAS — {rotulo} ({provider}: `{modelo}`)", "", descricao, "",
        f"Gerado em {dados['gerado_em']} · config: `{json.dumps(config, ensure_ascii=False)}`", "",
        "| Métrica | Valor |", "|---|---|",
        *[f"| {k} | {v} |" for k, v in resumo.items()], "",
        "| Caso | faithfulness (RAGAS) | answer_relevancy (RAGAS) | rubrica F/AR | acerto | citação | resposta |",
        "|---|---|---|---|---|---|---|",
    ]
    for i in itens:
        rg, rb = i.get("ragas", {}), i.get("rubrica", {})
        fmt = lambda v: "—" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:.2f}"  # noqa: E731
        resposta = i["resposta"].replace("\n", " ").replace("|", "/")[:220]
        linhas.append(
            f"| {i['id']} | {fmt(rg.get('faithfulness'))} | {fmt(rg.get('answer_relevancy'))} | "
            f"{fmt(rb.get('faithfulness'))}/{fmt(rb.get('answer_relevancy'))} | "
            f"{'—' if i.get('acerto_factual') is None else ('ok' if i['acerto_factual'] else 'FALHOU')} | "
            f"{', '.join(i.get('citacoes', [])) or '—'} | {resposta} |"
        )
    base.with_suffix(".md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"  -> {base.with_suffix('.md').relative_to(RESULTS_DIR.parent.parent)}")


def gerar_tabela() -> None:
    execucoes = [json.loads(p.read_text(encoding="utf-8")) for p in RESULTS_DIR.glob("ragas_*.json")]
    ordem = {r: n for n, r in enumerate(ORDEM)}
    execucoes.sort(key=lambda e: (e["provider"] != "ollama", ordem.get(e["rotulo"], 99)))
    fmt = lambda v, s="": "—" if v is None else f"{v}{s}"  # noqa: E731
    linhas = [
        "# Scores por iteração (RAGAS + rubrica de fallback)", "",
        "Gerado por `python -m evals.run_ragas`. Mesmo eval set em todas as linhas "
        f"(`evals/rag_eval_set.py`: {len(RESPONDIVEIS)} perguntas respondíveis + "
        f"{len(CASOS) - len(RESPONDIVEIS)} de recusa). Juiz: `gemma4:cloud`, temperature 0. "
        "Detalhes por caso em `evals/results/ragas_<iteração>_<provider>.md`.", "",
        "| Iteração | Modelo | Configuração | Faithfulness (RAGAS) | Answer relevancy (RAGAS) | "
        "Faithfulness (rubrica) | Answer relevancy (rubrica) | Doc. certo recuperado | Citação presente | "
        "Citação correta | Acerto factual | Recusa correta | Latência (s) |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for e in execucoes:
        r = e["resumo"]
        linhas.append(
            f"| {e['rotulo']} | `{e['modelo']}` | {e['descricao']} | {fmt(r['faithfulness_ragas'])} | "
            f"{fmt(r['answer_relevancy_ragas'])} | {fmt(r['faithfulness_rubrica'])} | "
            f"{fmt(r['answer_relevancy_rubrica'])} | {fmt(r['hit_documento_pct'], '%')} | "
            f"{fmt(r['citacao_presente_pct'], '%')} | {fmt(r['citacao_correta_pct'], '%')} | "
            f"{fmt(r['acerto_factual_pct'], '%')} | {fmt(r['recusa_correta_pct'], '%')} | {fmt(r['latencia_media_s'])} |"
        )
    SCORES_MD.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"Tabela consolidada: {SCORES_MD.relative_to(SCORES_MD.parent.parent)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--iteracao", choices=list(ITERACOES))
    parser.add_argument("--provider", choices=list(PROVIDERS), default="ollama")
    parser.add_argument("--metodo", choices=["ambos", "ragas", "rubrica", "auto"], default="ambos")
    parser.add_argument("--respostas", help="JSON com respostas já geradas (ex.: baseline da Sprint 03)")
    parser.add_argument("--rotulo", help="rótulo da execução quando usar --respostas")
    parser.add_argument("--tabela", action="store_true", help="só regenera SCORES_POR_ITERACAO.md")
    args = parser.parse_args()

    if args.tabela:
        gerar_tabela()
        return

    settings = load_settings()
    if args.respostas:
        externo = json.loads(Path(args.respostas).read_text(encoding="utf-8"))
        itens, rotulo = externo["itens"], args.rotulo or externo["rotulo"]
        provider, modelo, descricao, config = externo["provider"], externo["modelo"], externo["descricao"], externo["config"]
    else:
        it = ITERACOES[args.iteracao]
        if it.tipo == "legado" and args.provider != "ollama":
            parser.error("a versão legada só roda no Provider A (Ollama Cloud), como nas Sprints 1/2 refeitas.")
        rotulo, provider = it.rotulo, args.provider
        modelo, descricao = modelo_padrao(provider, settings), it.descricao
        config = {
            "chunking": it.estrategia, "k": it.k, "prompt_rag": it.prompt, "busca": it.busca,
            "limiar": it.limiar, "temperature": settings.temperature, "top_p": settings.top_p,
            "max_tokens": settings.max_tokens, "embeddings": f"{settings.embeddings_backend}/nomic-embed-text",
        } if it.tipo == "rag" else {"rag": False, "prompt": "system_prompt_v1", "temperature": settings.temperature}
        print(f"Gerando respostas — {rotulo} ({provider}: {modelo})", flush=True)
        itens = gerar_respostas(it, provider)

    resumo = pontuar(itens, args.metodo)
    _salvar(rotulo, provider, modelo, descricao, config, itens, resumo)
    print(json.dumps(resumo, indent=2, ensure_ascii=False))
    gerar_tabela()


if __name__ == "__main__":
    main()
