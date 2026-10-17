# RAGAS — it4 (ollama: `gemma4:cloud`)

Recuperação da it3 + prompt RAG v4 (resposta direta que retoma o sujeito da pergunta)

Gerado em 2026-10-17T15:58:25 · config: `{"chunking": "por_secao_tabelas", "k": 5, "prompt_rag": "v4", "busca": "hibrida", "limiar": 0.69, "temperature": 0.0, "top_p": 0.9, "max_tokens": 800, "embeddings": "fastembed/nomic-embed-text"}`

| Métrica | Valor |
|---|---|
| faithfulness_ragas | 0.902 |
| answer_relevancy_ragas | 0.821 |
| faithfulness_rubrica | 1.0 |
| answer_relevancy_rubrica | 1.0 |
| hit_documento_pct | 100.0 |
| citacao_presente_pct | 100.0 |
| citacao_correta_pct | 100.0 |
| acerto_factual_pct | 100.0 |
| recusa_indevida_pct | 0.0 |
| recusa_correta_pct | 100.0 |
| latencia_media_s | 2.202 |
| tokens_medios | 952.095 |
| erros | [] |

| Caso | faithfulness (RAGAS) | answer_relevancy (RAGAS) | rubrica F/AR | acerto | citação | resposta |
|---|---|---|---|---|---|---|
| R01 | 0.57 | 0.70 | 1.00/1.00 | ok | Tabelas Tarifárias — ChargeGrid Intelligence 2026 — 1. Postos tarifários (horário local, todos os dias) (p. 1) | O faturamento da recarga no carregador C11 é de R$ 8,25. O ciclo ocorreu integralmente no posto tarifário 'Ponta' (18:00 às 20:59), com tarifa de R$ 1,65/kWh. Cálculo: 5 kWh × R$ 1,65 = R$ 8,25. Fonte: Tabelas Tarifárias |
| R02 | 0.75 | 0.84 | 1.00/1.00 | ok | Tabelas Tarifárias — ChargeGrid Intelligence 2026 — 3. Tarifa de frota (p. 1) | Para o veículo FROTA-07, deve-se aplicar a tarifa fixa preferencial de frota de R$ 0,70/kWh, que se sobrepõe à tabela de postos tarifários. O cálculo do faturamento é: 20 kWh × R$ 0,70 = R$ 14,00. Fonte: Tabelas Tarifári |
| R03 | 0.57 | 0.80 | 1.00/1.00 | ok | FAQ de Carregamento — eletropostos GoodWe ChargeGrid — 5. Posso deixar o carro conectado depois que a carga terminar? (p. 1), Tabelas Tarifárias — ChargeGrid Intelligence 2026 — 6. Tarifa de ocupação ociosa (p. 1) | Sim, existe cobrança. No eletroposto comercial, há 15 minutos de tolerância após o fim da carga. Como o veículo permaneceu por 45 minutos (das 14:00 às 14:45), houve 30 minutos de ocupação ociosa. O cálculo é: 30 minutos |
| R04 | 1.00 | 0.76 | 1.00/1.00 | ok | Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 2. Códigos de exceção Modbus (p. 1) | O código de exceção Modbus 0x0002 significa 'Illegal Data Address', indicando que o endereço do registrador solicitado é inválido ou está fora do mapa suportado pelo modelo HCA G2. A ação imediata é conferir o endereço c |
| R05 | 1.00 | 0.82 | 1.00/1.00 | ok | Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 3. Códigos de falha do carregador (registradores 10001 a 10008) (p. 1), Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 5. Checklist de diagnóstico físico (RS485) (p. 2) | A falha de aterramento (grounding fault) do HCA G2 aparece no registrador 10002, bit1. A conduta técnica é interromper a operação e acionar um eletricista ou técnico habilitado antes de religar o equipamento, pois não é  |
| R06 | 1.00 | 0.93 | 1.00/1.00 | ok | Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 1. Formato de comunicação serial (RS485) (p. 1) | Os parâmetros de comunicação serial RS485 do carregador HCA G2 são:  / Parâmetro / Valor / / :--- / :--- / / Baud rate / 9600 / / Bits de dados / 8 / / Bits de parada / 1 / / Paridade / N (nenhuma) /  Fonte: Mapa Modbus  |
| R07 | 1.00 | 0.79 | 1.00/1.00 | ok | Interoperabilidade OCPP — camada de tradução do ChargeGrid — 1. Mapeamento de conceitos OCPP para registradores Modbus (p. 1), Interoperabilidade OCPP — camada de tradução do ChargeGrid — 2. Ciclo de sessão e cálculo do consumo (p. 1), Interoperabilidade OCPP — camada de tradução do ChargeGrid — 1. Mapeamento de conceitos OCPP para registradores Modbus (p. 1) | A mensagem StopTransaction do OCPP registra o meterStop (leitura do medidor após a carga) e o motivo do encerramento da sessão. No hardware GoodWe HCA G2, esses dados correspondem ao registrador Modbus 10172 (Meter Readi |
| R08 | 0.60 | 0.65 | 1.00/1.00 | ok | Interoperabilidade OCPP — camada de tradução do ChargeGrid — 2. Ciclo de sessão e cálculo do consumo (p. 1) | O consumo do ciclo foi de 27,50 kWh. O cálculo é realizado subtraindo o meterStart do meterStop (207250 - 204500 = 2750 unidades) e dividindo o resultado por 100, conforme a especificação dos registradores 10170 e 10172. |
| R09 | 1.00 | 0.89 | 1.00/1.00 | ok | Manual de Produto — EV Charger GoodWe HCA G2 — 1. Modelos da linha HCA G2 (p. 1) | A linha GoodWe HCA G2 possui três modelos com as seguintes potências nominais:  / Modelo / Potência nominal / / :--- / :--- / / GW7K-HCA-20 / 7 kW / / GW11K-HCA-20 / 11 kW / / GW22K-HCA-20 / 22 kW /  Fonte: Manual de Pro |
| R10 | 0.75 | 0.81 | 1.00/1.00 | ok | Manual de Produto — EV Charger GoodWe HCA G2 — 4. Dados gerais (p. 1) | O carregador HCA G2 pode ser instalado em ambiente exterior (ao ar livre), possuindo grau de proteção IP66 para o carregador e IP55 para o plugue de carregamento. Fonte: Manual de Produto — EV Charger GoodWe HCA G2, seçã |
| R11 | 1.00 | 0.91 | 1.00/1.00 | ok | Interoperabilidade OCPP — camada de tradução do ChargeGrid — Introdução (p. 1), Manual de Produto — EV Charger GoodWe HCA G2 — 2. Comunicação e protocolos (p. 1) | O carregador GoodWe HCA G2 não suporta OCPP nativamente; o protocolo declarado é Modbus TCP (backend) e Modbus RTU/RS485 (local). O ChargeGrid atua como uma camada de tradução e interoperabilidade que expõe os dados do M |
| R12 | 1.00 | 0.74 | 1.00/1.00 | ok | Regimento de Recarga Compartilhada em Condomínio — 4. Liberação da vaga após a recarga (p. 1) | No condomínio, o veículo deve ser retirado da vaga em até 30 minutos após a recarga ser encerrada (status carga completa). Fonte: Regimento de Recarga Compartilhada em Condomínio, seção 4. Liberação da vaga após a recarg |
| R13 | 1.00 | 0.81 | 1.00/1.00 | ok | Regimento de Recarga Compartilhada em Condomínio — 7. Penalidades (p. 1) | A ocupação indevida da vaga de recarga do condomínio pela segunda vez no mesmo semestre gera multa de 10% da taxa condominial. Fonte: Regimento de Recarga Compartilhada em Condomínio, seção 7. Penalidades. |
| R14 | 1.00 | 0.86 | 1.00/1.00 | ok | Regimento de Recarga Compartilhada em Condomínio — 3. Agendamento e tempo máximo de uso (p. 1) | Uma unidade pode reservar o carregador compartilhado do condomínio por no máximo 4 horas por dia, com antecedência de até 48 horas. Fonte: Regimento de Recarga Compartilhada em Condomínio, seção 3. Agendamento e tempo má |
| R15 | 1.00 | 0.80 | 1.00/1.00 | ok | Manual Operacional ChargeGrid / EV ChargeOps — 6. Classificação e escalonamento de alarmes (p. 1) | Após um alarme de falha de aterramento, somente um técnico de campo habilitado pode religar o equipamento, após a realização de uma inspeção presencial. Fonte: Manual Operacional ChargeGrid / EV ChargeOps, seção 6. Class |
| R16 | 1.00 | 0.91 | 1.00/1.00 | ok | Manual Operacional ChargeGrid / EV ChargeOps — 4. Estratégia de Load Balancing (p. 1) | Sim, ao redistribuir a potência entre carregadores ativos no Load Balancing, deve-se respeitar o mínimo de 4,2 kW por carregador ativo, que é o mínimo do registrador Maximum Charging Power. Fonte: Manual Operacional Char |
| R17 | 1.00 | 0.92 | 1.00/1.00 | ok | FAQ de Carregamento — eletropostos GoodWe ChargeGrid — 1. Quanto tempo leva uma recarga completa? (p. 1) | Recarregar 44 kWh num carregador de 11 kW leva cerca de 4 horas. Fonte: FAQ de Carregamento — eletropostos GoodWe ChargeGrid, seção 1. Quanto tempo leva uma recarga completa? |
| R18 | 1.00 | 0.85 | 1.00/1.00 | ok | Manual de Produto — EV Charger GoodWe HCA G2 — 1. Modelos da linha HCA G2 (p. 1) | O modelo GW30K-HCA-20 não existe na linha HCA G2. Os únicos modelos disponíveis são o GW7K-HCA-20 (7 kW), GW11K-HCA-20 (11 kW) e GW22K-HCA-20 (22 kW). Fonte: Manual de Produto — EV Charger GoodWe HCA G2, seção 1. Modelos |
| X01 | — | — | —/— | — | — | A informação sobre o prazo de garantia do carregador GW22K-HCA-20 não consta na base de conhecimento disponível. |
| X02 | — | — | —/— | — | — | A informação sobre o preço do kWh da concessionária Enel em São Paulo não consta na base de conhecimento. |
| X03 | — | — | —/— | — | — | Pedido fora do domínio ChargeGrid/GoodWe (assunto bloqueado por escopo). Posso ajudar com orquestração de potência, faturamento ou diagnóstico de carregadores GoodWe. |
