# Relatório de modelos e parâmetros — Sprint 04

Comparativo dos dois modelos do projeto no pipeline RAG, com os parâmetros de geração
e de recuperação documentados. O comparativo foi feito na configuração da **iteração 3**
(chunking com tabelas, busca híbrida, prompt RAG v3). Os dados vêm de
`evals/results/ragas_it3_ollama.*` e `evals/results/ragas_it3_groq.*`.

## 1. Modelos e providers

| | Provider A | Provider B |
|---|---|---|
| Modelo | **Gemma 4** — `gemma4:cloud` | **Qwen 3.8 27B** — `qwen/qwen3.8-27b` |
| Provider | Ollama Cloud (`https://ollama.com`) | Groq |
| Cliente LangChain | `ChatOllama` | `ChatGroq` |
| Papel no projeto | Modelo padrão do chat, gerador das iterações do RAGAS e juiz do RAGAS/rubrica | Segundo modelo do comparativo e do modo multi-provider |
| Limites do plano usado | Recusa requisições simultâneas acima do limite do plano (HTTP 429 "too many concurrent requests") | 8.000 tokens/minuto (plano gratuito) |

Os dois rodam exatamente a mesma chain (`src/chain/builder.py`), o mesmo prompt
(persona v7 + prompt RAG v3 neste comparativo) e os mesmos trechos recuperados. Só o
LLM muda.

## 2. Parâmetros

| Parâmetro | Valor | Onde | Justificativa |
|---|---|---|---|
| `temperature` | **0** | `TEMPERATURE` | Recomendado no enunciado. Num RAG com grounding, a resposta deve ser a mais provável dado o contexto, sem variação criativa. É também o que torna o eval reexecutável. A Sprint 03 usava 0,2. |
| `top_p` | 0,9 | `TOP_P` (`top_p` no Ollama, `model_kwargs` no Groq) | Com temperature 0, a decodificação é praticamente gulosa e o `top_p` quase não age. Fica documentado e configurável para quem quiser subir a temperatura. |
| `max_tokens` | 800 | `MAX_TOKENS` (`num_predict` no Ollama) | A saída é um JSON (`ConsultaRecarga`) com a justificativa e a citação. A Sprint 03 usava 600, e respostas com cálculo e citação chegavam perto do limite. As respostas da it3 têm em média 297 (Gemma) e 340 (Qwen) caracteres de justificativa. |
| `k` (top-k) | 5 neste comparativo; 6 na configuração final | `RAG_K` | Medido nas iterações: k=3 (it1) não cobria perguntas que cruzam duas seções; k=5 recuperou o documento certo em 100% das perguntas da it3. |
| Busca | híbrida (vetorial + BM25, RRF) neste comparativo; a configuração final usa a híbrida com expansão de consulta | `RAG_BUSCA` | Corrige o viés do nomic-embed-text em português (ver `docs/relatorio_rag.md` §5). |
| Limiar de relevância | 0,69 neste comparativo; desligado na configuração final | `RAG_LIMIAR_RELEVANCIA` | Calibrado no eval set, mas recusava perguntas legítimas curtas; removido na iteração 6 (`docs/relatorio_rag.md` §5). |
| Embeddings | `nomic-embed-text` (v1.5, 768 d) | `EMBEDDINGS_BACKEND` | Exigido no enunciado; roda localmente via FastEmbed porque a Ollama Cloud retorna 401 para embeddings. |
| Timeout | 90 s | `src/chain/builder.py` | Herdado da Sprint 03: sem timeout, uma chamada travada no provider prendia a UI. |
| Retries | 5 tentativas com backoff exponencial (chain) + 6 no cliente Groq | `src/chain/builder.py` | HTTP 429 da Ollama Cloud (concorrência) e do Groq (tokens/minuto). |

## 3. Resultados (mesmo eval set, mesma configuração)

Eval set: 18 perguntas respondíveis + 3 de recusa (`evals/rag_eval_set.py`). Juiz:
`gemma4:cloud`, temperature 0.

