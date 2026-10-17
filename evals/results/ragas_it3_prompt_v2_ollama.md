# RAGAS — it3_prompt_v2 (ollama: `gemma4:cloud`)

Ablação: recuperação da it3 (tabelas + híbrida + limiar) com o prompt RAG v2

Gerado em 2026-10-17T15:48:39 · config: `{"chunking": "por_secao_tabelas", "k": 5, "prompt_rag": "v2", "busca": "hibrida", "limiar": 0.69, "temperature": 0.0, "top_p": 0.9, "max_tokens": 800, "embeddings": "fastembed/nomic-embed-text"}`

| Métrica | Valor |
|---|---|
| faithfulness_ragas | 0.892 |
| answer_relevancy_ragas | 0.806 |
| faithfulness_rubrica | 1.0 |
| answer_relevancy_rubrica | 1.0 |
| hit_documento_pct | 100.0 |
| citacao_presente_pct | 100.0 |
| citacao_correta_pct | 100.0 |
| acerto_factual_pct | 100.0 |
| recusa_indevida_pct | 0.0 |
| recusa_correta_pct | 100.0 |
| latencia_media_s | 2.123 |
| tokens_medios | 955.238 |
| erros | [] |

| Caso | faithfulness (RAGAS) | answer_relevancy (RAGAS) | rubrica F/AR | acerto | citação | resposta |
|---|---|---|---|---|---|---|
| R01 | 0.71 | 0.70 | 1.00/1.00 | ok | Tabelas Tarifárias — ChargeGrid Intelligence 2026 — 1. Postos tarifários (horário local, todos os dias) (p. 1) | Ciclo registrado para o carregador C11. O período de recarga (18:30 às 19:00) enquadra-se integralmente no posto tarifário 'Ponta' (18:00 às 20:59), com tarifa de R$ 1,65/kWh. Cálculo: 5 kWh × R$ 1,65 = R$ 8,25. Fonte: T |
| R02 | 0.75 | 0.82 | 1.00/1.00 | ok | Tabelas Tarifárias — ChargeGrid Intelligence 2026 — 3. Tarifa de frota (p. 1) | Para o veículo FROTA-07, aplica-se a tarifa fixa preferencial de frota de R$ 0,70/kWh, que se sobrepõe à tabela de postos tarifários (mesmo em horário de ponta). Cálculo: 20 kWh × R$ 0,70 = R$ 14,00. Fonte: Tabelas Tarif |
| R03 | 0.50 | 0.79 | 1.00/1.00 | ok | FAQ de Carregamento — eletropostos GoodWe ChargeGrid — 5. Posso deixar o carro conectado depois que a carga terminar? (p. 1), Tabelas Tarifárias — ChargeGrid Intelligence 2026 — 6. Tarifa de ocupação ociosa (p. 1) | Sim, existe cobrança. No eletroposto comercial, há 15 minutos de tolerância após o fim da carga. O veículo permaneceu 45 minutos (das 14:00 às 14:45), resultando em 30 minutos de ocupação ociosa. O cálculo é: 30 min × R$ |
| R04 | 1.00 | 0.74 | 1.00/1.00 | ok | Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 2. Códigos de exceção Modbus (p. 1) | O código de exceção Modbus 0x0002 (Illegal Data Address) indica que o endereço do registrador solicitado é inválido ou está fora do mapa suportado pelo modelo HCA G2. A ação imediata é conferir o endereço solicitado cont |
| R05 | 1.00 | 0.80 | 1.00/1.00 | ok | Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 3. Códigos de falha do carregador (registradores 10001 a 10008) (p. 1), Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 5. Checklist de diagnóstico físico (RS485) (p. 2) | A falha de aterramento (grounding fault) do GoodWe HCA G2 é indicada no registrador 10002, bit1. A conduta obrigatória é interromper a operação e acionar um eletricista ou técnico habilitado antes de religar o equipament |
| R06 | 1.00 | 0.91 | 1.00/1.00 | ok | Mapa Modbus RTU/RS485 — GoodWe HCA G2 — 1. Formato de comunicação serial (RS485) (p. 1) | Os parâmetros de comunicação serial RS485 para o carregador GoodWe HCA G2 são: Baud rate de 9600, 8 bits de dados, 1 bit de parada e paridade N (nenhuma). Fonte: Mapa Modbus RTU/RS485 — GoodWe HCA G2, seção 1. Formato de |
| R07 | 1.00 | 0.79 | 1.00/1.00 | ok | Interoperabilidade OCPP — camada de tradução do ChargeGrid — 1. Mapeamento de conceitos OCPP para registradores Modbus (p. 1), Interoperabilidade OCPP — camada de tradução do ChargeGrid — 2. Ciclo de sessão e cálculo do consumo (p. 1), Interoperabilidade OCPP — camada de tradução do ChargeGrid — 1. Mapeamento de conceitos OCPP para registradores Modbus (p. 1) | A mensagem StopTransaction do OCPP registra o fim do ciclo de recarga, capturando o meterStop (leitura do medidor após a carga) e o motivo do encerramento (StopTransaction.reason). No hardware GoodWe HCA G2, isso corresp |
| R08 | 0.83 | 0.76 | 1.00/1.00 | ok | Interoperabilidade OCPP — camada de tradução do ChargeGrid — 2. Ciclo de sessão e cálculo do consumo (p. 1) | O consumo é calculado pela diferença entre meterStop (207250) e meterStart (204500), resultando em 2750 unidades. Como os registradores do GoodWe HCA G2 são expressos em 0,01 kWh, a diferença bruta é dividida por 100, to |
| R09 | 1.00 | 0.83 | 1.00/1.00 | ok | Manual de Produto — EV Charger GoodWe HCA G2 — 1. Modelos da linha HCA G2 (p. 1) | A linha HCA G2 possui três modelos com as seguintes potências nominais: - GW7K-HCA-20: 7 kW (Monofásico) - GW11K-HCA-20: 11 kW (Trifásico) - GW22K-HCA-20: 22 kW (Trifásico)  Fonte: Manual de Produto — EV Charger GoodWe H |
| R10 | 0.75 | 0.79 | 1.00/1.00 | ok | Manual de Produto — EV Charger GoodWe HCA G2 — 4. Dados gerais (p. 1) | Sim, o carregador GoodWe HCA G2 pode ser instalado em ambiente exterior. O grau de proteção é IP66 para o carregador e IP55 para o plugue de carregamento. Fonte: Manual de Produto — EV Charger GoodWe HCA G2, seção 4. Dad |
| R11 | 1.00 | 0.91 | 1.00/1.00 | ok | Interoperabilidade OCPP — camada de tradução do ChargeGrid — Introdução (p. 1), Manual de Produto — EV Charger GoodWe HCA G2 — 2. Comunicação e protocolos (p. 1) | Não. O carregador GoodWe HCA G2 não suporta OCPP nativamente; o protocolo declarado é Modbus TCP (backend) e Modbus RTU/RS485 (local). O ChargeGrid atua como uma camada de tradução e interoperabilidade que expõe os dados |
| R12 | 1.00 | 0.75 | 1.00/1.00 | ok | Regimento de Recarga Compartilhada em Condomínio — 4. Liberação da vaga após a recarga (p. 1) | Após o encerramento da carga (status carga completa), o veículo deve ser retirado da vaga em até 30 minutos. A permanência além deste prazo é classificada como ocupação indevida. Fonte: Regimento de Recarga Compartilhada |
| R13 | 1.00 | 0.81 | 1.00/1.00 | ok | Regimento de Recarga Compartilhada em Condomínio — 7. Penalidades (p. 1) | A ocupação indevida da vaga na segunda ocorrência dentro do mesmo semestre gera a aplicação de multa de 10% da taxa condominial. Fonte: Regimento de Recarga Compartilhada em Condomínio, seção 7. Penalidades. |
| R14 | 1.00 | 0.77 | 1.00/1.00 | ok | Regimento de Recarga Compartilhada em Condomínio — 3. Agendamento e tempo máximo de uso (p. 1) | Cada reserva de carregador compartilhado tem duração máxima de 4 horas por dia por unidade, podendo ser realizada com até 48 horas de antecedência via aplicativo. Fonte: Regimento de Recarga Compartilhada em Condomínio,  |
| R15 | 0.50 | 0.70 | 1.00/1.00 | ok | Manual Operacional ChargeGrid / EV ChargeOps — 6. Classificação e escalonamento de alarmes (p. 1) | Alarmes de falha de aterramento são classificados como Nível 3 (segurança elétrica). A operação do carregador deve ser interrompida imediatamente e somente um técnico de campo habilitado pode religar o equipamento, após  |
| R16 | 1.00 | 0.91 | 1.00/1.00 | ok | Manual Operacional ChargeGrid / EV ChargeOps — 4. Estratégia de Load Balancing (p. 1) | Sim, ao redistribuir a potência entre carregadores ativos no Load Balancing, deve-se respeitar o mínimo de 4,2 kW por carregador ativo, que é o limite do registrador Maximum Charging Power. Fonte: Manual Operacional Char |
| R17 | 1.00 | 0.91 | 1.00/1.00 | ok | FAQ de Carregamento — eletropostos GoodWe ChargeGrid — 1. Quanto tempo leva uma recarga completa? (p. 1) | Para recarregar 44 kWh em um carregador de 11 kW, o tempo aproximado é de 4 horas. Note que a potência efetiva pode ser limitada pelo carregador de bordo do veículo e pelo controle de carga dinâmico do site. Fonte: FAQ d |
| R18 | 1.00 | 0.85 | 1.00/1.00 | ok | Manual de Produto — EV Charger GoodWe HCA G2 — 1. Modelos da linha HCA G2 (p. 1) | O modelo GW30K-HCA-20 não existe na linha HCA G2. Os únicos modelos disponíveis são o GW7K-HCA-20 (7 kW), GW11K-HCA-20 (11 kW) e GW22K-HCA-20 (22 kW). Fonte: Manual de Produto — EV Charger GoodWe HCA G2, seção 1. Modelos |
| X01 | — | — | —/— | — | — | A informação sobre o prazo de garantia do modelo GW22K-HCA-20 não consta na base de conhecimento disponível. |
| X02 | — | — | —/— | — | — | A informação sobre a tarifa atual da concessionária Enel em São Paulo não consta na base de conhecimento disponível. Para prosseguir com cálculos de faturamento, por favor, informe a tarifa vigente. |
| X03 | — | — | —/— | — | — | Pedido fora do domínio ChargeGrid/GoodWe (assunto bloqueado por escopo). Posso ajudar com orquestração de potência, faturamento ou diagnóstico de carregadores GoodWe. |
