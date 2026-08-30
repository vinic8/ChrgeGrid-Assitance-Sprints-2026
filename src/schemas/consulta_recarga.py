"""Schema Pydantic v2 do domínio EV — saída estruturada do ChargeGrid Assistant.

Este é o contrato entre o LLM e o resto do sistema (UI, eval, auditoria). A chain
LCEL (src/chain/builder.py) usa `PydanticOutputParser(pydantic_object=ConsultaRecarga)`
como último passo do pipe (`prompt | llm | parser`), então qualquer resposta que não
caiba neste schema falha a validação (com uma tentativa de correção automática antes
de desistir — ver `_parse_com_correcao`), em vez de silenciosamente virar texto solto.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class Decisao(str, Enum):
    AUTORIZADO = "autorizado"
    NEGADO = "negado"
    NAO_APLICAVEL = "nao_aplicavel"  # pergunta não envolve decisão de potência/faturamento


class ConsultaRecarga(BaseModel):
    """Estado de uma consulta de recarga: potência, faturamento e decisão do assistente."""

    carregador_id: str | None = Field(
        default=None,
        description="Identificador do carregador (ex.: 'C05'). None se não informado.",
    )
    veiculo_id: str | None = Field(
        default=None,
        description="Identificador do veículo/sessão de recarga, para auditoria.",
    )
    inicio_sessao: str | None = Field(
        default=None,
        description="Horário de início do ciclo de recarga, como informado na conversa.",
    )
    fim_sessao: str | None = Field(
        default=None,
        description="Horário de fim do ciclo de recarga, como informado na conversa.",
    )
    potencia_solicitada_kw: float | None = Field(
        default=None,
        ge=0,
        description="Potência que o operador quer liberar, em kW.",
    )
    limite_rede_kw: float | None = Field(
        default=None,
        ge=0,
        description="Limite de potência da rede local informado na conversa, em kW.",
    )
    consumo_kwh: float | None = Field(
        default=None,
        ge=0,
        description="Consumo do ciclo de recarga, em kWh, para fins de faturamento.",
    )
    tarifa_reais_kwh: float | None = Field(
        default=None,
        ge=0,
        description="Tarifa vigente, em R$/kWh.",
    )
    total_faturado_reais: float | None = Field(
        default=None,
        ge=0,
        description="consumo_kwh * tarifa_reais_kwh, quando ambos estiverem disponíveis.",
    )
    decisao: Decisao = Field(
        description="Resultado da checagem de orquestração de potência.",
    )
    excedente_kw: float | None = Field(
        default=None,
        description="Se decisao=negado, quanto (em kW) excede o limite da rede.",
    )
    justificativa: str = Field(
        min_length=1,
        max_length=1500,
        description="Explicação técnica curta e direta da decisão, no tom do ChargeGrid Assistant.",
    )

    @field_validator("justificativa")
    @classmethod
    def justificativa_nao_vazia(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("justificativa não pode ser vazia")
        return v

    @model_validator(mode="after")
    def coerencia_decisao_excedente(self) -> "ConsultaRecarga":
        if self.decisao == Decisao.NEGADO and self.potencia_solicitada_kw is not None and self.limite_rede_kw is not None:
            calculado = round(self.potencia_solicitada_kw - self.limite_rede_kw, 3)
            if calculado > 0 and self.excedente_kw is None:
                # normaliza em vez de falhar: o LLM às vezes esquece de repetir o número
                # que já dá para calcular a partir dos outros dois campos.
                self.excedente_kw = calculado
        if self.consumo_kwh is not None and self.tarifa_reais_kwh is not None and self.total_faturado_reais is None:
            self.total_faturado_reais = round(self.consumo_kwh * self.tarifa_reais_kwh, 2)
        return self
