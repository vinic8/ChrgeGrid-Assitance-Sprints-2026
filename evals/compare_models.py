"""Comparativo multi-provider (Bloco B), com parâmetros documentados.

Isola a variável "provider/modelo": mesma chain LCEL, mesmo prompt v2, mesmos
casos de `evals/eval_cases.py`, variando só o provider por trás — Ollama Cloud
(Provider A) vs. Groq (Provider B), ver `src/chain/builder.PROVIDERS`. A
comparação de arquitetura (legado vs LCEL) já é feita em `run_eval.py` — aqui o
que muda é o LLM/provider, não o pipeline.

Uso:
    python -m evals.compare_models
"""
from __future__ import annotations

import json
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from evals.eval_cases import CASOS, CasoEval
from src.chain.builder import PROVIDERS, conversar, modelo_padrao
from src.chain.memoria import limpar_sessao
from src.config import load_settings

RESULTS_DIR = Path(__file__).resolve().parent / "results"


@dataclass
class ResultadoCasoProvider:
    id: str
    categoria: str
    provider: str
    modelo: str
    passou: bool
    latencia_s: float
    tokens_entrada: int
    tokens_saida: int
    resposta: str = ""  # texto da última resposta, para auditar falhas sem reproduzir manualmente
    erro: str | None = None


def _rodar_caso(caso: CasoEval, provider: str, modelo: str) -> ResultadoCasoProvider:
    session_id = f"cmp-{provider}-{caso.id}"
    limpar_sessao(session_id)
    try:
        latencias, tok_in, tok_out = [], 0, 0
        ultima = None
        for turno in caso.turnos:
            ultima = conversar(session_id, turno, model=modelo, provider=provider)
            latencias.append(ultima.latencia_s)
            tok_in += ultima.tokens_entrada
            tok_out += ultima.tokens_saida
        return ResultadoCasoProvider(
            id=caso.id,
            categoria=caso.categoria,
            provider=provider,
            modelo=modelo,
            passou=caso.verificar(ultima.resultado.justificativa),
            latencia_s=statistics.mean(latencias),
            tokens_entrada=tok_in,
            tokens_saida=tok_out,
            resposta=ultima.resultado.justificativa,
        )
    except Exception as exc:  # noqa: BLE001 - eval não deve derrubar o processo inteiro
        return ResultadoCasoProvider(
            id=caso.id, categoria=caso.categoria, provider=provider, modelo=modelo, passou=False,
            latencia_s=0.0, tokens_entrada=0, tokens_saida=0, erro=str(exc),
        )
    finally:
        limpar_sessao(session_id)


def _resumo(resultados: list[ResultadoCasoProvider], provider: str) -> dict:
    todos = [r for r in resultados if r.provider == provider]
    validos = [r for r in todos if r.erro is None]
    if not todos:
        return {"nota": 0.0, "tokens_por_turno": 0.0, "latencia_media_s": 0.0, "falhas": []}

    nota = round(10 * sum(r.passou for r in todos) / len(todos), 1)
    tokens_por_turno = round(statistics.mean(r.tokens_entrada + r.tokens_saida for r in validos), 1) if validos else 0.0
    latencia_media = round(statistics.mean(r.latencia_s for r in validos), 2) if validos else 0.0
    falhas = [r.id for r in todos if not r.passou]

    return {
        "nota": nota,
        "tokens_por_turno": tokens_por_turno,
        "latencia_media_s": latencia_media,
        "falhas": falhas,
    }


def rodar() -> dict:
    settings = load_settings()
    providers = list(PROVIDERS.keys())
    resultados: list[ResultadoCasoProvider] = []

    for provider in providers:
        modelo = modelo_padrao(provider, settings)
        for caso in CASOS:
            print(f"[{provider}:{modelo}] {caso.id} ({caso.categoria})...", flush=True)
            resultados.append(_rodar_caso(caso, provider, modelo))

    return {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "parametros": {
            "temperature": settings.temperature,
            "max_tokens": settings.max_tokens,
            "system_prompt_version": settings.system_prompt_version,
        },
        "casos": [asdict(r) for r in resultados],
        "resumo": {provider: _resumo(resultados, provider) for provider in providers},
    }


def _tabela_markdown(resultado: dict) -> str:
    params = resultado["parametros"]
    params_str = f"temp={params['temperature']} / max_tokens={params['max_tokens']}"
    modelos_por_provider = {
        r["provider"]: r["modelo"] for r in resultado["casos"]
    }
    linhas = [
        f"Parâmetros (iguais nas duas execuções): `{params_str}`, prompt `{params['system_prompt_version']}`, "
        f"{len(CASOS)} casos de `evals/eval_cases.py`.",
        "",
        "| Provider | Modelo | Parâmetros | Nota no eval (0-10) | Tokens/turno (média) | Latência média (s) | Casos que falharam |",
        "|---|---|---|---|---|---|---|",
    ]
    for provider, resumo in resultado["resumo"].items():
        falhas = ", ".join(resumo["falhas"]) if resumo["falhas"] else "—"
        linhas.append(
            f"| {PROVIDERS[provider]} | `{modelos_por_provider.get(provider, '?')}` | {params_str} | "
            f"{resumo['nota']} | {resumo['tokens_por_turno']} | {resumo['latencia_media_s']} | {falhas} |"
        )
    return "\n".join(linhas)


if __name__ == "__main__":
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    resultado = rodar()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    (RESULTS_DIR / f"modelos_{timestamp}.json").write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    tabela = _tabela_markdown(resultado)
    (RESULTS_DIR / f"modelos_{timestamp}.md").write_text(tabela, encoding="utf-8")

    print("\n" + tabela)
    print(f"\nResultados salvos em evals/results/modelos_{timestamp}.{{json,md}}")
