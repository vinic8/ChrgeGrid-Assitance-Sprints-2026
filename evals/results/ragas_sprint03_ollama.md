# RAGAS — sprint03 (ollama: `gemma4:cloud`)

Sprint 03 (commit 244a814): FAISS + FastEmbed MiniLM, 4 docs .md, k=6, prompt v6, sem citação

Gerado em 2026-10-17T15:07:53 · config: `{"vector_store": "FAISS", "embeddings": "paraphrase-multilingual-MiniLM-L12-v2", "k": 6, "chunking": "1 chunk por seção ##", "prompt": "system_prompt_v6", "temperature": 0.2, "max_tokens": 600, "base": "knowledge/*.md (4 documentos)"}`

| Métrica | Valor |
|---|---|
| faithfulness_ragas | 0.497 |
| answer_relevancy_ragas | 0.655 |
| faithfulness_rubrica | 0.847 |
| answer_relevancy_rubrica | 0.722 |
| hit_documento_pct | 66.7 |
| citacao_presente_pct | 0.0 |
| citacao_correta_pct | 0.0 |
| acerto_factual_pct | 55.6 |
| recusa_indevida_pct | 16.7 |
| recusa_correta_pct | 66.7 |
| latencia_media_s | 1.3 |
| tokens_medios | 97.095 |
| erros | [] |

