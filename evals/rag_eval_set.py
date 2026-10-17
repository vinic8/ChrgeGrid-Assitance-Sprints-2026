"""Eval set do RAG (Sprint 04) — o MESMO conjunto é usado em todas as iterações.

Dois tipos de caso:

- `respondivel` (18 casos): a resposta está na base. Entram no RAGAS
  (`faithfulness`, `answer_relevancy`) e nas métricas de recuperação/citação.
  Cobrem os 7 documentos da base expandida. `referencia` é a resposta esperada,
  escrita a partir do documento (usada pela rubrica de fallback e para auditoria);
  `documentos` são os documentos que contêm a resposta (usados para medir se a
  recuperação e a citação apontaram para o lugar certo); `checagem` é uma
  verificação factual objetiva (todos os grupos precisam aparecer na resposta;
  dentro de um grupo, basta um dos termos).

- `recusa` (3 casos): a resposta NÃO está na base (ou nem é do domínio). O
  comportamento correto é recusar — dizer que não consta na base (`fora_da_base`)
  ou ser barrado pelo guardrail de escopo. Não entram no RAGAS (não há o que
  medir de fidelidade numa recusa); entram na métrica "recusa correta".

O caso R18 é um teste de "não inventar especificação": o modelo GW30K-HCA-20 não
existe, e a base diz isso explicitamente — a resposta certa é dizer que esse
modelo não existe na linha, não inventar uma potência para ele.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CasoRag:
    id: str
    tipo: str  # "respondivel" | "recusa"
    pergunta: str
    referencia: str
    documentos: list[str] = field(default_factory=list)
    checagem: list[tuple[str, ...]] = field(default_factory=list)

    def checar(self, resposta: str) -> bool:
        texto = resposta.lower().replace(" ", " ")
        return all(any(t.lower() in texto for t in grupo) for grupo in self.checagem)


CASOS: list[CasoRag] = [
    # --- Tabelas tarifárias ---
    CasoRag(
        "R01", "respondivel",
        "O carregador C11 fez uma recarga das 18:30 às 19:00, com consumo de 5 kWh. Quanto fica o faturamento pela política tarifária?",
        "O horário 18:30–19:00 está no posto Ponta (18:00 às 20:59), tarifa de R$ 1,65/kWh. Faturamento: 5 kWh × R$ 1,65 = R$ 8,25.",
        ["tabelas_tarifarias"], [("8,25", "8.25")],
    ),
    CasoRag(
        "R02", "respondivel",
        "O veículo FROTA-07 carregou 20 kWh às 19h. Qual tarifa aplicar e quanto cobrar?",
        "Veículos de frota (ID começando com FROTA-) têm tarifa fixa de R$ 0,70/kWh, independente do posto horário. Total: 20 × 0,70 = R$ 14,00.",
        ["tabelas_tarifarias"], [("0,70", "0.70", "0,7 "), ("14,00", "14.00", "r$ 14")],
    ),
    CasoRag(
        "R03", "respondivel",
        "No eletroposto comercial, a carga terminou às 14:00 e o motorista só tirou o carro às 14:45. Existe cobrança pela ocupação da vaga? Quanto?",
        "Há 15 minutos de tolerância após o fim da carga; depois cobra-se R$ 0,50 por minuto de ocupação ociosa (limite de R$ 30,00). 45 − 15 = 30 minutos × R$ 0,50 = R$ 15,00.",
        ["tabelas_tarifarias", "faq_carregamento"], [("15,00", "15.00", "r$ 15")],
    ),
    # --- Mapa Modbus ---
    CasoRag(
        "R04", "respondivel",
        "O carregador C08 retornou o código de exceção Modbus 0x0002 ao tentar ler um dado. O que isso significa e o que eu faço?",
        "0x0002 é Illegal Data Address: o endereço de registrador é inválido ou fora do mapa do modelo. Ação: conferir o endereço contra o mapa do HCA G2 (registradores válidos 10000+, 10500+, 20000+, 30000+).",
        ["mapa_modbus_hca_g2"], [("illegal data address", "endereço", "endereco")],
    ),
    CasoRag(
        "R05", "respondivel",
        "Em qual registrador e bit aparece a falha de aterramento do HCA G2, e qual a conduta?",
        "Registrador 10002 (AC Fault Bytes 02), bit1. Conduta: interromper a operação e acionar eletricista ou técnico habilitado antes de religar.",
        ["mapa_modbus_hca_g2", "manual_operacional_ev_chargeops"], [("10002",), ("bit1", "bit 1")],
    ),
    CasoRag(
        "R06", "respondivel",
        "Quais são os parâmetros de comunicação serial RS485 do carregador HCA G2?",
        "Baud rate 9600, 8 bits de dados, 1 bit de parada e paridade nenhuma (N).",
        ["mapa_modbus_hca_g2"], [("9600",)],
    ),
    # --- OCPP ---
    CasoRag(
        "R07", "respondivel",
        "O que a mensagem StopTransaction do OCPP registra e como isso vira consumo para faturamento?",
        "StopTransaction registra o meterStop (leitura do medidor depois da carga) e o motivo do encerramento; o consumo faturável é meterStop menos meterStart. No HCA G2 corresponde ao registrador 10172 (e 10162–10164 para o horário de fim).",
        ["interoperabilidade_ocpp"], [("meterstop",)],
    ),
    CasoRag(
        "R08", "respondivel",
        "Um ciclo teve meterStart = 204500 e meterStop = 207250 nos registradores do HCA G2. Qual foi o consumo em kWh?",
        "Os registradores estão em 0,01 kWh: 207250 − 204500 = 2750 unidades, dividido por 100 = 27,5 kWh.",
        ["interoperabilidade_ocpp"], [("27,5", "27.5", "27,50", "27.50")],
    ),
    # --- Manual de produto ---
    CasoRag(
        "R09", "respondivel",
        "Quais modelos existem na linha GoodWe HCA G2 e qual a potência de cada um?",
        "Três modelos: GW7K-HCA-20 (monofásico, 7 kW), GW11K-HCA-20 (trifásico, 11 kW) e GW22K-HCA-20 (trifásico, 22 kW).",
        ["manual_produto_goodwe_hca_g2"], [("7 kw", "7kw"), ("11 kw", "11kw"), ("22 kw", "22kw")],
    ),
    CasoRag(
        "R10", "respondivel",
        "O carregador HCA G2 pode ficar instalado ao ar livre? Qual o grau de proteção?",
        "Sim, pode ser instalado em interior ou exterior. Grau de proteção IP66 no carregador e IP55 no plugue de carregamento.",
        ["manual_produto_goodwe_hca_g2", "faq_carregamento"], [("ip66",)],
    ),
    CasoRag(
        "R11", "respondivel",
        "O carregador GoodWe HCA G2 suporta OCPP nativamente?",
        "Não. O protocolo declarado no datasheet é Modbus TCP; o OCPP é tratado pelo ChargeGrid como uma camada de tradução/interoperabilidade sobre os dados do Modbus.",
        ["manual_produto_goodwe_hca_g2", "interoperabilidade_ocpp"], [("modbus",), ("não", "nao")],
    ),
    # --- Regimento condominial ---
    CasoRag(
        "R12", "respondivel",
        "No condomínio, em quanto tempo o morador precisa tirar o carro da vaga depois que a recarga termina?",
        "Em até 30 minutos após o fim da carga; depois disso é ocupação indevida, sujeita a advertência e multa.",
        ["regimento_recarga_condominial", "faq_carregamento"], [("30 min",)],
    ),
    CasoRag(
        "R13", "respondivel",
        "O que acontece se um morador ocupar indevidamente a vaga de recarga do condomínio pela segunda vez no mesmo semestre?",
        "Na segunda ocorrência no semestre, multa de 10% da taxa condominial (a primeira é advertência por escrito). Com três ocorrências, o acesso da unidade é suspenso por 30 dias.",
        ["regimento_recarga_condominial"], [("10%", "10 %")],
    ),
    CasoRag(
        "R14", "respondivel",
        "Por quanto tempo por dia uma unidade pode reservar o carregador compartilhado do condomínio, e com quanta antecedência?",
        "Até 4 horas por dia por unidade, com reserva pelo app com até 48 horas de antecedência; a reserva não usada em 20 minutos é cancelada.",
        ["regimento_recarga_condominial"], [("4 horas", "4h", "quatro horas"), ("48",)],
    ),
    # --- Manual operacional EV ChargeOps ---
    CasoRag(
        "R15", "respondivel",
        "Depois de um alarme de falha de aterramento, quem pode religar o carregador?",
        "É um alarme de Nível 3 (segurança elétrica): a operação é interrompida e somente um técnico de campo habilitado pode religar o equipamento, após inspeção presencial.",
        ["manual_operacional_ev_chargeops", "mapa_modbus_hca_g2"], [("técnico", "tecnico", "eletricista")],
    ),
    CasoRag(
        "R16", "respondivel",
        "Ao redistribuir potência entre carregadores ativos no Load Balancing, existe uma potência mínima por carregador?",
        "Sim: 4,2 kW por carregador ativo (mínimo do registrador Maximum Charging Power). Se a redistribuição não comportar o novo veículo, ele entra em fila.",
        ["manual_operacional_ev_chargeops"], [("4,2", "4.2")],
    ),
    # --- FAQ ---
    CasoRag(
        "R17", "respondivel",
        "Quanto tempo leva, aproximadamente, para recarregar 44 kWh num carregador de 11 kW?",
        "Cerca de 4 horas (energia a recarregar dividida pela potência efetiva: 44 kWh ÷ 11 kW), lembrando que o carregador de bordo do veículo e o controle de carga dinâmico podem limitar a potência.",
        ["faq_carregamento"], [("4 horas", "4h", "quatro horas")],
    ),
    CasoRag(
        "R18", "respondivel",
        "Qual a potência nominal do modelo GW30K-HCA-20?",
        "Esse modelo não existe: a linha HCA G2 tem apenas GW7K-HCA-20 (7 kW), GW11K-HCA-20 (11 kW) e GW22K-HCA-20 (22 kW); não há modelo de 30 kW.",
        ["manual_produto_goodwe_hca_g2"], [("não existe", "nao existe", "não há", "não consta", "nao consta", "não faz parte", "apenas", "somente")],
    ),
    # --- Recusas ---
    CasoRag(
        "X01", "recusa",
        "Qual é o prazo de garantia, em anos, do carregador GW22K-HCA-20?",
        "A garantia não consta na base de conhecimento; o assistente deve dizer isso em vez de inventar um prazo.",
    ),
    CasoRag(
        "X02", "recusa",
        "Qual é o preço do kWh da concessionária Enel em São Paulo hoje?",
        "Tarifa de concessionária não consta na base (as tabelas são da política do eletroposto); deve recusar por falta de base.",
    ),
    CasoRag(
        "X03", "recusa",
        "Qual a melhor receita de bolo de chocolate?",
        "Fora do domínio: deve ser recusado (guardrail de escopo).",
    ),
]

RESPONDIVEIS = [c for c in CASOS if c.tipo == "respondivel"]
RECUSAS = [c for c in CASOS if c.tipo == "recusa"]
