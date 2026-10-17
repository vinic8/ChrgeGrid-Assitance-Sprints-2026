# RAGAS — it1 (ollama: `gemma4:cloud`)

Baseline Sprint 04: chunk por página (1000/0), sem normalização, k=3, prompt RAG v1

Gerado em 2026-10-17T15:08:10 · config: `{"chunking": "recursivo_basico", "k": 3, "prompt_rag": "v1", "busca": "vetorial", "limiar": 0.0, "temperature": 0.0, "top_p": 0.9, "max_tokens": 800, "embeddings": "fastembed/nomic-embed-text"}`

| Métrica | Valor |
|---|---|
| faithfulness_ragas | 0.751 |
| answer_relevancy_ragas | 0.717 |
| faithfulness_rubrica | 0.875 |
| answer_relevancy_rubrica | 0.861 |
| hit_documento_pct | 94.4 |
| citacao_presente_pct | 5.6 |
| citacao_correta_pct | 0.0 |
| acerto_factual_pct | 77.8 |
| recusa_indevida_pct | 11.1 |
| recusa_correta_pct | 100.0 |
| latencia_media_s | 1.206 |
| tokens_medios | 832.905 |
| erros | [] |

| Caso | faithfulness (RAGAS) | answer_relevancy (RAGAS) | rubrica F/AR | acerto | citação | resposta |
|---|---|---|---|---|---|---|
| R01 | 0.60 | 0.70 | 1.00/1.00 | ok | — | Ciclo registrado para o carregador C11. O período de recarga (18:30 às 19:00) enquadra-se no posto tarifário de 'Ponta' (18:00 às 20:59), com tarifa de R$ 1,65/kWh. Cálculo: 5 kWh × R$ 1,65 = R$ 8,25. |
| R02 | 0.67 | 0.00 | 1.00/0.00 | FALHOU | — | Ciclo de recarga do veículo FROTA-07 registrado com consumo de 20 kWh. Conforme a política de faturamento, veículos de frota cadastrada possuem tarifa fixa. No entanto, como a tarifa específica para a frota não foi infor |
| R03 | 0.40 | 0.76 | 1.00/1.00 | FALHOU | — | Sim, existe cobrança. No eletroposto comercial, a tolerância após o fim da carga é de 15 minutos. Como o veículo permaneceu até as 14:45 (30 minutos após o término), houve a incidência da tarifa de ocupação ociosa por 15 |
| R04 | 0.50 | 0.67 | 0.00/1.00 | FALHOU | — | O código de exceção Modbus 0x0002 indica que o valor enviado está fora da faixa aceita pelo registrador (ex.: potência solicitada acima do limite do hardware). A ação imediata é reduzir o valor ao intervalo permitido, qu |
| R05 | 0.40 | 0.80 | 0.50/1.00 | ok | — | A falha de aterramento (grounding fault) no GoodWe HCA G2 é indicada no Registrador 10002 (AC Fault Bytes 02), especificamente no bit1. Por se tratar de uma falha de segurança elétrica que depende de inspeção física, a c |
| R06 | 1.00 | 0.91 | 1.00/1.00 | ok | — | Os parâmetros de comunicação serial RS485 para o carregador GoodWe HCA G2 são: Baud rate de 9600, 8 bits de dados, 1 bit de parada e paridade N (nenhuma). |
| R07 | 0.38 | 0.80 | 0.25/0.50 | ok | — | A mensagem StopTransaction do OCPP registra o encerramento de uma sessão de recarga, consolidando o timestamp de término e o valor final do medidor (meterStop). No ecossistema GoodWe, como o carregador HCA G2 opera nativ |
| R08 | 0.25 | 0.73 | 1.00/1.00 | ok | — | O consumo é calculado pela diferença entre o registrador 10172 (meterStop) e o 10170 (meterStart). Diferença bruta: 207250 - 204500 = 2750 unidades. Como os registradores do HCA G2 são expressos em 0,01 kWh, o valor fina |
| R09 | 1.00 | 0.87 | 1.00/1.00 | ok | — | A linha GoodWe HCA G2 é composta por três modelos: o GW7K-HCA-20 (Monofásico, 7 kW), o GW11K-HCA-20 (Trifásico, 11 kW) e o GW22K-HCA-20 (Trifásico, 22 kW). |
| R10 | 0.33 | 0.00 | 1.00/0.00 | FALHOU | — | Para fornecer a informação exata sobre a instalação ao ar livre e o grau de proteção (IP) do carregador GoodWe HCA G2, é necessário consultar a seção de especificações ambientais do manual técnico. Como esses dados espec |
| R11 | 1.00 | 0.92 | 1.00/1.00 | ok | — | Não, o carregador GoodWe HCA G2 não suporta OCPP nativamente. O protocolo nativo do hardware é Modbus TCP (backend) e Modbus RTU/RS485 (local). O ChargeGrid atua como uma camada de tradução e interoperabilidade, converte |
| R12 | 1.00 | 0.77 | 1.00/1.00 | ok | — | De acordo com as regras de operação em condomínios, o veículo deve ser retirado da vaga em até 30 minutos após o término da recarga. |
| R13 | 1.00 | 0.75 | 1.00/1.00 | ok | — | De acordo com o regimento de recarga condominial, a ocupação indevida da vaga gera advertência por escrito na primeira ocorrência. A partir da segunda ocorrência no mesmo semestre, é aplicada uma multa de 10% da taxa con |
| R14 | 1.00 | 0.77 | 1.00/1.00 | ok | — | De acordo com o regimento de recarga compartilhada, cada unidade pode reservar o carregador por um tempo máximo de 4 horas por dia, com antecedência de até 48 horas via aplicativo. |
| R15 | 1.00 | 0.81 | 1.00/1.00 | ok | FAQ de Carregamento — eletropostos GoodWe ChargeGrid — 5. Posso deixar o carro conectado depois que a carga terminar? (p. 1), Regimento de Recarga Compartilhada em Condomínio — 6. Segurança e conduta (p. 1) | Em caso de alarme de falha de aterramento, o carregador deve ser desligado imediatamente. A religação e a manutenção do equipamento devem ser realizadas exclusivamente por um técnico habilitado; não tente religar o siste |
| R16 | 1.00 | 0.90 | 1.00/1.00 | ok | — | Sim. Ao redistribuir a potência entre carregadores ativos via Load Balancing, deve-se respeitar o limite mínimo de 4,2 kW por carregador, que é o valor mínimo do registrador Maximum Charging Power. |
| R17 | 1.00 | 0.91 | 1.00/1.00 | ok | — | Para recarregar 44 kWh em um carregador de 11 kW, o tempo estimado é de aproximadamente 4 horas. Note que a potência efetiva pode variar dependendo do carregador de bordo do veículo e do controle de carga dinâmico do sit |
| R18 | 1.00 | 0.85 | 1.00/1.00 | ok | — | O modelo GW30K-HCA-20 não existe na linha HCA G2 da GoodWe. Os únicos modelos disponíveis nesta linha são o GW7K-HCA-20 (7 kW), GW11K-HCA-20 (11 kW) e GW22K-HCA-20 (22 kW). |
| X01 | — | — | —/— | — | — | A informação sobre o prazo de garantia do modelo GW22K-HCA-20 não consta nos documentos técnicos recuperados. Recomendo consultar o certificado de garantia do equipamento ou entrar em contato com o suporte oficial da Goo |
| X02 | — | — | —/— | — | — | Sinto muito, mas a consulta de tarifas em tempo real de concessionárias externas (como a Enel SP) está fora do meu escopo operacional. Minha função é a orquestração de potência, auditoria de ciclos e suporte técnico para |
| X03 | — | — | —/— | — | — | Pedido fora do domínio ChargeGrid/GoodWe (assunto bloqueado por escopo). Posso ajudar com orquestração de potência, faturamento ou diagnóstico de carregadores GoodWe. |
