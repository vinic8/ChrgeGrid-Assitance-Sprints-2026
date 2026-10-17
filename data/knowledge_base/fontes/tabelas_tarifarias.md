# Tabelas Tarifárias — ChargeGrid Intelligence 2026

**Nota de proveniência**: esta política é **ilustrativa**, elaborada para o
projeto ChargeGrid. Não é uma tarifa real publicada pela GoodWe. A documentação
oficial do HCA G2 confirma que o carregador já expõe um valor monetário calculado
no próprio equipamento (registrador Modbus 10061, "Charge amount"), o que mostra
que aplicar uma política de tarifação sobre os dados do carregador é compatível
com o hardware real.

A política substitui a tarifa fixa única por **postos tarifários horários**
(time-of-use), refletindo o custo da energia ao longo do dia, no mesmo princípio
das tarifas branca e verde do setor elétrico brasileiro.

## 1. Postos tarifários (horário local, todos os dias)

| Posto | Horário | Tarifa (R$/kWh) | Observação |
|---|---|---|---|
| Fora de ponta (madrugada) | 00:00 às 06:59 | R$ 0,55 | Tarifa mais baixa, incentiva recarga noturna |
| Fora de ponta (dia) | 07:00 às 17:59 | R$ 0,75 | Tarifa padrão diurna |
| Ponta | 18:00 às 20:59 | R$ 1,65 | Horário de pico do sistema elétrico, tarifa mais alta |
| Fora de ponta (noite) | 21:00 às 23:59 | R$ 0,75 | Retorno à tarifa padrão |

Exemplo de cálculo: um ciclo de 12 kWh das 02:00 às 04:00 cai inteiro no posto Fora
de ponta (madrugada), então o faturamento é 12 kWh × R$ 0,55 = R$ 6,60.

## 2. Ciclos que atravessam mais de um posto

Se o ciclo atravessar mais de um posto tarifário (ex.: início às 17:30 e fim às
19:00), o faturamento deve ser proporcional ao consumo em cada posto. Quando a
conversa não trouxer o consumo por sub-período, o assistente deve pedir o consumo
segmentado em vez de aplicar uma tarifa única arbitrariamente.

## 3. Tarifa de frota

Veículos de frota cadastrada (ID começando com "FROTA-") pagam tarifa fixa
preferencial de R$ 0,70/kWh, independente do posto horário, conforme contrato
comercial. Essa regra se sobrepõe à tabela de postos tarifários.

## 4. Descontos

Recarga fora de ponta acima de 4 horas contínuas recebe desconto de 10% sobre o
total do ciclo (incentivo ao uso em horário de baixa demanda). O desconto não se
acumula com a tarifa de frota.

## 5. Sobretaxa por excedente de demanda

Quando uma solicitação de potência é **negada** por exceder o limite da rede,
não há faturamento de excedente: a operação simplesmente não é autorizada. A
sobretaxa de demanda só se aplica a ciclos **já autorizados e concluídos** que,
por telemetria (MeterValues), mostrarem picos de potência acima do contratado:
soma-se uma multa de 20% sobre o valor do ciclo inteiro, e o caso deve ser
sinalizado para auditoria humana antes da cobrança. O assistente não fecha essa
cobrança sozinho.

## 6. Tarifa de ocupação ociosa

Após o fim da carga (status 04, carga completa), o veículo tem 15 minutos de
tolerância para liberar a vaga. A partir daí, cobra-se R$ 0,50 por minuto de
ocupação ociosa, limitado a R$ 30,00 por ciclo. A tarifa de ocupação não se
aplica a vagas de condomínio residencial, que seguem o regimento condominial.

## 7. Regras de aplicação pelo ChargeGrid Assistant

Ao calcular faturamento, o assistente deve: identificar o horário do ciclo e
aplicar o posto tarifário correto da seção 1; aplicar a tarifa de frota quando o
ID do veículo começar com "FROTA-"; nunca aplicar a sobretaxa de demanda sem que
o operador informe uma leitura de potência acima do contratado; e, se a tarifa
não puder ser determinada com segurança, perguntar o horário do ciclo em vez de
assumir um valor.
