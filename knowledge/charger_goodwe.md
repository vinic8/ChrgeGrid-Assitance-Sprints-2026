# EV Charger GoodWe HCA G2 — Especificações Reais

Fonte: "GW_HCA-G2_Datasheet-PT.pdf" e "GW_HCA-G2_User-Manual-PT.pdf" (fabricante,
2025). Substitui uma versão anterior desta base que estimava valores plausíveis
sem confirmação — os dados abaixo são do datasheet oficial.

## Modelos da linha HCA G2

A linha HCA G2 tem 3 modelos por potência nominal (não é um único modelo com
potência ajustável em faixa livre):

| Modelo | Fases | Potência nominal | Corrente nominal | Tensão de entrada |
|---|---|---|---|---|
| GW7K-HCA-20 | Monofásico | 7 kW | 32 A | 220 V (L/N/PE) |
| GW11K-HCA-20 | Trifásico | 11 kW | 16 A | 380 V (3L/N/PE) |
| GW22K-HCA-20 | Trifásico | 22 kW | 32 A | 380 V (3L/N/PE) |

Faixa de ajuste de potência de carregamento (registrador Modbus `Maximum
Charging Power`): 4,2 kW a 22,0 kW, respeitando o máximo do modelo instalado.

## Comunicação e protocolos

- **Protocolo de comunicação declarado no datasheet: Modbus TCP.**
- Portas físicas: Bluetooth, Wi-Fi, RS485 (×2 — uma para inversor, outra para
  medidor MID), LAN (para o roteador/nuvem SEMS).
- **Nota importante sobre OCPP**: o datasheet e o manual do HCA G2 NÃO mencionam
  OCPP em nenhum momento — o ecossistema nativo da GoodWe é RS485/Modbus (local,
  com inversor e medidor MID) + Modbus TCP/nuvem SEMS (com o app SolarGo/SEMS
  Portal). O desafio ChargeGrid Intelligence pede explicitamente cobertura de
  OCPP e Modbus; como o hardware real não fala OCPP nativamente, o ChargeGrid
  trata OCPP como uma camada de **tradução/interoperabilidade** que expõe os
  dados reais do Modbus (status, sessão, falhas) em vocabulário OCPP para
  integração com sistemas de gestão de frota/CSMS de terceiros — ver
  `knowledge/ocpp.md` para o mapeamento exato.

## Proteções elétricas (integradas)

Corrente residual (RCD) 30 mA CA + 6 mA CC · sobrecorrente · sobretensão ·
subtensão · falha de aterramento · surto CA (SPD Tipo III) · sobretemperatura ·
desligamento de emergência (botão físico). Um **RCD/RCBO externo tipo A** ainda é
exigido na instalação (o carregador não substitui a proteção de circuito).

## Dados gerais

| Item | Valor |
|---|---|
| Faixa de temperatura operacional | -30°C a +50°C (carregador); plugue até 50°C |
| Umidade relativa | 5%–95%, sem condensação |
| Altitude operacional máxima | 2000 m |
| Grau de proteção | IP66 (carregador) / IP55 (plugue de carregamento) |
| Conector | IEC Tipo 2 |
| Cabo de saída | 6 m (7,5 m opcional) |
| Ruído emitido | < 20 dB |
| Consumo em espera | < 6,5 W |
| Modos de partida | App (SolarGo/SEMS), cartão RFID, início automático ao conectar |
| Modos de operação | Carregamento rápido, Prioridade solar, PV + bateria, agendamento, controle de carga dinâmico |
| Instalação | Interior ou exterior, parede ou piso/poste |
| Certificações | IEC61851-1, IEC62311, IEC62955, AS/NZS 4268:2017, IEC61008-1 |

## Limite de rede / disjuntor de entrada

O datasheet não especifica um "limite de rede padrão" fixo — isso é configurado
por instalação, no registrador Modbus `Household Circuit Breaker Rated Current`
(10026) e no parâmetro `Grid Power Limit` (10039, faixa 4,2–22,0 kW conforme o
modelo). Cada eletroposto GoodWe real tem seu próprio limite contratado/instalado
— o ChargeGrid **nunca assume um valor padrão fixo entre instalações**: usa
sempre o limite informado pelo operador na conversa para aquele site específico
ou, quando disponível, a leitura em tempo real desses registradores Modbus do
equipamento em questão. Se nenhum dos dois estiver disponível, o assistente pede
o limite de rede daquele eletroposto em vez de presumir um número.

## Load Balancing / Controle de Carga Dinâmico

Após ativado, o carregador ajusta a velocidade de carregamento (ou pausa)
conforme os dados do medidor e a corrente de conexão à rede configurada, para
evitar o disparo do disjuntor principal — reiniciando automaticamente quando a
diferença entre a corrente contratada e a consumida permitir. É esse mecanismo
que o ChargeGrid aciona ao negar uma solicitação de potência e sugerir
"reduzir X para liberar Y".

## Relação com o ChargeGrid Assistant

Ao orientar sobre limite de potência, cite o registrador `Household Circuit
Breaker Rated Current`/`Grid Power Limit` como a fonte real do dado quando o
operador mencionar leitura do equipamento; nunca aplique um valor de referência
fixo entre instalações — cada eletroposto GoodWe real tem seu próprio limite de
rede/disjuntor, que vem sempre da conversa (o operador informando o site em
questão) ou da leitura do equipamento daquele eletroposto específico.
