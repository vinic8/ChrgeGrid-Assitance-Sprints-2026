# RAGAS — it6 (ollama: `gemma4:cloud`)

it5 sem a porta de relevância + base sem os 2 trechos escritos sob medida para o eval set

Gerado em 2026-10-17T16:51:48 · config: `{"chunking": "por_secao_tabelas", "k": 6, "prompt_rag": "v4", "busca": "hibrida_expandida", "limiar": 0.0, "temperature": 0.0, "top_p": 0.9, "max_tokens": 800, "embeddings": "fastembed/nomic-embed-text"}`

| Métrica | Valor |
|---|---|
| faithfulness_ragas | 0.895 |
| answer_relevancy_ragas | 0.777 |
| faithfulness_rubrica | 1.0 |
| answer_relevancy_rubrica | 0.944 |
| hit_documento_pct | 100.0 |
| citacao_presente_pct | 100.0 |
| citacao_correta_pct | 100.0 |
| acerto_factual_pct | 100.0 |
| recusa_indevida_pct | 5.6 |
| recusa_correta_pct | 100.0 |
| latencia_media_s | 1.452 |
| tokens_medios | 1203.619 |
| erros | [] |

| Caso | faithfulness (RAGAS) | answer_relevancy (RAGAS) | rubrica F/AR | acerto | citação | resposta |
|---|---|---|---|---|---|---|
| R01 | 0.40 | 0.70 | 1.00/1.00 | ok | Tabelas Tarifárias — ChargeGrid Intelligence 2026 — 1. Postos tarifários (horário local, todos os dias) (p. 1) | O faturamento da recarga no carregador C11 é de R$ 8,25. O ciclo ocorreu integralmente no posto 'Ponta' (18:00 às 20:59), com tarifa de R$ 1,65/kWh. Cálculo: 5 kWh × R$ 1,65 = R$ 8,25. Fonte: Tabelas Tarifárias — ChargeG |
| R02 | 0.75 | 0.84 | 1.00/1.00 | ok | Tabelas Tarifárias — ChargeGrid Intelligence 2026 — 3. Tarifa de frota (p. 1) | Para o veículo FROTA-07, deve-se aplicar a tarifa fixa preferencial de frota de R$ 0,70/kWh, que se sobrepõe à tabela de postos tarifários. O valor a cobrar é 20 kWh × R$ 0,70 = R$ 14,00. Fonte: Tabelas Tarifárias — Char |
| R03 | 0.50 | 0.80 | 1.00/1.00 | ok | Tabelas Tarifárias — ChargeGrid Intelligence 2026 — 6. Tarifa de ocupação ociosa (p. 1) | Sim, existe cobrança. No eletroposto comercial, há 15 minutos de tolerância após o fim da carga. Como o veículo permaneceu por 45 minutos (das 14:00 às 14:45), houve 30 minutos de ocupação ociosa. O cálculo é: 30 minutos |
| R04 | 0.80 | 0.77 | 1.00/1.00 | ok | Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 2. Códigos de exceção Modbus (p. 1) | O código de exceção Modbus 0x0002 significa 'Illegal Data Address', indicando que o endereço de registrador solicitado é inválido ou está fora do mapa suportado por este modelo. A ação imediata é conferir o endereço cont |
| R05 | 1.00 | 0.82 | 1.00/1.00 | ok | Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 3. Códigos de falha do carregador (registradores 10001 a 10008) (p. 1), Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 5. Checklist de diagnóstico físico (RS485) (p. 2) | A falha de aterramento (grounding fault) do HCA G2 aparece no registrador 10002, bit1. A conduta técnica é interromper a operação e acionar um eletricista ou técnico habilitado antes de religar o equipamento, pois não é  |
| R06 | 1.00 | 0.93 | 1.00/1.00 | ok | Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 1. Formato de comunicação serial (RS485) (p. 1) | Os parâmetros de comunicação serial RS485 do carregador HCA G2 são:  / Parâmetro / Valor / / :--- / :--- / / Baud rate / 9600 / / Bits de dados / 8 / / Bits de parada / 1 / / Paridade / N (nenhuma) /  Fonte: Mapa Modbus  |
| R07 | 1.00 | 0.85 | 1.00/1.00 | ok | Interoperabilidade OCPP — camada de tradução do ChargeGrid — 2. Ciclo de sessão e cálculo do consumo (p. 1) | A mensagem StopTransaction do OCPP registra o meterStop (leitura do medidor após a carga) e o motivo do encerramento da sessão. Para o faturamento, o consumo é calculado subtraindo o meterStart (leitura inicial) do meter |
| R08 | 0.67 | 0.65 | 1.00/1.00 | ok | Interoperabilidade OCPP — camada de tradução do ChargeGrid — 2. Ciclo de sessão e cálculo do consumo (p. 1) | O consumo do ciclo foi de 27,50 kWh. O cálculo é realizado subtraindo o meterStart do meterStop (207250 - 204500 = 2750 unidades) e dividindo o resultado por 100, conforme a especificação de que os registradores são expr |
| R09 | 1.00 | 0.83 | 1.00/1.00 | ok | Manual de Produto — EV Charger GoodWe HCA G2 — 1. Modelos da linha HCA G2 (p. 1) | A linha HCA G2 possui 3 modelos: o GW7K-HCA-20 com potência nominal de 7 kW, o GW11K-HCA-20 com potência nominal de 11 kW e o GW22K-HCA-20 com potência nominal de 22 kW. Fonte: Manual de Produto — EV Charger GoodWe HCA G |
| R10 | 1.00 | 0.85 | 1.00/1.00 | ok | FAQ de Carregamento — eletropostos GoodWe ChargeGrid — 6. A recarga é segura na chuva? (p. 1), Manual de Produto — EV Charger GoodWe HCA G2 — 4. Dados gerais (p. 1) | O carregador HCA G2 pode ser instalado ao ar livre (ambiente externo), possuindo grau de proteção IP66 para o carregador e IP55 para o plugue de carregamento. |
| R11 | 1.00 | 0.91 | 1.00/1.00 | ok | Interoperabilidade OCPP — camada de tradução do ChargeGrid — Introdução (p. 1), Manual de Produto — EV Charger GoodWe HCA G2 — 2. Comunicação e protocolos (p. 1) | O carregador GoodWe HCA G2 não suporta OCPP nativamente; o protocolo declarado é Modbus TCP (backend) e Modbus RTU/RS485 (local). O ChargeGrid atua como uma camada de tradução e interoperabilidade que expõe os dados do M |
| R12 | 1.00 | 0.76 | 1.00/1.00 | ok | Regimento de Recarga Compartilhada em Condomínio — 4. Liberação da vaga após a recarga (p. 1), FAQ de Carregamento — eletropostos GoodWe ChargeGrid — 5. Posso deixar o carro conectado depois que a carga terminar? (p. 1) | No condomínio, o veículo deve ser retirado da vaga em até 30 minutos após a recarga terminar (status carga completa). Fonte: Regimento de Recarga Compartilhada em Condomínio, seção 4. Liberação da vaga após a recarga. |
| R13 | 1.00 | 0.81 | 1.00/1.00 | ok | Regimento de Recarga Compartilhada em Condomínio — 7. Penalidades (p. 1) | A ocupação indevida da vaga de recarga do condomínio pela segunda vez no mesmo semestre gera multa de 10% da taxa condominial. Fonte: Regimento de Recarga Compartilhada em Condomínio, seção 7. Penalidades. |
| R14 | 1.00 | 0.84 | 1.00/1.00 | ok | Regimento de Recarga Compartilhada em Condomínio — 3. Agendamento e tempo máximo de uso (p. 1) | Cada reserva de carregador compartilhado do condomínio tem duração máxima de 4 horas por dia por unidade, podendo ser realizada com até 48 horas de antecedência. Fonte: Regimento de Recarga Compartilhada em Condomínio, s |
| R15 | 1.00 | 0.79 | 1.00/1.00 | ok | Manual Operacional ChargeGrid / EV ChargeOps — 6. Classificação e escalonamento de alarmes (p. 1) | Após um alarme de falha de aterramento, a operação do carregador deve ser interrompida imediatamente e somente um técnico de campo habilitado pode religar o equipamento, após a realização de uma inspeção presencial. Font |
| R16 | 1.00 | 0.90 | 1.00/1.00 | ok | Manual Operacional ChargeGrid / EV ChargeOps — 4. Estratégia de Load Balancing (p. 1) | Sim, ao redistribuir a potência entre carregadores ativos no Load Balancing, deve-se respeitar o mínimo de 4,2 kW por carregador ativo, que é o mínimo do registrador Maximum Charging Power. Fonte: Manual Operacional Char |
| R17 | 1.00 | 0.92 | 1.00/1.00 | ok | FAQ de Carregamento — eletropostos GoodWe ChargeGrid — 1. Quanto tempo leva uma recarga completa? (p. 1) | Recarregar 44 kWh num carregador de 11 kW leva aproximadamente 4 horas (44 kWh / 11 kW = 4h). Fonte: FAQ de Carregamento — eletropostos GoodWe ChargeGrid, seção 1. Quanto tempo leva uma recarga completa? |
| R18 | 1.00 | 0.00 | 1.00/0.00 | ok | Manual de Produto — EV Charger GoodWe HCA G2 — 1. Modelos da linha HCA G2 (p. 1) | A informação sobre o modelo GW30K-HCA-20 não consta na base de conhecimento. A linha HCA G2 possui apenas três modelos: GW7K-HCA-20 (7 kW), GW11K-HCA-20 (11 kW) e GW22K-HCA-20 (22 kW). Fonte: Manual de Produto — EV Charg |
| X01 | — | — | —/— | — | — | A informação sobre o prazo de garantia do carregador GW22K-HCA-20 não consta na base de conhecimento. |
| X02 | — | — | —/— | — | — | A informação sobre o preço do kWh da concessionária Enel em São Paulo não consta na base de conhecimento disponível. |
| X03 | — | — | —/— | — | — | Pedido fora do domínio ChargeGrid/GoodWe (assunto bloqueado por escopo). Posso ajudar com orquestração de potência, faturamento ou diagnóstico de carregadores GoodWe. |