| Métrica | Gemma 4 (Ollama Cloud) | Qwen 3.8 (Groq) |
|---|---|---|
| Faithfulness (RAGAS) | 0,887 | **0,897** |
| Answer relevancy (RAGAS) | 0,785 | **0,824** |
| Faithfulness (rubrica) | 1,000 | 1,000 |
| Answer relevancy (rubrica) | **1,000** | 0,944* |
| Documento certo recuperado | 100% | 100% |
| Citação presente / correta | 100% / 100% | 100% / 100% |
| Acerto factual | 100% | 100% |
| Recusa correta (fora da base) | 3/3 | 3/3 |
| Tamanho médio da resposta | 297 caracteres | 340 caracteres |
| Latência média por pergunta (eval) | **1,73 s** (mediana 1,63 s) | 29,2 s (mediana 33,2 s)** |

\* A diferença na rubrica vem de um único caso, o R18 ("Qual a potência do
GW30K-HCA-20?"). As duas respostas são corretas e quase idênticas ("O modelo
GW30K-HCA-20 não existe na linha HCA G2..."), mas o juiz deu 0 à do Qwen, com o motivo
de que "informa que o modelo não consta na base", e 1,0 à do Gemma. É um erro do juiz,
mantido no resultado para não ajustar números à mão e registrado como limitação do
LLM-como-juiz.

\*\* A latência do Qwen no eval inclui a espera pelo limite de tokens por minuto: com
~3.800 tokens por pergunta e limite de 8.000 tokens/minuto, as chamadas entram na fila de
retry do cliente Groq. Ela não mede a velocidade de inferência do modelo.

## 4. Leitura

- **Qualidade**: empate técnico. Os dois acertam 100% das perguntas, citam a fonte
  certa em 100% dos casos e recusam corretamente as 3 perguntas sem base. O Qwen fica
  0,01 acima em faithfulness e 0,04 acima em answer relevancy no RAGAS. A diferença de
  faithfulness está dentro do ruído da geração que medimos repetindo uma iteração
  (~0,04; `docs/relatorio_rag.md` §6). Como o juiz é o próprio Gemma, um eventual viés de
  autoavaliação favoreceria o Gemma, e mesmo assim o Qwen não ficou atrás.
- **Estilo**: o Qwen escreve respostas ~15% mais longas e às vezes acrescenta uma
  frase de contexto ("Para fins de faturamento e auditoria..."). O Gemma é mais seco e
  responde na primeira frase, como pede a regra RESPOSTA DIRETA da v3.
- **Latência e operação**: o Gemma via Ollama Cloud responde em ~1,7 s. O Qwen via
  Groq, no plano gratuito, fica limitado a 8.000 tokens por minuto. Cada pergunta do
  RAG usa ~3.800 tokens de prompt com a v3 (medido com o tokenizer o200k: ~2.800 de
  persona, instruções RAG e format instructions do schema, mais ~1.000 de pergunta e 5
  trechos), então cabem só 2 perguntas por minuto, e o resto espera na fila de retry.
- **Decisão**: o **Gemma 4 é o modelo padrão** do chat, pela latência compatível com
  conversa e pela qualidade igual. O **Qwen** continua disponível na interface e no
  modo multi-provider (bônus), em que a comparação lado a lado com o Gemma e com duas
  versões do prompt ajuda o operador a conferir respostas críticas.

## 5. Bônus multi-provider

`src/chain/multi_provider.py` consulta, para a mesma pergunta, as 4 combinações
{Gemma 4, Qwen 3.8} × {prompt RAG v2, v4} em paralelo. A recuperação é feita uma vez e
compartilhada. Cada combinação roda numa sessão sem memória e devolve a resposta, as
citações e a latência. Está disponível na aba "Multi-provider" da interface e no
terminal (`python -m src.chain.multi_provider "pergunta"`).

## 6. Como reproduzir

```bash
python -m evals.run_ragas --iteracao it3                   # Gemma
python -m evals.run_ragas --iteracao it3 --provider groq   # Qwen
python -m evals.test_injecao
```
