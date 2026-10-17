# RAGAS — it3 (ollama: `gemma4:cloud`)

Tabelas linha a linha + busca híbrida (vetorial + BM25) + limiar 0,69, k=5, prompt RAG v3

Gerado em 2026-10-17T15:12:34 · config: `{"chunking": "por_secao_tabelas", "k": 5, "prompt_rag": "v3", "busca": "hibrida", "limiar": 0.69, "temperature": 0.0, "top_p": 0.9, "max_tokens": 800, "embeddings": "fastembed/nomic-embed-text"}`

| Métrica | Valor |
|---|---|
| faithfulness_ragas | 0.887 |
| answer_relevancy_ragas | 0.785 |
| faithfulness_rubrica | 1.0 |
| answer_relevancy_rubrica | 1.0 |
| hit_documento_pct | 100.0 |
| citacao_presente_pct | 100.0 |
| citacao_correta_pct | 100.0 |
| acerto_factual_pct | 100.0 |
| recusa_indevida_pct | 0.0 |
| recusa_correta_pct | 100.0 |
| latencia_media_s | 1.73 |
| tokens_medios | 946.762 |
| erros | [] |

| Caso | faithfulness (RAGAS) | answer_relevancy (RAGAS) | rubrica F/AR | acerto | citação | resposta |
|---|---|---|---|---|---|---|
| R01 | 0.40 | 0.62 | 1.00/1.00 | ok | Tabelas Tarifárias — ChargeGrid Intelligence 2026 — 1. Postos tarifários (horário local, todos os dias) (p. 1) | O faturamento é de R$ 8,25. O ciclo ocorreu integralmente no posto 'Ponta' (18:00 às 20:59), com tarifa de R$ 1,65/kWh. Cálculo: 5 kWh × R$ 1,65 = R$ 8,25. Fonte: Tabelas Tarifárias — ChargeGrid Intelligence 2026, seção  |
| R02 | 0.67 | 0.85 | 1.00/1.00 | ok | Tabelas Tarifárias — ChargeGrid Intelligence 2026 — 3. Tarifa de frota (p. 1) | A tarifa a aplicar é a de frota (R$ 0,70/kWh), pois o ID do veículo começa com "FROTA-", regra que se sobrepõe à tabela de postos tarifários. O valor a cobrar é R$ 14,00 (20 kWh × R$ 0,70). Fonte: Tabelas Tarifárias — Ch |
| R03 | 0.50 | 0.80 | 1.00/1.00 | ok | FAQ de Carregamento — eletropostos GoodWe ChargeGrid — 5. Posso deixar o carro conectado depois que a carga terminar? (p. 1), Tabelas Tarifárias — ChargeGrid Intelligence 2026 — 6. Tarifa de ocupação ociosa (p. 1) | Sim, existe cobrança. No eletroposto comercial, há 15 minutos de tolerância após o fim da carga. O veículo permaneceu 45 minutos (das 14:00 às 14:45), resultando em 30 minutos de ocupação ociosa. O cálculo é: 30 min × R$ |
| R04 | 0.80 | 0.73 | 1.00/1.00 | ok | Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 2. Códigos de exceção Modbus (p. 1) | O código 0x0002 significa 'Illegal Data Address', indicando que o endereço do registrador solicitado é inválido ou está fora do mapa suportado por este modelo. A ação imediata é conferir o endereço contra o mapa do HCA G |
| R05 | 1.00 | 0.81 | 1.00/1.00 | ok | Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 3. Códigos de falha do carregador (registradores 10001 a 10008) (p. 1), Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 5. Checklist de diagnóstico físico (RS485) (p. 2) | A falha de aterramento (grounding fault) aparece no registrador 10002, bit1. A conduta técnica é interromper a operação e acionar um eletricista ou técnico habilitado antes de religar o equipamento, pois não é uma falha  |
| R06 | 1.00 | 0.93 | 1.00/1.00 | ok | Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 1. Formato de comunicação serial (RS485) (p. 1) | Os parâmetros de comunicação serial RS485 do carregador HCA G2 são:  / Parâmetro / Valor / / :--- / :--- / / Baud rate / 9600 / / Bits de dados / 8 / / Bits de parada / 1 / / Paridade / N (nenhuma) /  Fonte: Mapa Modbus  |
| R07 | 1.00 | 0.83 | 1.00/1.00 | ok | Interoperabilidade OCPP — camada de tradução do ChargeGrid — 1. Mapeamento de conceitos OCPP para registradores Modbus (p. 1), Interoperabilidade OCPP — camada de tradução do ChargeGrid — 2. Ciclo de sessão e cálculo do consumo (p. 1), Interoperabilidade OCPP — camada de tradução do ChargeGrid — 1. Mapeamento de conceitos OCPP para registradores Modbus (p. 1) | A mensagem StopTransaction do OCPP registra o meterStop (leitura do medidor após a carga) e o motivo do encerramento (StopTransaction.reason), que no hardware GoodWe HCA G2 correspondem aos registradores Modbus 10172 e 1 |
| R08 | 0.60 | 0.76 | 1.00/1.00 | ok | Interoperabilidade OCPP — camada de tradução do ChargeGrid — 2. Ciclo de sessão e cálculo do consumo (p. 1) | O consumo foi de 27,50 kWh. O cálculo é realizado subtraindo o meterStart do meterStop (207250 - 204500 = 2750 unidades) e dividindo o resultado por 100, conforme a especificação dos registradores do HCA G2. Fonte: Inter |
| R09 | 1.00 | 0.83 | 1.00/1.00 | ok | Manual de Produto — EV Charger GoodWe HCA G2 — 1. Modelos da linha HCA G2 (p. 1) | A linha HCA G2 possui três modelos: / Modelo / Potência nominal / / GW7K-HCA-20 / 7 kW / / GW11K-HCA-20 / 11 kW / / GW22K-HCA-20 / 22 kW /  Fonte: Manual de Produto — EV Charger GoodWe HCA G2, seção 1. Modelos da linha H |
| R10 | 1.00 | 0.78 | 1.00/1.00 | ok | Manual de Produto — EV Charger GoodWe HCA G2 — 4. Dados gerais (p. 1) | Sim, o carregador HCA G2 pode ser instalado em exterior. O grau de proteção é IP66 para o carregador e IP55 para o plugue de carregamento. Fonte: Manual de Produto — EV Charger GoodWe HCA G2, seção 4. Dados gerais. |
| R11 | 1.00 | 0.93 | 1.00/1.00 | ok | Interoperabilidade OCPP — camada de tradução do ChargeGrid — Introdução (p. 1), Manual de Produto — EV Charger GoodWe HCA G2 — 2. Comunicação e protocolos (p. 1) | Não, o carregador GoodWe HCA G2 não suporta OCPP nativamente. O protocolo declarado é Modbus TCP (backend) e Modbus RTU/RS485 (local), sendo o OCPP implementado apenas como uma camada de tradução e interoperabilidade via |
| R12 | 1.00 | 0.75 | 1.00/1.00 | ok | Regimento de Recarga Compartilhada em Condomínio — 4. Liberação da vaga após a recarga (p. 1) | O veículo deve ser retirado da vaga em até 30 minutos após o encerramento da carga (status carga completa). Fonte: Regimento de Recarga Compartilhada em Condomínio, seção 4. Liberação da vaga após a recarga. |
| R13 | 1.00 | 0.81 | 1.00/1.00 | ok | Regimento de Recarga Compartilhada em Condomínio — 7. Penalidades (p. 1) | A segunda ocorrência de ocupação indevida da vaga no mesmo semestre gera multa de 10% da taxa condominial. Fonte: Regimento de Recarga Compartilhada em Condomínio, seção 7. Penalidades. |
| R14 | 1.00 | 0.80 | 1.00/1.00 | ok | Regimento de Recarga Compartilhada em Condomínio — 3. Agendamento e tempo máximo de uso (p. 1) | Cada reserva tem duração máxima de 4 horas por dia por unidade, podendo ser realizada com até 48 horas de antecedência. Fonte: Regimento de Recarga Compartilhada em Condomínio, seção 3. Agendamento e tempo máximo de uso. |
| R15 | 1.00 | 0.67 | 1.00/1.00 | ok | Manual Operacional ChargeGrid / EV ChargeOps — 6. Classificação e escalonamento de alarmes (p. 1) | Somente um técnico de campo habilitado pode religar o equipamento após inspeção presencial, pois a falha de aterramento é classificada como Nível 3 (segurança elétrica), exigindo a interrupção imediata da operação. Fonte |
| R16 | 1.00 | 0.75 | 1.00/1.00 | ok | Manual Operacional ChargeGrid / EV ChargeOps — 4. Estratégia de Load Balancing (p. 1) | Sim, existe uma potência mínima de 4,2 kW por carregador ativo, que corresponde ao mínimo do registrador Maximum Charging Power.  Fonte: Manual Operacional ChargeGrid / EV ChargeOps, seção 4. Estratégia de Load Balancing |
| R17 | 1.00 | 0.63 | 1.00/1.00 | ok | FAQ de Carregamento — eletropostos GoodWe ChargeGrid — 1. Quanto tempo leva uma recarga completa? (p. 1) | Leva cerca de 4 horas. O cálculo é baseado na energia a recarregar dividida pela potência efetiva (44 kWh / 11 kW). Fonte: FAQ de Carregamento — eletropostos GoodWe ChargeGrid, seção 1. Quanto tempo leva uma recarga comp |
| R18 | 1.00 | 0.85 | 1.00/1.00 | ok | Manual de Produto — EV Charger GoodWe HCA G2 — 1. Modelos da linha HCA G2 (p. 1) | O modelo GW30K-HCA-20 não existe na linha HCA G2. Os únicos modelos disponíveis são o GW7K-HCA-20 (7 kW), GW11K-HCA-20 (11 kW) e GW22K-HCA-20 (22 kW). Fonte: Manual de Produto — EV Charger GoodWe HCA G2, seção 1. Modelos |
| X01 | — | — | —/— | — | — | A informação sobre o prazo de garantia do carregador GW22K-HCA-20 não consta na base de conhecimento disponível. |
| X02 | — | — | —/— | — | — | A informação sobre o preço do kWh da concessionária Enel em São Paulo não consta na base de conhecimento. |
| X03 | — | — | —/— | — | — | Pedido fora do domínio ChargeGrid/GoodWe (assunto bloqueado por escopo). Posso ajudar com orquestração de potência, faturamento ou diagnóstico de carregadores GoodWe. |
