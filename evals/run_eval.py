"""Reexecuta o eval set (evals/eval_cases.py) contra a versão legada e a LCEL,
e gera a tabela comparativo antes/depois exigida no Bloco D da rubrica.

Uso:
    python -m evals.run_eval

Requer OLLAMA_API_KEY configurada no .env — faz chamadas reais ao modelo,
os números aqui não são simulados.
"""
from __future__ import annotations

import json
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from evals.eval_cases import CASOS, CasoEval
from src.chain.builder import conversar
from src.chain.memoria import limpar_sessao
from src.manual_chat import conversar_legado, limpar_sessao_legada

RESULTS_DIR = Path(__file__).resolve().parent / "results"


@dataclass
class ResultadoCaso:
    id: str
    categoria: str
    versao: str
    passou: bool
    latencia_s: float
    tokens_entrada: int
    tokens_saida: int
    structured_ok: bool | None  # None = não aplicável (legado não tem structured output)
    resposta: str = ""  # texto da última resposta, para auditar falhas sem reproduzir manualmente
    erro: str | None = None


def _rodar_legado(caso: CasoEval) -> ResultadoCaso:
    session_id = f"eval-legado-{caso.id}"
    limpar_sessao_legada(session_id)
    try:
        latencias, tok_in, tok_out = [], 0, 0
        ultima = None
        for turno in caso.turnos:
            ultima = conversar_legado(session_id, turno)
            latencias.append(ultima.latencia_s)
            tok_in += ultima.tokens_entrada
            tok_out += ultima.tokens_saida
        return ResultadoCaso(
            id=caso.id,
            categoria=caso.categoria,
            versao="legado",
            passou=caso.verificar(ultima.texto),
            latencia_s=statistics.mean(latencias),
            tokens_entrada=tok_in,
            tokens_saida=tok_out,
            structured_ok=None,
            resposta=ultima.texto,
        )
    except Exception as exc:  # noqa: BLE001 - eval não deve derrubar o processo inteiro
        return ResultadoCaso(
            id=caso.id, categoria=caso.categoria, versao="legado", passou=False,
            latencia_s=0.0, tokens_entrada=0, tokens_saida=0, structured_ok=None, erro=str(exc),
        )
    finally:
        limpar_sessao_legada(session_id)


def _rodar_lcel(caso: CasoEval) -> ResultadoCaso:
    session_id = f"eval-lcel-{caso.id}"
    limpar_sessao(session_id)
    try:
        latencias, tok_in, tok_out = [], 0, 0
        ultima = None
        for turno in caso.turnos:
            ultima = conversar(session_id, turno)
            latencias.append(ultima.latencia_s)
            tok_in += ultima.tokens_entrada
            tok_out += ultima.tokens_saida
        return ResultadoCaso(
            id=caso.id,
            categoria=caso.categoria,
            versao="lcel",
            passou=caso.verificar(ultima.resultado.justificativa),
            latencia_s=statistics.mean(latencias),
            tokens_entrada=tok_in,
            tokens_saida=tok_out,
            structured_ok=True,
            resposta=ultima.resultado.justificativa,
        )
    except Exception as exc:  # noqa: BLE001
        return ResultadoCaso(
            id=caso.id, categoria=caso.categoria, versao="lcel", passou=False,
            latencia_s=0.0, tokens_entrada=0, tokens_saida=0, structured_ok=False, erro=str(exc),
        )
    finally:
        limpar_sessao(session_id)


def _resumo(resultados: list[ResultadoCaso], versao: str) -> dict:
    todos = [r for r in resultados if r.versao == versao]
    validos = [r for r in todos if r.erro is None]
    if not todos:
        return {"nota": 0.0, "tokens_por_turno": 0.0, "latencia_media_s": 0.0, "acuracia_structured_pct": None}

    nota = round(10 * sum(r.passou for r in todos) / len(todos), 1)
    if validos:
        tokens_por_turno = round(statistics.mean(r.tokens_entrada + r.tokens_saida for r in validos), 1)
        latencia_media = round(statistics.mean(r.latencia_s for r in validos), 2)
    else:
        tokens_por_turno = 0.0
        latencia_media = 0.0

    structured_vals = [r.structured_ok for r in todos if r.structured_ok is not None]
    acuracia = round(100 * sum(structured_vals) / len(structured_vals), 1) if structured_vals else None

    return {
        "nota": nota,
        "tokens_por_turno": tokens_por_turno,
        "latencia_media_s": latencia_media,
        "acuracia_structured_pct": acuracia,
    }


def rodar() -> dict:
    resultados: list[ResultadoCaso] = []
    for caso in CASOS:
        print(f"[legado] {caso.id} ({caso.categoria})...", flush=True)
        resultados.append(_rodar_legado(caso))
        print(f"[lcel]   {caso.id} ({caso.categoria})...", flush=True)
        resultados.append(_rodar_lcel(caso))

    return {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "casos": [asdict(r) for r in resultados],
        "resumo": {
            "legado": _resumo(resultados, "legado"),
            "lcel": _resumo(resultados, "lcel"),
        },
    }


def _tabela_markdown(resultado: dict) -> str:
    legado = resultado["resumo"]["legado"]
    lcel = resultado["resumo"]["lcel"]
    structured_lcel = f"{lcel['acuracia_structured_pct']}%" if lcel["acuracia_structured_pct"] is not None else "N/A"
    linhas = [
        "| Métrica | Sprints 1/2 (versão manual/legado) | Sprint 03 (LCEL) |",
        "|---|---|---|",
        f"| Qualidade das respostas (nota no eval, 0-10) | {legado['nota']} | {lcel['nota']} |",
        f"| Tokens por turno (média) | {legado['tokens_por_turno']} | {lcel['tokens_por_turno']} |",
        f"| Latência média (s) | {legado['latencia_media_s']} | {lcel['latencia_media_s']} |",
        f"| Acurácia do structured output | N/A (sem schema) | {structured_lcel} |",
    ]
    return "\n".join(linhas)


if __name__ == "__main__":
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    resultado = rodar()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    (RESULTS_DIR / f"comparativo_{timestamp}.json").write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    tabela = _tabela_markdown(resultado)
    (RESULTS_DIR / f"comparativo_{timestamp}.md").write_text(tabela, encoding="utf-8")

    print("\n" + tabela)
    print(f"\nResultados salvos em evals/results/comparativo_{timestamp}.{{json,md}}")
