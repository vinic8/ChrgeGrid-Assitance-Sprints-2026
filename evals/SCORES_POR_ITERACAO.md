# Scores por iteração (RAGAS + rubrica de fallback)

Gerado por `python -m evals.run_ragas`. Mesmo eval set em todas as linhas (`evals/rag_eval_set.py`: 18 perguntas respondíveis + 3 de recusa). Juiz: `gemma4:cloud`, temperature 0. Detalhes por caso em `evals/results/ragas_<iteração>_<provider>.md`.

| Iteração | Modelo | Configuração | Faithfulness (RAGAS) | Answer relevancy (RAGAS) | Faithfulness (rubrica) | Answer relevancy (rubrica) | Doc. certo recuperado | Citação presente | Citação correta | Acerto factual | Recusa correta | Latência (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| legado | `gemma4:cloud` | Sprints 1/2: sem RAG, prompt v1 em texto corrido, saída em texto livre | 0.137 | 0.732 | 0.097 | 0.681 | 0.0% | 0.0% | 0.0% | 33.3% | 33.3% | 1.696 |
| sprint03 | `gemma4:cloud` | Sprint 03 (commit 244a814): FAISS + FastEmbed MiniLM, 4 docs .md, k=6, prompt v6, sem citação | 0.497 | 0.655 | 0.847 | 0.722 | 66.7% | 0.0% | 0.0% | 55.6% | 66.7% | 1.3 |
| it1 | `gemma4:cloud` | Baseline Sprint 04: chunk por página (1000/0), sem normalização, k=3, prompt RAG v1 | 0.751 | 0.717 | 0.875 | 0.861 | 94.4% | 5.6% | 0.0% | 77.8% | 100.0% | 1.206 |
| it2 | `gemma4:cloud` | Chunk por seção (800/120) + NFKC + cabeçalho, k=5, prompt RAG v2 (grounding + citação) | 0.856 | 0.767 | 0.917 | 0.931 | 94.4% | 94.4% | 88.9% | 88.9% | 100.0% | 1.263 |
| it3 | `gemma4:cloud` | Tabelas linha a linha + busca híbrida (vetorial + BM25) + limiar 0,69, k=5, prompt RAG v3 | 0.887 | 0.785 | 1.0 | 1.0 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 1.73 |
| it4 | `gemma4:cloud` | Recuperação da it3 + prompt RAG v4 (resposta direta que retoma o sujeito da pergunta) | 0.902 | 0.821 | 1.0 | 1.0 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 2.202 |
| it5 | `gemma4:cloud` | it4 + expansão de consulta no BM25 com 1 vaga garantida ao BM25 (busca hibrida_expandida), k=6 | 0.896 | 0.821 | 1.0 | 1.0 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 1.198 |
| it6 | `gemma4:cloud` | it5 sem a porta de relevância + base sem os 2 trechos escritos sob medida para o eval set | 0.895 | 0.777 | 1.0 | 0.944 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 1.452 |
| it3_prompt_v2 | `gemma4:cloud` | Ablação: recuperação da it3 (tabelas + híbrida + limiar) com o prompt RAG v2 | 0.892 | 0.806 | 1.0 | 1.0 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 2.123 |
| it3 | `qwen/qwen3.8-27b` | Tabelas linha a linha + busca híbrida (vetorial + BM25) + limiar 0,69, k=5, prompt RAG v3 | 0.897 | 0.824 | 1.0 | 0.944 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 29.244 |
