# FAQ de Carregamento — eletropostos GoodWe ChargeGrid

**Nota de proveniência**: perguntas frequentes **ilustrativas** elaboradas para o
projeto ChargeGrid, consolidando o manual de produto GoodWe HCA G2, o mapa Modbus,
as tabelas tarifárias e o manual operacional. Em caso de divergência, prevalece o
documento de origem.

## 1. Quanto tempo leva uma recarga completa?

Depende da capacidade da bateria do veículo e da potência do carregador. Como
referência de cálculo, o tempo aproximado é a energia a recarregar dividida pela
potência efetiva: 33 kWh num carregador de 11 kW levam cerca de 3 horas. A
potência efetiva também é limitada pelo carregador de bordo do próprio veículo e
pelo controle de carga dinâmico do site.

## 2. Meu veículo é compatível com o carregador GoodWe HCA G2?

O HCA G2 usa conector IEC Tipo 2 com cabo de 6 m (7,5 m opcional). Veículos com
entrada Tipo 2 conectam diretamente. Veículos com outros padrões de entrada
precisam de adaptador certificado pelo fabricante do veículo.

## 3. Por que minha recarga está mais lenta do que o esperado?

As causas mais comuns são: o controle de carga dinâmico reduziu a potência para
não ultrapassar o limite de rede do site; o carregador de bordo do veículo aceita
menos potência que o carregador oferece; ou o modo de operação está em
Prioridade solar, que acompanha a geração fotovoltaica disponível.

## 4. Como é calculado o valor da minha recarga?

No eletroposto comercial, o valor é o consumo em kWh (meterStop menos meterStart)
multiplicado pela tarifa do posto horário em que a recarga ocorreu, conforme as
tabelas tarifárias. Veículos de frota cadastrada têm tarifa fixa. Em condomínios,
vale o rateio definido no regimento condominial.

## 5. Posso deixar o carro conectado depois que a carga terminar?

No eletroposto comercial há 15 minutos de tolerância após o fim da carga; depois
disso é cobrada a tarifa de ocupação ociosa. Em condomínio, o veículo deve ser
retirado em até 30 minutos, sob pena de advertência e multa previstas no
regimento.

## 6. A recarga é segura na chuva?

Sim. O carregador tem grau de proteção IP66 e o plugue IP55, e o equipamento pode
ser instalado em ambiente externo. Não manuseie o plugue com as mãos molhadas e
não use o carregador se o cabo estiver danificado.

## 7. O carregador mostrou um alarme. O que faço?

Alarmes leves (registrador 10005) não interrompem a carga e podem ser
acompanhados pelo app. Se a carga parou com falha, verifique se o plugue está bem
encaixado e tente reiniciar a sessão. Alarmes de falha de aterramento, fuga de
corrente ou curto-circuito exigem desligar o carregador e acionar um técnico
habilitado; não tente religar por conta própria.

## 8. Posso carregar usando energia solar?

Sim, quando o site tem sistema fotovoltaico GoodWe integrado. O HCA G2 tem os
modos Prioridade solar e PV + bateria, que priorizam a energia gerada localmente.
Se a geração for insuficiente, a carga pode ser interrompida (status 10 do
registrador 10017) até a geração voltar.

## 9. Como contestar uma cobrança?

Abra a contestação pelo app ou com o operador do eletroposto informando o ID do
veículo, o carregador e o horário do ciclo. A cobrança fica congelada e o auditor
responde em até 5 dias úteis.
