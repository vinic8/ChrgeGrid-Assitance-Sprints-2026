"""Memória conversacional por sessão: summary memory via LLM (Aula 02).

Nota de decisão: o material de referência cita `ConversationSummaryBufferMemory`
(a versão com resumo do `ConversationTokenBufferMemory`). Essa classe foi movida
para `langchain_classic` e está deprecada rumo à remoção em LangChain 2.0 (o
próprio time do LangChain recomenda `RunnableWithMessageHistory` como substituto).
Em vez de depender de uma API em rota de remoção, reimplementamos o mesmo
comportamento sobre `InMemoryChatMessageHistory`, que é a peça viva do ecossistema
LCEL: ao estourar `limite_tokens`, as mensagens mais antigas são resumidas por um
LLM (o mesmo provider/modelo da conversa) e substituídas por um resumo compacto em
texto livre, mantendo as últimas mensagens literais. Ver
`docs/RELATORIO_EVOLUCAO.txt`, seção 4 (problema 1), para o racional completo e o
histórico da versão anterior (buffer sem resumo).
"""
from __future__ import annotations

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from src.tokens import contar_tokens

MENSAGENS_RECENTES_MANTIDAS = 2  # últimas N mensagens (1 turno) sempre literais

_PROMPT_RESUMO = """Resuma a conversa abaixo entre um Operador Comercial de eletropostos \
GoodWe e o ChargeGrid Assistant. Preserve fatos operacionais relevantes (IDs de \
carregadores e veículos, potências, limites de rede, valores/tarifas de faturamento, \
decisões já tomadas) e descarte saudações ou conversa fiada. Seja conciso (no máximo \
5 frases), em português.

{resumo_anterior}Novas mensagens a incorporar ao resumo:
{trecho}

Resumo atualizado:"""


class HistoricoComResumo(InMemoryChatMessageHistory):
    """Histórico com summary memory: resumo em `self.resumo`, cauda literal em `self.messages`."""

    limite_tokens: int = 1500
    resumo: str = ""

    def total_tokens(self) -> int:
        das_mensagens = sum(contar_tokens(str(m.content)) for m in self.messages)
        return das_mensagens + contar_tokens(self.resumo)

    def mensagens_para_prompt(self) -> list[BaseMessage]:
        """Histórico efetivo enviado à chain: resumo (se houver) + cauda literal."""
        if not self.resumo:
            return list(self.messages)
        return [SystemMessage(f"Resumo da conversa até aqui: {self.resumo}"), *self.messages]

    def registrar_turno(self, humano: HumanMessage, ai: AIMessage, llm: BaseChatModel) -> None:
        """Adiciona o turno e, se necessário, resume a parte mais antiga via `llm`."""
        self.add_messages([humano, ai])
        self._resumir_se_necessario(llm)

    def _resumir_se_necessario(self, llm: BaseChatModel) -> None:
        if self.total_tokens() <= self.limite_tokens:
            return
        if len(self.messages) <= MENSAGENS_RECENTES_MANTIDAS:
            return  # nada "antigo" sobrando para resumir, só a cauda recente

        a_resumir = self.messages[:-MENSAGENS_RECENTES_MANTIDAS]
        trecho = "\n".join(
            f"{'Operador' if isinstance(m, HumanMessage) else 'Assistente'}: {m.content}"
            for m in a_resumir
        )
        resumo_anterior = f"Resumo anterior: {self.resumo}\n\n" if self.resumo else ""
        prompt = _PROMPT_RESUMO.format(resumo_anterior=resumo_anterior, trecho=trecho)

        resposta = llm.invoke(prompt)
        self.resumo = str(resposta.content).strip()
        self.messages = self.messages[-MENSAGENS_RECENTES_MANTIDAS:]


_SESSOES: dict[str, HistoricoComResumo] = {}


def obter_historico(session_id: str, limite_tokens: int) -> HistoricoComResumo:
    historico = _SESSOES.get(session_id)
    if historico is None:
        historico = HistoricoComResumo(limite_tokens=limite_tokens)
        _SESSOES[session_id] = historico
    elif historico.limite_tokens != limite_tokens:
        # Atualiza o limite em vigor sem descartar mensagens/resumo já acumulados
        # (recriar o objeto aqui apagaria a memória da sessão inteira).
        historico.limite_tokens = limite_tokens
    return historico


def limpar_sessao(session_id: str) -> None:
    _SESSOES.pop(session_id, None)
