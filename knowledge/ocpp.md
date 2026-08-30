# OCPP — Camada de Interoperabilidade (não nativa do hardware GoodWe)

**Nota de proveniência importante**: ao revisar a documentação oficial da GoodWe
(datasheet e manual do HCA G2 — ver `knowledge/charger_goodwe.md`), confirmamos
que o carregador real **não fala OCPP nativamente** — seu protocolo declarado é
Modbus TCP (backend) + Modbus RTU/RS485 (local, com inversor e medidor MID),
integrado ao ecossistema próprio da GoodWe (SEMS Portal / SolarGo). O desafio
ChargeGrid Intelligence, no entanto, pede explicitamente cobertura de "protocolos
OCPP e MODBUS". A leitura mais honesta é: o ChargeGrid atua como uma camada de
**tradução/interoperabilidade** que expõe os dados reais do Modbus GoodWe em
vocabulário OCPP — para integração com sistemas de gestão de frota, CSMS de
terceiros ou relatórios que exigem o padrão do setor — sem que isso signifique
que o carregador físico execute o protocolo OCPP em si.

## Mapeamento: conceito OCPP → registrador Modbus real do HCA G2

| Conceito OCPP 1.6 | Dado Modbus GoodWe equivalente |
|---|---|
| `StatusNotification` (estado do conector) | Registrador `10017` (Charging Station Status: idle/handshake/charging/completed/alarm/...) |
| `StatusNotification.errorCode` | Bits de falha dos registradores `10001-10008` (ver `knowledge/modbus_rs485.md`) |
| `StartTransaction` / `meterStart` | Início do ciclo — registrador `10170` (Meter Reading Before Charging, em 0,01 kWh) e `10158-10160` (Charging Start Time) |
| `StopTransaction` / `meterStop` | Fim do ciclo — registrador `10172` (Meter Reading After Charging, em 0,01 kWh) e `10162-10164` (Charging End Time); `meterStop - meterStart` = consumo do ciclo |
| `StopTransaction.reason` | Registrador `10168` (Reason for Charging Termination — códigos detalhados no Apêndice 2 do protocolo GoodWe carregador↔servidor, não replicado aqui) |
| `MeterValues` (leituras intermediárias) | Registradores `10015` (Charging power) e `10016` (Charging Capacity, consumo do ciclo em andamento) |
| `Authorize` | Registrador `10076` (Charge starting mode: cartão RFID, app, VIN, plug-and-charge etc.) |
| Valor a faturar do ciclo | Registrador `10061` (Charge amount, disponível em "modo de operação" — o próprio carregador já calcula um valor monetário internamente, na configuração vigente do equipamento) |

## Por que manter essa camada conceitual

- O enunciado do desafio pede cobertura de OCPP explicitamente — remover essa
  referência deixaria uma lacuna frente ao Bloco A/C da rubrica.
- Ambientes reais de gestão de frota multi-fabricante frequentemente precisam
  dessa tradução: nem todo carregador da frota é GoodWe, e um CSMS central
  tipicamente fala OCPP com o "mundo exterior" enquanto lida com protocolos
  proprietários (como o Modbus da GoodWe) internamente.
- Ser transparente sobre isso evita o assistente "inventar" que o hardware
  suporta um protocolo que a documentação oficial não confirma.

## Relação com o ChargeGrid Assistant

Ao explicar um conceito de "ciclo de sessão" em termos operacionais, prefira
citar o registrador Modbus real (fonte de verdade, ver `modbus_rs485.md`) e, se
o operador perguntar especificamente em termos OCPP (ex.: "o que é
StopTransaction"), use a tabela de mapeamento acima para traduzir — deixando
claro, se perguntado diretamente, que o carregador GoodWe HCA fala Modbus
nativamente e o OCPP é a camada de interoperabilidade do ChargeGrid.