| Caso | faithfulness (RAGAS) | answer_relevancy (RAGAS) | rubrica F/AR | acerto | citação | resposta |
|---|---|---|---|---|---|---|
| R01 | 0.50 | 0.70 | 1.00/1.00 | ok | — | Ciclo registrado no carregador C11. O período de recarga (18:30 às 19:00) enquadra-se integralmente no Posto de Ponta, com tarifa de R$ 1,65/kWh. Cálculo: 5 kWh × R$ 1,65 = R$ 8,25. |
| R02 | 0.67 | 0.82 | 1.00/1.00 | ok | — | Para o veículo FROTA-07, aplica-se a tarifa fixa preferencial de R$ 0,70/kWh destinada a veículos de frota cadastrada, a qual sobrepõe a tarifa de posto horário (Ponta). Cálculo: 20 kWh × R$ 0,70 = R$ 14,00. |
| R03 | 0.33 | 0.73 | 1.00/1.00 | FALHOU | — | Não há previsão de cobrança por tempo de ocupação de vaga (idle fee) na política de tarifação dinâmica atual. O faturamento é baseado estritamente no consumo de energia (kWh) e nas regras de postos tarifários ou tarifas  |
| R04 | 1.00 | 0.76 | 1.00/1.00 | ok | — | O código de exceção Modbus 0x0002 indica 'Illegal Data Address'. Isso significa que o controlador tentou acessar um endereço de registrador inválido ou que não é suportado pelo modelo HCA G2. A ação imediata é conferir o |
| R05 | 0.25 | 0.64 | 0.25/0.50 | FALHOU | — | A falha de aterramento (Ground Failure) é reportada via bits de falha nos registradores Modbus 10001 a 10008. Diante deste erro, a conduta obrigatória é a interrupção imediata da operação do eletroposto. Por se tratar de |
| R06 | 1.00 | 0.91 | 1.00/1.00 | ok | — | Os parâmetros de comunicação serial RS485 para o carregador GoodWe HCA G2 são: Baud rate de 9600, 8 bits de dados, 1 bit de parada e sem paridade (N). |
| R07 | 0.50 | 0.82 | 0.25/0.50 | FALHOU | — | A mensagem StopTransaction do OCPP registra o encerramento de uma sessão de recarga, reportando o timestamp final e o valor do medidor (meter stop) no momento da desconexão. Para o faturamento, o consumo é calculado pela |
| R08 | 0.00 | 0.76 | 1.00/1.00 | FALHOU | — | O consumo foi calculado com base na diferença entre os registradores de energia do HCA G2: 207.250 (meterStop) - 204.500 (meterStart) = 2.750 kWh. |
| R09 | 1.00 | 0.89 | 1.00/1.00 | ok | — | A linha GoodWe HCA G2 é composta por três modelos com potências nominais distintas: o GW7K-HCA-20 (Monofásico, 7 kW), o GW11K-HCA-20 (Trifásico, 11 kW) e o GW22K-HCA-20 (Trifásico, 22 kW). |
| R10 | 1.00 | 0.78 | 1.00/1.00 | ok | — | Sim, o carregador GoodWe HCA G2 pode ser instalado em ambientes externos (exterior). Ele possui grau de proteção IP66 para o corpo do carregador e IP55 para o plugue de carregamento. |
| R11 | 1.00 | 0.83 | 1.00/1.00 | ok | — | Não. O hardware GoodWe HCA G2 não suporta OCPP nativamente; seu protocolo de comunicação declarado é Modbus TCP (backend) e Modbus RTU/RS485 (local). O ChargeGrid atua como uma camada de tradução e interoperabilidade, ma |
| R12 | 0.14 | 0.00 | 1.00/0.00 | FALHOU | — | Esta solicitação está fora do escopo de operação do ChargeGrid Assistant. Minha função é a orquestração de potência, registro de ciclos via OCPP, faturamento e diagnóstico técnico de eletropostos GoodWe. Regras de conviv |
| R13 | 0.00 | 0.00 | 1.00/0.00 | FALHOU | — | Sinto muito, mas essa questão está fora do meu escopo de atuação. Como ChargeGrid Assistant, sou responsável exclusivamente pela orquestração de potência, faturamento, diagnóstico de comunicação (OCPP/Modbus) e integrida |
| R14 | 0.00 | 0.00 | 1.00/0.00 | FALHOU | — | Sua pergunta está fora do escopo de atuação do ChargeGrid Assistant. Minha função é a orquestração de potência, registro de ciclos de recarga via OCPP, faturamento e diagnóstico técnico de eletropostos GoodWe. Regras de  |
| R15 | 0.75 | 0.68 | 0.75/1.00 | ok | — | Diante de um alarme de falha de aterramento (registrador Modbus 10002, bit1), a operação deve ser interrompida imediatamente. A religação do carregador só pode ser efetuada por um eletricista ou técnico habilitado, após  |
| R16 | 0.00 | 0.76 | 0.00/1.00 | FALHOU | — | Sim. Para carregadores GoodWe HCA G2, a potência mínima de saída é limitada pela corrente mínima de carga do veículo e pelas especificações do hardware (geralmente 6A por fase, resultando em aproximadamente 3,7kW em sist |
| R17 | 0.00 | 0.86 | 1.00/1.00 | ok | — | Para recarregar 44 kWh com uma potência de 11 kW, o tempo estimado é de 4 horas (44 kWh / 11 kW = 4h). Este cálculo assume a manutenção da potência nominal durante todo o ciclo, sem considerar a curva de descarga da bate |
| R18 | 0.80 | 0.85 | 1.00/0.00 | ok | — | O modelo GW30K-HCA-20 não consta nas especificações técnicas da linha GoodWe HCA G2. Os modelos disponíveis são o GW7K-HCA-20 (7 kW), GW11K-HCA-20 (11 kW) e GW22K-HCA-20 (22 kW). Verifique se o código do modelo está corr |
| X01 | — | — | —/— | — | — | Sinto muito, mas a informação sobre prazos de garantia não faz parte do meu escopo operacional. Meu domínio é restrito à orquestração de potência, registro de ciclos via OCPP, faturamento e diagnóstico técnico de eletrop |
| X02 | — | — | —/— | — | — | Solicitação fora de escopo. Minha operação é restrita à orquestração de potência, faturamento e diagnóstico de eletropostos GoodWe, conforme definido em <escopo>. Não possuo acesso a tarifas externas de concessionárias d |
| X03 | — | — | —/— | — | — | Pedido fora do domínio ChargeGrid/GoodWe (assunto bloqueado por escopo). Posso ajudar com orquestração de potência, faturamento ou diagnóstico de carregadores GoodWe. |
