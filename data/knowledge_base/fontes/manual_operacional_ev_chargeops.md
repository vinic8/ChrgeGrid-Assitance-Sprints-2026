# Manual Operacional ChargeGrid / EV ChargeOps

**Nota de proveniência**: manual operacional **ilustrativo** da plataforma
ChargeGrid / EV ChargeOps, elaborado para este projeto a partir da documentação
oficial do carregador GoodWe HCA G2 (manual de produto e mapa Modbus). Define
procedimentos de operação do eletroposto; não acrescenta especificações de
hardware. Especificações do carregador estão exclusivamente no "Manual de Produto
GoodWe HCA G2".

## 1. Perfis de acesso

A plataforma tem três perfis. O **Operador Comercial** acompanha as sessões,
autoriza mudanças de potência, registra ciclos e emite o faturamento. O
**Técnico de Campo** executa manutenção física, instalação e inspeção elétrica, e
é o único perfil autorizado a intervir no hardware. O **Auditor** consulta o
histórico de ciclos e aprova cobranças sinalizadas (sobretaxa de demanda,
contestações). O assistente ChargeGrid apoia o Operador Comercial e nunca executa
ações físicas.

## 2. Abertura de sessão de recarga

A sessão é aberta quando o veículo é autenticado por cartão RFID, pelo app ou por
início automático ao conectar. O operador deve confirmar que o status do
carregador (registrador 10017) passou de 01 (ocioso com plugue) para 02
(handshake) e depois para 03 (carregando). Se o status ficar em 02 por mais de 2
minutos, trata-se de timeout de handshake (registrador 10002, bit2): pedir ao
usuário para reconectar o plugue antes de qualquer outra ação.

## 3. Autorização de aumento de potência

Antes de autorizar um aumento de potência, o operador soma a potência atual de
todos os carregadores do mesmo circuito com o aumento pedido e compara com o
limite de rede daquele site (registrador 10026 ou 10039, ou o valor informado
pelo responsável da instalação). Se a soma exceder o limite, o pedido é negado e
o excedente em kW é registrado. Não existe limite padrão entre sites: sem o
limite do site, a autorização fica pendente até que ele seja informado.

## 4. Estratégia de Load Balancing

Quando o limite de rede não comporta um novo veículo, o procedimento padrão é
redistribuir a potência entre os carregadores ativos: reduzir proporcionalmente
os carregadores em curso para liberar a potência pedida, respeitando o mínimo de
4,2 kW por carregador ativo (mínimo do registrador Maximum Charging Power). Se
nem a redistribuição comportar o novo veículo, ele entra em fila e é atendido
quando um ciclo terminar. Veículos de frota ("FROTA-") têm prioridade na fila
apenas em contratos que prevejam isso.

## 5. Encerramento e registro do ciclo

No encerramento, o operador registra para auditoria: ID do veículo, ID do
carregador, horário de início, horário de fim, leitura inicial e final do medidor
(meterStart e meterStop), consumo em kWh e motivo do encerramento (registrador
10168). O registro do ciclo é obrigatório mesmo quando a tarifa ainda não foi
definida; nesse caso o faturamento fica pendente.

## 6. Classificação e escalonamento de alarmes

Os eventos são classificados em três níveis. **Nível 1 (operacional)**: alarmes do
registrador 10005, timeout de handshake e pausa de carregamento; o próprio
operador trata remotamente. **Nível 2 (comunicação)**: exceções Modbus 0x0001 a
0x0004 e perda de comunicação RS485; o operador segue o checklist de diagnóstico
do mapa Modbus e, se não resolver em 30 minutos, abre chamado técnico. **Nível 3
(segurança elétrica)**: falha de aterramento, curto-circuito na saída, falha de
corrente de fuga e sobretemperatura; a operação do carregador é interrompida
imediatamente e somente um técnico de campo habilitado pode religar o
equipamento, após inspeção presencial.

## 7. Auditoria e contestação de cobrança

Toda cobrança contestada pelo usuário é congelada e enviada ao Auditor com o
registro completo do ciclo. O prazo de resposta a uma contestação é de 5 dias
úteis. A sobretaxa de demanda (tabelas tarifárias, seção 5) sempre passa por
aprovação do Auditor antes de ser cobrada.

## 8. Limites do assistente

O assistente ChargeGrid calcula, registra, explica e recomenda. Ele não processa
pagamentos (a cobrança passa pelo gateway financeiro da operação), não libera
religamento após alarme de Nível 3 e não orienta intervenção física no
carregador: nesses casos indica qual perfil acionar (Técnico de Campo ou
Auditor).
