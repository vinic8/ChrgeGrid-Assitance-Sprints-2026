# Rubrica manual de fallback do RAGAS

A Sprint 04 aceita uma rubrica manual equivalente (0–1) para `faithfulness` e
`answer_relevancy` caso o ambiente não suporte o RAGAS. Neste projeto o RAGAS
**roda** (RAGAS 0.4.3 com o shim de `evals/ragas_compat.py`), e a rubrica é aplicada
**junto** com ele, no mesmo eval set e em todas as iterações. Assim ela fica pronta
para assumir caso o RAGAS quebre (`python -m evals.run_ragas --metodo rubrica`, ou
`--metodo auto`, que cai na rubrica sozinho se o RAGAS lançar erro) e a equivalência
entre as duas medições é justificada com números, não só com argumento.

## Critérios

A nota de cada dimensão é um de cinco níveis: 0, 0,25, 0,5, 0,75 ou 1.

### Faithfulness: a resposta é sustentada pelos trechos recuperados?

| Nota | Critério |
|---|---|
| 1,0 | Todas as afirmações factuais estão nos trechos. Contas aritméticas corretas sobre números dos trechos ou da pergunta contam como sustentadas. |
| 0,75 | Um detalhe secundário não está nos trechos, mas não altera a resposta. |
| 0,5 | Parte relevante das afirmações está nos trechos e parte não. |
| 0,25 | A maior parte das afirmações não está nos trechos. |
| 0,0 | Contradiz os trechos ou inventa o dado principal. |

Caso especial: se a resposta apenas diz que a informação não consta na base, a
faithfulness é 1,0 (nada foi afirmado sem suporte).

### Answer relevancy: a resposta entrega o que foi perguntado?

Primeiro, identifique o dado específico que a pergunta pede (valor, prazo, código,
nome, sim/não).

| Nota | Critério |
|---|---|
| 1,0 | Entrega esse dado de forma direta e completa, sem desvio. |
| 0,75 | Entrega o dado, mas com informação desnecessária ou com um ponto secundário faltando. |
| 0,5 | Entrega só parte do que foi pedido. |
| 0,25 | Fala do assunto, mas não entrega o dado pedido. |
| 0,0 | Não responde: diz que não sabe, que não consta, que é preciso consultar outro lugar, ou responde outra coisa. |

Falar do mesmo assunto não basta para nota alta: sem o dado pedido, a nota é no
máximo 0,25.

**Revisão da rubrica (iteração 2 → 3):** a primeira versão desta dimensão dizia só
"responde direta e completamente ao que foi perguntado". Com ela, o juiz deu 1,0 em
todos os 18 casos da iteração 1, inclusive no R10, em que o modelo respondeu "é
necessário consultar a seção de especificações do manual" sem dar o grau de
proteção. O juiz estava avaliando se a resposta era do mesmo assunto, não se
entregava o dado. O critério passou a ancorar a nota no dado pedido, e todas as
execuções (legado, Sprint 03, it1, it2) foram repontuadas com a rubrica revisada
sobre as mesmas respostas já geradas, sem chamar os modelos de novo.

## Por que é equivalente ao RAGAS

- **Faithfulness**: o RAGAS quebra a resposta em afirmações e calcula a fração
  delas que pode ser inferida dos trechos recuperados. A rubrica avalia a mesma
  coisa (proporção da resposta sustentada pelos trechos), discretizada em 5 níveis
  que correspondem às faixas 100%, ~75%, ~50%, ~25% e 0% de afirmações sustentadas.
- **Answer relevancy**: o RAGAS gera perguntas a partir da resposta e mede a
  similaridade de cosseno com a pergunta original. Uma resposta incompleta, que
  desvia do assunto ou recusa sem motivo gera perguntas diferentes e baixa a
  similaridade. A rubrica julga esses mesmos três defeitos diretamente.
- **Mesmas entradas**: as duas medições usam a mesma pergunta, os mesmos trechos
  recuperados e a mesma resposta de cada caso, e o mesmo juiz (`gemma4:cloud`,
  temperature 0). A concordância observada está em `docs/relatorio_rag.md`.

## Como aplicar manualmente (sem LLM)

Para cada caso `respondivel` de `evals/rag_eval_set.py`, abra
`evals/results/ragas_<iteração>_<provider>.json`. Em cada item, leia `pergunta`,
`contextos` e `resposta` e anote as duas notas segundo as tabelas acima. A média
dos casos é o score da iteração. O módulo `evals/rubrica_manual.py` aplica
exatamente este texto por meio do LLM juiz, para a rubrica poder ser
reexecutada a cada iteração sem trabalho manual.
