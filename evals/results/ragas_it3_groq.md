# RAGAS — it3 (groq: `qwen/qwen3.8-27b`)

Tabelas linha a linha + busca híbrida (vetorial + BM25) + limiar 0,69, k=5, prompt RAG v3

Gerado em 2026-10-17T15:26:08 · config: `{"chunking": "por_secao_tabelas", "k": 5, "prompt_rag": "v3", "busca": "hibrida", "limiar": 0.69, "temperature": 0.0, "top_p": 0.9, "max_tokens": 800, "embeddings": "fastembed/nomic-embed-text"}`

| Métrica | Valor |
|---|---|
| faithfulness_ragas | 0.897 |
| answer_relevancy_ragas | 0.824 |
| faithfulness_rubrica | 1.0 |
| answer_relevancy_rubrica | 0.944 |
| hit_documento_pct | 100.0 |
| citacao_presente_pct | 100.0 |
| citacao_correta_pct | 100.0 |
| acerto_factual_pct | 100.0 |
| recusa_indevida_pct | 0.0 |
| recusa_correta_pct | 100.0 |
| latencia_media_s | 29.244 |
| tokens_medios | 960.333 |
| erros | [] |

| Caso | faithfulness (RAGAS) | answer_relevancy (RAGAS) | rubrica F/AR | acerto | citação | resposta |
|---|---|---|---|---|---|---|
| R01 | 0.80 | 0.76 | 1.00/1.00 | ok | Tabelas Tarifárias — ChargeGrid Intelligence 2026 — 1. Postos tarifários (horário local, todos os dias) (p. 1) | O faturamento do ciclo do carregador C11 (18:30 às 19:00, 5 kWh) é de R$ 8,25. O ciclo ocorreu integralmente no posto tarifário de Ponta (18:00 às 20:59), cuja tarifa é de R$ 1,65/kWh. Cálculo: 5 kWh × R$ 1,65 = R$ 8,25. |
| R02 | 0.80 | 0.81 | 1.00/1.00 | ok | Tabelas Tarifárias — ChargeGrid Intelligence 2026 — 3. Tarifa de frota (p. 1) | Aplica-se a tarifa de frota fixa de R$ 0,70/kWh, pois o ID do veículo (FROTA-07) inicia com "FROTA-", regra que se sobrepõe à tabela de postos tarifários. O cálculo do faturamento é: 20 kWh × R$ 0,70/kWh = R$ 14,00. Font |
| R03 | 0.60 | 0.75 | 1.00/1.00 | ok | FAQ de Carregamento — eletropostos GoodWe ChargeGrid — 5. Posso deixar o carro conectado depois que a carga terminar? (p. 1), Tabelas Tarifárias — ChargeGrid Intelligence 2026 — 6. Tarifa de ocupação ociosa (p. 1) | Sim, há cobrança. A tolerância no eletroposto comercial é de 15 minutos após o fim da carga (14:00 + 15 min = 14:15). O veículo foi retirado às 14:45, resultando em 30 minutos de ocupação ociosa (14:45 - 14:15). A tarifa |
| R04 | 1.00 | 0.76 | 1.00/1.00 | ok | Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 2. Códigos de exceção Modbus (p. 1) | O código de exceção Modbus 0x0002 significa Illegal Data Address, indicando que o endereço de registrador solicitado é inválido ou está fora do mapa suportado pelo modelo HCA G2. A ação imediata recomendada é conferir o  |
| R05 | 1.00 | 0.75 | 1.00/1.00 | ok | Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 3. Códigos de falha do carregador (registradores 10001 a 10008) (p. 1), Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 5. Checklist de diagnóstico físico (RS485) (p. 2) | A falha de aterramento (grounding fault) do HCA G2 aparece no registrador 10002 (AC Fault Bytes 02), bit1. A conduta indicada é: interromper a operação e acionar um eletricista ou técnico habilitado antes de religar, poi |
| R06 | 1.00 | 0.91 | 1.00/1.00 | ok | Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 1. Formato de comunicação serial (RS485) (p. 1) | Os parâmetros de comunicação serial RS485 do carregador GoodWe HCA G2 são: Baud rate 9600, Bits de dados 8, Bits de parada 1 e Paridade N (nenhuma). Fonte: Mapa Modbus RTU/RS485 — GoodWe HCA G2, seção 1. Formato de comun |
| R07 | 1.00 | 0.81 | 1.00/1.00 | ok | Interoperabilidade OCPP — camada de tradução do ChargeGrid — 1. Mapeamento de conceitos OCPP para registradores Modbus (p. 1), Interoperabilidade OCPP — camada de tradução do ChargeGrid — 2. Ciclo de sessão e cálculo do consumo (p. 1), Interoperabilidade OCPP — camada de tradução do ChargeGrid — 1. Mapeamento de conceitos OCPP para registradores Modbus (p. 1) | A mensagem StopTransaction do OCPP registra o meterStop (leitura do medidor após a carga) e o motivo do encerramento. No mapeamento para o HCA G2, isso corresponde ao registrador Modbus 10172 (Meter Reading After Chargin |
| R08 | 0.40 | 0.78 | 1.00/1.00 | ok | Interoperabilidade OCPP — camada de tradução do ChargeGrid — 2. Ciclo de sessão e cálculo do consumo (p. 1) | O consumo do ciclo foi de 27,50 kWh. Como os registradores 10170 e 10172 do HCA G2 são expressos em 0,01 kWh, a diferença bruta entre meterStop (207250) e meterStart (204500) é de 2750 unidades. Dividindo por 100, obtém- |
| R09 | 1.00 | 0.85 | 1.00/1.00 | ok | Manual de Produto — EV Charger GoodWe HCA G2 — 1. Modelos da linha HCA G2 (p. 1) | A linha GoodWe HCA G2 possui 3 modelos: GW7K-HCA-20 (7 kW), GW11K-HCA-20 (11 kW) e GW22K-HCA-20 (22 kW). Não existem outros modelos nesta linha. Fonte: Manual de Produto — EV Charger GoodWe HCA G2, seção 1. Modelos da li |
| R10 | 0.75 | 0.85 | 1.00/1.00 | ok | Manual de Produto — EV Charger GoodWe HCA G2 — 4. Dados gerais (p. 1) | Sim, o carregador HCA G2 pode ser instalado ao ar livre. O grau de proteção é IP66 para o carregador e IP55 para o plugue de carregamento. Fonte: Manual de Produto — EV Charger GoodWe HCA G2, seção 4. Dados gerais. |
| R11 | 1.00 | 0.91 | 1.00/1.00 | ok | Interoperabilidade OCPP — camada de tradução do ChargeGrid — Introdução (p. 1), Manual de Produto — EV Charger GoodWe HCA G2 — 2. Comunicação e protocolos (p. 1) | Não, o carregador GoodWe HCA G2 não suporta OCPP nativamente. O protocolo de comunicação declarado no datasheet e no manual é Modbus TCP (backend) e Modbus RTU/RS485 (local, para inversor e medidor MID). O OCPP é tratado |
| R12 | 1.00 | 0.82 | 1.00/1.00 | ok | Regimento de Recarga Compartilhada em Condomínio — 4. Liberação da vaga após a recarga (p. 1) | O morador precisa retirar o veículo da vaga em até 30 minutos após o encerramento da carga (status carga completa). Fonte: Regimento de Recarga Compartilhada em Condomínio, seção 4. Liberação da vaga após a recarga. |
| R13 | 1.00 | 0.81 | 1.00/1.00 | ok | Regimento de Recarga Compartilhada em Condomínio — 7. Penalidades (p. 1) | A segunda ocorrência de ocupação indevida da vaga no mesmo semestre gera multa de 10% da taxa condominial. Fonte: Regimento de Recarga Compartilhada em Condomínio, seção 7. Penalidades. |
| R14 | 1.00 | 0.81 | 1.00/1.00 | ok | Regimento de Recarga Compartilhada em Condomínio — 3. Agendamento e tempo máximo de uso (p. 1) | Cada unidade pode reservar o carregador compartilhado por um tempo máximo de 4 horas por dia, com antecedência de até 48 horas. Fonte: Regimento de Recarga Compartilhada em Condomínio, seção 3. Agendamento e tempo máximo |
| R15 | 0.80 | 0.88 | 1.00/1.00 | ok | Manual Operacional ChargeGrid / EV ChargeOps — 6. Classificação e escalonamento de alarmes (p. 1) | Somente um técnico de campo habilitado pode religar o carregador após um alarme de falha de aterramento, e isso deve ocorrer após inspeção presencial. A operação do equipamento deve ser interrompida imediatamente e não d |
| R16 | 1.00 | 0.91 | 1.00/1.00 | ok | Manual Operacional ChargeGrid / EV ChargeOps — 4. Estratégia de Load Balancing (p. 1) | Sim, existe uma potência mínima de 4,2 kW por carregador ativo durante a redistribuição de potência no Load Balancing. Fonte: Manual Operacional ChargeGrid / EV ChargeOps, seção 4. Estratégia de Load Balancing. |
| R17 | 1.00 | 0.83 | 1.00/1.00 | ok | FAQ de Carregamento — eletropostos GoodWe ChargeGrid — 1. Quanto tempo leva uma recarga completa? (p. 1) | Aproximadamente 4 horas. O tempo é calculado dividindo a energia a recarregar (44 kWh) pela potência efetiva do carregador (11 kW). Fonte: FAQ de Carregamento — eletropostos GoodWe ChargeGrid, seção 1. Quanto tempo leva  |
| R18 | 1.00 | 0.85 | 1.00/0.00 | ok | Manual de Produto — EV Charger GoodWe HCA G2 — 1. Modelos da linha HCA G2 (p. 1) | O modelo GW30K-HCA-20 não existe na linha HCA G2. A base de conhecimento lista apenas três modelos: GW7K-HCA-20 (7 kW), GW11K-HCA-20 (11 kW) e GW22K-HCA-20 (22 kW). Fonte: Manual de Produto — EV Charger GoodWe HCA G2, se |
| X01 | — | — | —/— | — | — | A informação sobre o prazo de garantia do carregador GW22K-HCA-20 não consta na base de conhecimento recuperada. Fonte: Nenhum documento disponível. |
| X02 | — | — | —/— | — | — | A informação sobre o preço do kWh da concessionária Enel em São Paulo não consta na base de conhecimento recuperada. Para fins de faturamento e auditoria, utilize a tarifa vigente informada pelo operador ou registrada no |
| X03 | — | — | —/— | — | — | Pedido fora do domínio ChargeGrid/GoodWe (assunto bloqueado por escopo). Posso ajudar com orquestração de potência, faturamento ou diagnóstico de carregadores GoodWe. |
