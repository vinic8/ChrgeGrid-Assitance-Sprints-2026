"""Fallback manual do RAGAS: rubrica equivalente (0–1) para faithfulness e answer_relevancy.

A rubrica está descrita em `evals/RUBRICA_FALLBACK.md` (critérios e justificativa
da equivalência). Ela foi escrita para ser aplicada por uma pessoa — este módulo
só automatiza a aplicação, pedindo a um LLM juiz que siga exatamente os mesmos
critérios e devolva a nota de cada dimensão. É usada:

- automaticamente, quando o RAGAS falha no ambiente (`run_ragas.py --metodo auto`);
- em paralelo ao RAGAS (`--metodo ambos`, padrão), para medir a concordância entre
  as duas medições no mesmo eval set — é essa concordância que sustenta a
  equivalência no relatório.
"""
from __future__ import annotations

import json
import re

from langchain_core.language_models.chat_models import BaseChatModel

NIVEIS = (0.0, 0.25, 0.5, 0.75, 1.0)

PROMPT_RUBRICA = """Você é um avaliador de sistemas RAG. Avalie a RESPOSTA abaixo com a rubrica, \
usando SOMENTE os TRECHOS como verdade (não use conhecimento próprio).

PERGUNTA:
{pergunta}

TRECHOS RECUPERADOS:
{contextos}

RESPOSTA:
{resposta}

RUBRICA — faithfulness (a resposta é sustentada pelos trechos?):
1.0  = todas as afirmações factuais estão nos trechos (contas aritméticas corretas sobre números dos trechos ou da pergunta contam como sustentadas)
0.75 = um detalhe secundário não está nos trechos, mas não altera a resposta
0.5  = parte relevante das afirmações está nos trechos e parte não
0.25 = a maior parte não está nos trechos
0.0  = contradiz os trechos ou inventa o dado principal
(Se a resposta só diz que a informação não consta na base, faithfulness = 1.0.)

RUBRICA — answer_relevancy (a resposta entrega o que foi perguntado?):
Primeiro identifique o dado específico que a pergunta pede (valor, prazo, código, nome, sim/não).
1.0  = entrega esse dado de forma direta e completa, sem desvio
0.75 = entrega o dado, mas com informação desnecessária ou um ponto secundário faltando
0.5  = entrega só parte do que foi pedido
0.25 = fala do assunto, mas NÃO entrega o dado pedido
0.0  = não responde: diz que não sabe, que não consta, que é preciso consultar outro lugar,
       ou responde outra coisa — mesmo que de forma educada e no tema
(Falar do mesmo assunto NÃO basta para nota alta: sem o dado pedido, a nota é no máximo 0.25.)

Responda APENAS com JSON: {{"faithfulness": <nivel>, "answer_relevancy": <nivel>, "motivo": "<uma frase>"}}"""


def _nivel(valor) -> float:
    v = float(valor)
    return min(NIVEIS, key=lambda n: abs(n - v))


def avaliar(juiz: BaseChatModel, pergunta: str, contextos: list[str], resposta: str) -> dict:
    texto_contextos = "\n\n".join(f"[{i}] {c}" for i, c in enumerate(contextos, 1)) or "(nenhum trecho)"
    saida = juiz.invoke(
        PROMPT_RUBRICA.format(pergunta=pergunta, contextos=texto_contextos, resposta=resposta)
    ).content
    bloco = re.search(r"\{.*\}", saida, re.DOTALL)
    dados = json.loads(bloco.group(0)) if bloco else {}
    return {
        "faithfulness": _nivel(dados.get("faithfulness", 0)),
        "answer_relevancy": _nivel(dados.get("answer_relevancy", 0)),
        "motivo": str(dados.get("motivo", "")),
    }
