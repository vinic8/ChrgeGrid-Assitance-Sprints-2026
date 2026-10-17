# Teste de recuperação com paráfrases (sem LLM)

Gerado em 2026-10-17T16:47:11 por `python -m evals.test_recuperacao`. Chunking `por_secao_tabelas`, k=6. Paráfrases: perguntas novas, fora do eval set, escritas sem o vocabulário dos documentos.

| Busca | Paráfrases com a seção certa no top-k | Eval set: doc. certo no top-k | Melhor score da respondível mais fraca | Melhor score da recusa mais forte |
|---|---|---|---|---|
| `vetorial` | 4/10 | 17/18 | 0.716 | 0.666 |
| `hibrida` | 8/10 | 18/18 | 0.716 | 0.666 |
| `hibrida_expandida` | 10/10 | 18/18 | 0.716 | 0.666 |

## Paráfrases que falharam

- `vetorial`: "O carregador C11 fez uma recarga das 18:30 às 19:00, com consumo de 5 kWh. Quanto fica o faturamento?"; "Quanto custa carregar às 19h?"; "Quanto o cliente paga por 10 kWh carregados às 2 da manhã?"; "Quanto cobrar de um carro que carregou 12 kWh entre 21h e 22h?"; "Quanto tempo o morador pode ficar na vaga depois que a bateria encheu?"; "Qual registrador mostra se o carro está conectado?"
- `hibrida`: "O carregador C11 fez uma recarga das 18:30 às 19:00, com consumo de 5 kWh. Quanto fica o faturamento?"; "Quanto custa carregar às 19h?"
- `hibrida_expandida`: nenhuma

## Pipeline completo (`gemma4:cloud`, busca `hibrida_expandida`, k=6, porta 0.0, prompt RAG v4)

| Teste | Resultado |
|---|---|
| Paráfrases respondidas citando o documento certo | 10/10 |
| Perguntas fora do domínio recusadas | 6/6 |
