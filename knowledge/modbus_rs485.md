# Modbus RTU / RS485 — Referência Real (GoodWe HCA G2)

Fonte: "Mapa MODBUS_HCA G2.pdf" (protocolo Modbus da 2ª geração do carregador CA
GoodWe, v1.0.15) e "GW_HCA-G2_Datasheet-PT.pdf". Substitui uma versão anterior
desta base que usava códigos de exceção genéricos e não verificados — os dados
abaixo vêm do documento oficial do fabricante.

## Formato de comunicação serial (RS485)

| Parâmetro | Valor |
|---|---|
| Baud rate | 9600 |
| Bits de dados | 8 |
| Bits de parada | 1 |
| Paridade | N (nenhuma) |

## Códigos de exceção Modbus (nível de protocolo)

Estes são erros de PROTOCOLO (a requisição Modbus em si é inválida) — diferentes
dos códigos de FALHA do equipamento (ver seção seguinte). O mapa oficial do HCA
G2 define apenas 4 códigos de exceção:

| Código | Nome | Causa provável | Ação imediata |
|---|---|---|---|
| `0x0001` | Illegal Function | O controlador pediu uma função Modbus que o carregador não suporta (ex.: firmware desatualizado) | Verificar versão de firmware do carregador |
| `0x0002` | Illegal Data Address | Endereço de registrador Modbus inválido ou fora do mapa suportado por este modelo | Conferir o endereço contra o mapa de registradores do HCA G2 (registradores válidos: 10000+, 10500+, 20000+, 30000+) |
| `0x0003` | Illegal Data Value | Valor fora da faixa aceita pelo registrador (ex.: potência de carregamento acima do limite do hardware) | Reduzir o valor ao intervalo permitido (ex.: 4,2–22,0 kW para `Maximum Charging Power`) |
| `0x0004` | Slave Device Failure | Falha interna no carregador ao processar o comando | Reiniciar o carregador; se persistir, abrir chamado técnico |

## Códigos de FALHA do carregador (registradores 10001–10008, "AC Fault Bytes")

Diferente dos códigos de exceção acima, estes são bits de status lidos via Modbus
que indicam falhas reais do equipamento — é o que efetivamente aparece quando o
operador pergunta "por que o carregador parou" ou "o que esse alarme significa".

**Registrador 10001 (AC Fault Bytes 01)** — bit a bit:
`bit0` parada de emergência acionada · `bit1` sobretensão · `bit2` sobrecorrente ·
`bit3` subtensão · `bit4` falha no conector · `bit5` S2 desconectado ·
`bit6` sobretemperatura ambiente · `bit7` sobretemperatura do plugue de carga

**Registrador 10002 (AC Fault Bytes 02)**:
`bit0` falha de controle de acesso · **`bit1` falha de aterramento (grounding fault)** ·
`bit2` timeout de handshake com o veículo · `bit3` falha de comunicação com cartão RF ·
`bit4` falha de comunicação com display serial · `bit5` falha de comunicação com o
medidor embarcado · `bit6` falha no relé de saída · `bit7` falha na trava do plugue

**Registrador 10003 (AC Fault Bytes 03)**:
`bit0` curto-circuito na saída · `bit1` falha de corrente de fuga ·
`bit2` pausa de carregamento por mais de 10 min · `bit3` leitura anômala do medidor ·
`bit4` carregador offline ao iniciar carga por PV/bateria · `bit5` potência
insuficiente ao iniciar carga por PV/bateria

**Registrador 10007 (falhas de hardware)**:
`bit0` falha na flash externa · `bit1` falha na EEPROM · `bit2` falha no
dispositivo de detecção de vazamento · `bit3` alimentação de entrada anormal ·
`bit4` SN não registrado · `bit5` parâmetros de fábrica anômalos ·
`bit6` firmware não autorizado

O registrador 10005 replica um subconjunto desses bits como **alarmes** (severidade
menor, não interrompem a carga) em vez de **falhas** (registrador 10001-10003).

## Registradores operacionais relevantes para orquestração e diagnóstico

| Registrador | Nome | Uso |
|---|---|---|
| `10017` | Charging Station Status | 00 ocioso sem plugue · 01 ocioso com plugue · 02 handshake com veículo · 03 carregando · 04 carga completa · 05 alarme · 06 início agendado · 07 manutenção · 08 falha ao iniciar · 09 atualizando firmware · 10 interrompido (PV/bateria insuficiente) |
| `10026` | Household/site circuit breaker rated current | Corrente nominal do disjuntor de entrada — é a fonte real do "Limite da Rede" usado na orquestração de potência, quando disponível via Modbus |
| `10029` | Maximum Charging Power | Potência máxima configurada (4,2–22,0 kW conforme o modelo) |
| `10039` | Maximum Grid Electricity Draw Power | Limite de potência de compra da rede (Grid Power Limit) — usado pelo Controle de Carga Dinâmico |
| `10075` | Car connection status | 0 desconectado · 1 meia-conexão · 2 conectado |
| `10084` | CP voltage state | Estado do sinal de Control Pilot (IEC 61851) entre carregador e veículo |

## Checklist de diagnóstico físico (RS485)

1. **Conexão do cabo**: verificar se os fios A/B não estão invertidos entre os
   dispositivos — causa comum de falha de comunicação com inversor/medidor.
2. **Endereço Modbus duplicado**: dois dispositivos com o mesmo endereço no
   mesmo barramento causam colisão e leituras corrompidas.
3. **Falha de aterramento (registrador 10002, bit1)**: interromper a operação
   e acionar eletricista/técnico habilitado antes de religar — ver
   `<limites_de_atuacao>` no system prompt, não é uma falha que se resolve à
   distância.
4. **Reinício da sessão Modbus**: reiniciar o driver/gateway Modbus sem
   desligar o carregador inteiro resolve a maioria dos travamentos de
   comunicação.
5. **Power-cycle do carregador**: último recurso antes de abrir chamado
   técnico.

## Relação com o ChargeGrid Assistant

Quando o operador reportar um código de exceção Modbus (0x0001–0x0004), use a
tabela de exceções acima. Quando reportar um comportamento do carregador (não
responde, parou, alarme), mapeie para os bits de falha dos registradores
10001–10008 quando o sintoma bater, e siga o checklist de diagnóstico físico.
Nunca invente um código de exceção ou de falha que não esteja nesta tabela —
se o operador citar um código fora do mapa (ex.: um código de 2 dígitos como
"0B"), informe que esse código não consta no mapa Modbus do HCA G2 e peça para
confirmar o valor reportado pelo equipamento.
