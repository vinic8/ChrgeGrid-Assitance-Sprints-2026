# Mapa Modbus RTU/RS485 — GoodWe HCA G2

Fonte: "Mapa MODBUS_HCA G2.pdf" (protocolo Modbus da 2ª geração do carregador CA
GoodWe, v1.0.15) e "GW_HCA-G2_Datasheet-PT.pdf". Os dados abaixo vêm do documento
oficial do fabricante.

## 1. Formato de comunicação serial (RS485)

| Parâmetro | Valor |
|---|---|
| Baud rate | 9600 |
| Bits de dados | 8 |
| Bits de parada | 1 |
| Paridade | N (nenhuma) |

## 2. Códigos de exceção Modbus

Estes são erros de PROTOCOLO (a requisição Modbus em si é inválida), diferentes
dos códigos de FALHA do equipamento (seção 3). O mapa oficial do HCA G2 define
apenas 4 códigos de exceção:

| Código | Nome | Causa provável | Ação imediata |
|---|---|---|---|
| 0x0001 | Illegal Function | O controlador pediu uma função Modbus que o carregador não suporta (ex.: firmware desatualizado) | Verificar a versão de firmware do carregador |
| 0x0002 | Illegal Data Address | Endereço de registrador inválido ou fora do mapa suportado por este modelo | Conferir o endereço contra o mapa do HCA G2 (registradores válidos: 10000+, 10500+, 20000+, 30000+) |
| 0x0003 | Illegal Data Value | Valor fora da faixa aceita pelo registrador (ex.: potência acima do limite do hardware) | Reduzir o valor ao intervalo permitido (ex.: 4,2 a 22,0 kW para Maximum Charging Power) |
| 0x0004 | Slave Device Failure | Falha interna no carregador ao processar o comando | Reiniciar o carregador; se persistir, abrir chamado técnico |

Qualquer código fora desta tabela (ex.: um código de 2 dígitos como "0B") não
consta no mapa Modbus do HCA G2 e deve ser confirmado no equipamento.

## 3. Códigos de falha do carregador (registradores 10001 a 10008)

Diferente dos códigos de exceção, estes são bits de status lidos via Modbus
("AC Fault Bytes") que indicam falhas reais do equipamento.

**Registrador 10001 (AC Fault Bytes 01)**: bit0 parada de emergência acionada;
bit1 sobretensão; bit2 sobrecorrente; bit3 subtensão; bit4 falha no conector;
bit5 S2 desconectado; bit6 sobretemperatura ambiente; bit7 sobretemperatura do
plugue de carga.

**Registrador 10002 (AC Fault Bytes 02)**: bit0 falha de controle de acesso;
**bit1 falha de aterramento (grounding fault)**; bit2 timeout de handshake com o
veículo; bit3 falha de comunicação com cartão RF; bit4 falha de comunicação com
display serial; bit5 falha de comunicação com o medidor embarcado; bit6 falha no
relé de saída; bit7 falha na trava do plugue.

**Registrador 10003 (AC Fault Bytes 03)**: bit0 curto-circuito na saída; bit1
falha de corrente de fuga; bit2 pausa de carregamento por mais de 10 min; bit3
leitura anômala do medidor; bit4 carregador offline ao iniciar carga por
PV/bateria; bit5 potência insuficiente ao iniciar carga por PV/bateria.

**Registrador 10007 (falhas de hardware)**: bit0 falha na flash externa; bit1
falha na EEPROM; bit2 falha no dispositivo de detecção de vazamento; bit3
alimentação de entrada anormal; bit4 SN não registrado; bit5 parâmetros de
fábrica anômalos; bit6 firmware não autorizado.

O registrador 10005 replica um subconjunto desses bits como **alarmes**
(severidade menor, não interrompem a carga), em vez de **falhas** (registradores
10001 a 10003).

## 4. Registradores operacionais

| Registrador | Nome | Uso |
|---|---|---|
| 10017 | Charging Station Status | 00 ocioso sem plugue; 01 ocioso com plugue; 02 handshake com veículo; 03 carregando; 04 carga completa; 05 alarme; 06 início agendado; 07 manutenção; 08 falha ao iniciar; 09 atualizando firmware; 10 interrompido (PV/bateria insuficiente) |
| 10026 | Household circuit breaker rated current | Corrente nominal do disjuntor de entrada: fonte real do "Limite da Rede" |
| 10029 | Maximum Charging Power | Potência máxima configurada (4,2 a 22,0 kW conforme o modelo) |
| 10039 | Maximum Grid Electricity Draw Power | Limite de compra da rede (Grid Power Limit), usado pelo controle de carga dinâmico |
| 10075 | Car connection status | 0 desconectado; 1 meia-conexão; 2 conectado |
| 10084 | CP voltage state | Estado do sinal Control Pilot (IEC 61851) entre carregador e veículo |

## 5. Checklist de diagnóstico físico (RS485)

- Passo 1, conexão do cabo: verificar se os fios A/B não estão invertidos entre
  os dispositivos, causa comum de falha de comunicação com inversor ou medidor.
- Passo 2, endereço Modbus duplicado: dois dispositivos com o mesmo endereço no
  mesmo barramento causam colisão e leituras corrompidas.
- Passo 3, falha de aterramento (registrador 10002, bit1): interromper a operação
  e acionar eletricista ou técnico habilitado antes de religar. Não é uma falha
  que se resolve à distância.
- Passo 4, reinício da sessão Modbus: reiniciar o driver/gateway Modbus sem
  desligar o carregador inteiro resolve a maioria dos travamentos de comunicação.
- Passo 5, power-cycle do carregador: último recurso antes de abrir chamado
  técnico.

## 6. Uso desta referência pelo ChargeGrid Assistant

Quando o operador reportar um código de exceção Modbus (0x0001 a 0x0004), use a
tabela da seção 2. Quando reportar um comportamento do carregador (não responde,
parou, alarme), mapeie para os bits de falha dos registradores 10001 a 10008
quando o sintoma bater e siga o checklist da seção 5. Nunca invente um código de
exceção ou de falha que não esteja neste mapa.
