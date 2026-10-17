# Interoperabilidade OCPP — camada de tradução do ChargeGrid

**Nota de proveniência**: a documentação oficial da GoodWe (datasheet e manual
do HCA G2) confirma que o carregador **não fala OCPP nativamente**. O protocolo
declarado é Modbus TCP (backend) mais Modbus RTU/RS485 (local, com inversor e
medidor MID), integrado ao ecossistema GoodWe (SEMS Portal e SolarGo). O
ChargeGrid atua como uma camada de **tradução e interoperabilidade** que expõe os
dados reais do Modbus GoodWe em vocabulário OCPP 1.6, para integração com
sistemas de gestão de frota e CSMS de terceiros, sem que o carregador físico
execute OCPP.

## 1. Mapeamento de conceitos OCPP para registradores Modbus

| Conceito OCPP 1.6 | Dado Modbus GoodWe equivalente |
|---|---|
| StatusNotification (estado do conector) | Registrador 10017 (Charging Station Status: ocioso, handshake, carregando, completo, alarme etc.) |
| StatusNotification.errorCode | Bits de falha dos registradores 10001 a 10008 (ver "Mapa Modbus HCA G2") |
| StartTransaction / meterStart | Início do ciclo: registrador 10170 (Meter Reading Before Charging, em 0,01 kWh) e 10158 a 10160 (Charging Start Time) |
| StopTransaction / meterStop | Fim do ciclo: registrador 10172 (Meter Reading After Charging, em 0,01 kWh) e 10162 a 10164 (Charging End Time) |
| StopTransaction.reason | Registrador 10168 (Reason for Charging Termination) |
| MeterValues (leituras intermediárias) | Registradores 10015 (Charging power) e 10016 (Charging Capacity, consumo do ciclo em andamento) |
| Authorize | Registrador 10076 (Charge starting mode: cartão RFID, app, VIN, plug-and-charge) |
| Valor a faturar do ciclo | Registrador 10061 (Charge amount, disponível em modo de operação) |

## 2. Ciclo de sessão e cálculo do consumo

Um ciclo de recarga começa com StartTransaction, que registra o meterStart
(leitura do medidor antes da carga), e termina com StopTransaction, que registra
o meterStop (leitura do medidor depois da carga) e o motivo do encerramento. O
consumo faturável do ciclo é sempre **meterStop menos meterStart**, em kWh. Como
os registradores 10170 e 10172 são expressos em 0,01 kWh, a diferença bruta deve
ser dividida por 100 para obter kWh. Exemplo: meterStart = 152300 e
meterStop = 154100 resultam em 1800 unidades, ou seja, 18,00 kWh.

## 3. Por que manter essa camada

- Ambientes de gestão de frota multi-fabricante frequentemente precisam dessa
  tradução: um CSMS central tipicamente fala OCPP com o mundo exterior enquanto
  lida internamente com protocolos proprietários, como o Modbus da GoodWe.
- Ser transparente sobre isso evita afirmar que o hardware suporta um protocolo
  que a documentação oficial não confirma.

## 4. Uso desta referência pelo ChargeGrid Assistant

Ao explicar o ciclo de sessão, prefira citar o registrador Modbus real (fonte de
verdade) e, se o operador perguntar em termos OCPP (ex.: "o que é
StopTransaction"), use a tabela da seção 1 para traduzir, deixando claro, se
perguntado diretamente, que o HCA G2 fala Modbus nativamente e o OCPP é a camada
de interoperabilidade do ChargeGrid.
