# Manual de Produto — EV Charger GoodWe HCA G2

Fonte: "GW_HCA-G2_Datasheet-PT.pdf" e "GW_HCA-G2_User-Manual-PT.pdf" (fabricante,
2025). Todos os valores deste documento vêm do datasheet e do manual oficiais da
GoodWe. Qualquer especificação que não esteja listada aqui NÃO foi confirmada pelo
fabricante e não deve ser presumida.

## 1. Modelos da linha HCA G2

A linha HCA G2 tem 3 modelos por potência nominal (não é um único modelo com
potência ajustável em faixa livre):

| Modelo | Fases | Potência nominal | Corrente nominal | Tensão de entrada |
|---|---|---|---|---|
| GW7K-HCA-20 | Monofásico | 7 kW | 32 A | 220 V (L/N/PE) |
| GW11K-HCA-20 | Trifásico | 11 kW | 16 A | 380 V (3L/N/PE) |
| GW22K-HCA-20 | Trifásico | 22 kW | 32 A | 380 V (3L/N/PE) |

Não existem outros modelos na linha HCA G2 além desses três.

Faixa de ajuste de potência de carregamento (registrador Modbus `Maximum
Charging Power`): 4,2 kW a 22,0 kW, respeitando o máximo do modelo instalado.

## 2. Comunicação e protocolos

- **Protocolo de comunicação declarado no datasheet: Modbus TCP.**
- Portas físicas: Bluetooth, Wi-Fi, RS485 (duas portas — uma para o inversor,
  outra para o medidor MID) e LAN (para o roteador e a nuvem SEMS).
- **OCPP não é nativo**: o datasheet e o manual do HCA G2 NÃO mencionam OCPP em
  nenhum momento. O ecossistema nativo da GoodWe é RS485/Modbus (local, com
  inversor e medidor MID) mais Modbus TCP e nuvem SEMS (app SolarGo e SEMS
  Portal). O ChargeGrid trata OCPP como uma camada de tradução e
  interoperabilidade sobre os dados reais do Modbus — ver o documento
  "Interoperabilidade OCPP".

## 3. Proteções elétricas integradas

Corrente residual (RCD) 30 mA CA + 6 mA CC, sobrecorrente, sobretensão,
subtensão, falha de aterramento, surto CA (SPD Tipo III), sobretemperatura e
desligamento de emergência (botão físico). Um **RCD/RCBO externo tipo A** ainda é
exigido na instalação: o carregador não substitui a proteção do circuito.

## 4. Dados gerais

| Item | Valor |
|---|---|
| Temperatura operacional | -30 °C a +50 °C (carregador); plugue até 50 °C |
| Umidade relativa | 5% a 95%, sem condensação |
| Altitude operacional máxima | 2000 m |
| Grau de proteção | IP66 (carregador) / IP55 (plugue de carregamento) |
| Conector | IEC Tipo 2 |
| Cabo de saída | 6 m (7,5 m opcional) |
| Ruído emitido | menor que 20 dB |
| Consumo em espera | menor que 6,5 W |
| Modos de partida | App (SolarGo/SEMS), cartão RFID, início automático ao conectar |
| Modos de operação | Carregamento rápido, Prioridade solar, PV + bateria, agendamento, controle de carga dinâmico |
| Instalação | Interior ou exterior, parede ou piso/poste |
| Certificações | IEC61851-1, IEC62311, IEC62955, AS/NZS 4268:2017, IEC61008-1 |

## 5. Limite de rede e disjuntor de entrada

O datasheet não especifica um "limite de rede padrão" fixo: isso é configurado
por instalação, no registrador Modbus `Household Circuit Breaker Rated Current`
(10026) e no parâmetro `Grid Power Limit` (10039, faixa de 4,2 a 22,0 kW conforme
o modelo). Cada eletroposto GoodWe real tem seu próprio limite contratado ou
instalado. O ChargeGrid **nunca assume um valor padrão fixo entre instalações**:
usa sempre o limite informado pelo operador para aquele site ou, quando
disponível, a leitura em tempo real desses registradores. Se nenhum dos dois
estiver disponível, o assistente pede o limite de rede daquele eletroposto.

## 6. Load Balancing e controle de carga dinâmico

Após ativado, o carregador ajusta a velocidade de carregamento (ou pausa)
conforme os dados do medidor e a corrente de conexão à rede configurada, para
evitar o disparo do disjuntor principal, e retoma automaticamente quando a
diferença entre a corrente contratada e a consumida permitir. É esse mecanismo
que o ChargeGrid aciona ao negar uma solicitação de potência e sugerir
"reduzir X para liberar Y".

## 7. Uso desta referência pelo ChargeGrid Assistant

Ao orientar sobre limite de potência, cite o registrador `Household Circuit
Breaker Rated Current` ou `Grid Power Limit` como fonte real do dado quando o
operador mencionar leitura do equipamento. Nunca aplique um valor de referência
fixo entre instalações e nunca informe uma especificação (potência, corrente,
certificação, garantia, preço) que não esteja listada neste manual.
