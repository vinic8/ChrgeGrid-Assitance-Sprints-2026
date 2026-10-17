# RAGAS — legado (ollama: `gemma4:cloud`)

Sprints 1/2: sem RAG, prompt v1 em texto corrido, saída em texto livre

Gerado em 2026-10-17T15:07:37 · config: `{"rag": false, "prompt": "system_prompt_v1", "temperature": 0.0}`

| Métrica | Valor |
|---|---|
| faithfulness_ragas | 0.137 |
| answer_relevancy_ragas | 0.732 |
| faithfulness_rubrica | 0.097 |
| answer_relevancy_rubrica | 0.681 |
| hit_documento_pct | 0.0 |
| citacao_presente_pct | 0.0 |
| citacao_correta_pct | 0.0 |
| acerto_factual_pct | 33.3 |
| recusa_indevida_pct | 0.0 |
| recusa_correta_pct | 33.3 |
| latencia_media_s | 1.696 |
| tokens_medios | 570.571 |
| erros | [] |

| Caso | faithfulness (RAGAS) | answer_relevancy (RAGAS) | rubrica F/AR | acerto | citação | resposta |
|---|---|---|---|---|---|---|
| R01 | 0.00 | 0.47 | 0.00/1.00 | FALHOU | — | **RELATÓRIO DE FATURAMENTO - CARREGADOR C11**  **Dados da Operação:** *   **ID do Veículo:** [Não informado] *   **Intervalo:** 18:30 — 19:00 (30 min) *   **Consumo Total:** 5 kWh  **Cálculo Financeiro:** (5 kWh × R$ 1,9 |
| R02 | 0.06 | 0.64 | 0.00/0.00 | FALHOU | — | **ANÁLISE DE FATURAMENTO: FROTA-07**  Para processar a cobrança, é necessário definir o perfil tarifário aplicado ao veículo. Com base na tabela de tarifas vigentes do ChargeGrid Intelligence 2026, aplique a regra corres |
| R03 | 0.08 | 0.75 | 0.00/0.75 | FALHOU | — | **Análise de Ocupação de Vaga (Idle Fee)**  Sim. De acordo com as diretrizes de otimização de fluxo do ChargeGrid Intelligence 2026, a permanência do veículo após a conclusão do ciclo de carga configura **Ocupação Indevi |
| R04 | 0.08 | 0.81 | 0.25/0.75 | ok | — | **Análise Técnica: Erro Modbus 0x0002**  **Significado:** O código de exceção `0x0002` (Illegal Data Address) indica que o mestre solicitou a leitura ou escrita de um registrador que não existe no mapa de memória do carr |
| R05 | 0.07 | 0.75 | 0.00/0.25 | FALHOU | — | **Análise Técnica: Falha de Aterramento - GoodWe HCA G2**  **Localização do Dado (Modbus RTU/TCP):** *   **Registrador:** `0x01A2` (Decimal: 418) - *Status de Alarmes/Falhas*. *   **Bit de Identificação:** `Bit 3` (Groun |
| R06 | 0.43 | 0.90 | 0.25/1.00 | ok | — | **PARÂMETROS DE COMUNICAÇÃO SERIAL RS485 - HCA G2**  Para a integração do carregador HCA G2 via Modbus RTU, utilize a seguinte configuração de stack:  *   **Protocolo:** Modbus RTU *   **Interface Física:** RS485 (Half-D |
| R07 | 0.22 | 0.81 | 0.25/0.75 | ok | — | A mensagem `StopTransaction` é o gatilho de encerramento de sessão no protocolo OCPP. Ela transforma a atividade elétrica em um registro financeiro auditável.  ### 1. O que a `StopTransaction` registra Quando o carregado |
| R08 | 0.29 | 0.76 | 0.00/1.00 | FALHOU | — | **Análise de Consumo - HCA G2**  **Cálculo:** (207.250 - 204.500) = 2.750 unidades de leitura.  Considerando a escala padrão de registradores de energia do HCA G2 (onde 1 unidade = 1 kWh): **Consumo Total: 2.750 kWh**  * |
| R09 | 0.00 | 0.85 | 0.00/0.75 | FALHOU | — | A linha **GoodWe HCA G2** é composta por carregadores AC inteligentes projetados para integração com ecossistemas fotovoltaicos e gestão de carga. Os modelos e suas respectivas potências nominais são:  / Modelo / Potênci |
| R10 | 0.08 | 0.89 | 0.00/0.75 | FALHOU | — | **Análise Técnica: Carregador HCA G2**  **Instalação:** Sim, o HCA G2 é projetado para instalação ao ar livre.  **Grau de Proteção:** *   **IP54:** Proteção contra deposição de poeira e projeções de água de qualquer dire |
| R11 | 0.14 | 0.84 | 0.00/1.00 | FALHOU | — | **Sim.** O GoodWe HCA G2 suporta o protocolo **OCPP (Open Charge Point Protocol)** nativamente.  **Análise Técnica:** A implementação do OCPP permite a integração do hardware com o CMS (*Central Management System*), viab |
| R12 | 0.00 | 0.63 | 0.25/0.75 | ok | — | A regra de liberação de vaga após a recarga é definida pela **Política de Uso do Condomínio**, porém, sob a ótica da operação **ChargeGrid**, a diretriz técnica e comercial é a seguinte:  **1. Prazo de Tolerância:** O ve |
| R13 | 0.06 | 0.68 | 0.00/0.25 | FALHOU | — | Sob a ótica da inteligência operacional ChargeGrid, a ocupação indevida de uma vaga de recarga não é apenas uma infração condominial, mas um **bloqueio de disponibilidade de infraestrutura**, impactando a eficiência do * |
| R14 | 0.09 | 0.75 | 0.00/0.25 | FALHOU | — | **CONSULTA: POLÍTICA DE RESERVA DE CARREGADORES COMPARTILHADOS**  As regras de reserva são parametrizadas via software de gestão para evitar a subutilização da infraestrutura e garantir a rotatividade do *Load Balancing* |
| R15 | 0.40 | 0.70 | 0.25/0.75 | ok | — | **Protocolo de Segurança: Falha de Aterramento (Ground Fault)**  A religação de um carregador após um alarme de falha de aterramento **não pode ser realizada por operadores comerciais ou usuários**.   Devido ao risco crí |
| R16 | 0.07 | 0.77 | 0.00/0.25 | FALHOU | — | **Sim.** Para garantir a estabilidade da carga e a integridade do hardware, a operação de *Load Balancing* segue a seguinte regra técnica:  **Potência Mínima Operacional: 6.6 kW (ou o limite inferior do protocolo de comu |
| R17 | 0.40 | 0.60 | 0.50/1.00 | ok | — | **Cálculo de Tempo de Recarga**  **Parâmetros:** - Energia Necessária: 44 kWh - Potência Nominal do Carregador: 11 kW  **Fórmula:** $\text{Tempo (h)} = \frac{\text{Energia (kWh)}}{\text{Potência (kW)}}$  **Execução:** $4 |
| R18 | 0.00 | 0.56 | 0.00/1.00 | FALHOU | — | **Modelo:** GW30K-HCA-20 **Potência Nominal de Saída:** 30 kW  **Especificações Técnicas Relevantes:** *   **Tipo:** Inversor Híbrido Trifásico. *   **Aplicação:** Gestão de energia solar e armazenamento (ESS). *   **Int |
| X01 | — | — | —/— | — | — | O prazo de garantia padrão para o carregador **GW22K-HCA-20** é de **5 anos**. |
| X02 | — | — | —/— | — | — | Informação não disponível no banco de dados local de tarifação em tempo real.   Para a precisão do faturamento e auditoria do ChargeGrid, o Operador Comercial deve inserir manualmente a tarifa vigente da Enel SP no módul |
| X03 | — | — | —/— | — | — | Solicitação fora de escopo. Minha função é a inteligência operacional da infraestrutura GoodWe/FIAP. Não possuo protocolos para processamento de receitas culinárias.  Retorne ao monitoramento de carga, balanceamento de p |
