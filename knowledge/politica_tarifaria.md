# Política de Tarifação Dinâmica — ChargeGrid Intelligence 2026

**Nota de proveniência**: esta política é **ilustrativa/fictícia**, elaborada
para o projeto ChargeGrid — não é uma tarifa real publicada pela GoodWe. A
documentação oficial do HCA G2 confirma que o carregador já expõe um valor
monetário calculado no próprio equipamento (registrador Modbus `10061`, "Charge
amount", disponível em modo de operação — ver `knowledge/modbus_rs485.md`),
o que mostra que aplicar uma política de tarifação sobre os dados do
carregador é compatível com o hardware real; os valores e regras abaixo, porém,
foram definidos para este projeto, não extraídos de um documento comercial da
GoodWe.

Esta política substitui a tarifa fixa única por uma estrutura de **postos
tarifários horários** (time-of-use), refletindo o custo real da energia ao
longo do dia — o mesmo princípo das tarifas branca/verde do setor elétrico
brasileiro, adaptado para o eletroposto comercial.

## Postos tarifários (horário local, todos os dias)

| Posto | Horário | Tarifa (R$/kWh) | Observação |
|---|---|---|---|
| Fora de ponta (madrugada) | 00:00–06:59 | R$ 0,55 | Tarifa mais baixa — incentiva recarga noturna |
| Fora de ponta (dia) | 07:00–17:59 | R$ 0,75 | Tarifa padrão diurna |
| **Ponta** | **18:00–20:59** | **R$ 1,65** | Horário de pico do sistema elétrico — tarifa mais alta |
| Fora de ponta (noite) | 21:00–23:59 | R$ 0,75 | Retorno à tarifa padrão |

Se o ciclo de recarga atravessar mais de um posto tarifário (ex.: início às
17:30 e fim às 19:00), o faturamento deve ser proporcional ao tempo/consumo em
cada posto — quando a conversa não trouxer dados suficientes para essa
proporção (consumo por sub-período), o assistente deve pedir o consumo
segmentado em vez de aplicar uma tarifa única arbitrariamente.

## Sobretaxa por excedente de demanda (Load Balancing negado)

Quando uma solicitação de potência é **negada** por exceder o limite da rede
(ver diretriz de Orquestração de Potência), não há faturamento de excedente —
a operação simplesmente não é autorizada. A sobretaxa de demanda só se aplica
a ciclos **já autorizados e concluídos** que, por telemetria (`MeterValues`
via OCPP), mostrarem picos de potência acima do contratado: nesse caso,
soma-se uma multa de 20% sobre o valor do ciclo inteiro, e o caso deve ser
sinalizado para auditoria humana antes de cobrar — o assistente não fecha essa
cobrança sozinho.

## Descontos e casos especiais

- **Recarga fora de ponta acima de 4 horas contínuas**: desconto de 10% sobre
  o total do ciclo (incentivo a uso em horário de baixa demanda).
- **Veículos de frota cadastrada (ID começando com "FROTA-")**: tarifa fixa
  preferencial de R$ 0,70/kWh independente do posto horário, conforme contrato
  comercial — essa regra sobrepõe a tabela de postos tarifários.

## Relação com o ChargeGrid Assistant

Ao calcular faturamento, o assistente deve: (1) identificar o horário do ciclo
(se informado) e aplicar o posto tarifário correto desta tabela em vez de uma
tarifa genérica; (2) aplicar a tarifa fixa de frota quando o ID do veículo
começar com "FROTA-"; (3) nunca aplicar a multa de excedente de demanda sem
que o operador tenha informado explicitamente uma leitura de potência acima do
contratado; (4) se a tarifa não puder ser determinada com segurança pelos
dados disponíveis, perguntar o horário do ciclo em vez de assumir um valor.
