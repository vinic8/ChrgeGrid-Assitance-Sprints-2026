"""Memória conversacional por sessão: `ConversationSummaryBufferMemory` (LangChain).

Requisito obrigatório do desafio: a classe oficial do LangChain
(`langchain_classic.memory.ConversationSummaryBufferMemory`), aceitando o aviso de
depreciação — está descontinuada rumo à remoção no LangChain 2.0 (movida para
`langchain_classic`; o próprio time do LangChain recomenda
`RunnableWithMessageHistory`/checkpointing como substituto) — em troca de aderência
literal ao requisito.

Detalhe de integração: `ConversationSummaryBufferMemory.prune()` conta tokens via
`self.llm.get_num_tokens_from_messages(...)`. Nem `ChatOllama` nem `ChatGroq` têm
tokenizer próprio, então isso cai no fallback padrão do LangChain, que exige o pacote
`transformers` (tokenizer GPT-2 baixado da internet na primeira chamada) — uma
dependência pesada e com acesso de rede que o projeto evita deliberadamente em todo o
resto (`src/tokens.py` usa `tiktoken`, local, e o FastEmbed do RAG foi escolhido por
não precisar de API/download externo). `_MemoriaChargeGrid` abaixo é a mesma
`ConversationSummaryBufferMemory` exigida — só troca a contagem de tokens do
`prune()` por `contar_tokens` (tiktoken), mantendo o resto do comportamento herdado
sem alteração.
"""
from __future__ import annotations

from langchain_classic.memory import ConversationSummaryBufferMemory
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.prompts import PromptTemplate

from src.tokens import contar_tokens


class _MemoriaChargeGrid(ConversationSummaryBufferMemory):
    """`ConversationSummaryBufferMemory` com contagem de tokens via tiktoken."""

    def _tokens_do_buffer(self, buffer: list[BaseMessage]) -> int:
        return sum(contar_tokens(str(m.content)) for m in buffer)

    def prune(self) -> None:
        buffer = self.chat_memory.messages
        curr_buffer_length = self._tokens_do_buffer(buffer)
        if curr_buffer_length > self.max_token_limit:
            pruned_memory = []
            while curr_buffer_length > self.max_token_limit:
                pruned_memory.append(buffer.pop(0))
                curr_buffer_length = self._tokens_do_buffer(buffer)
            self.moving_summary_buffer = self.predict_new_summary(
                pruned_memory, self.moving_summary_buffer
            )

    async def aprune(self) -> None:
        buffer = self.chat_memory.messages
        curr_buffer_length = self._tokens_do_buffer(buffer)
        if curr_buffer_length > self.max_token_limit:
            pruned_memory = []
            while curr_buffer_length > self.max_token_limit:
                pruned_memory.append(buffer.pop(0))
                curr_buffer_length = self._tokens_do_buffer(buffer)
            self.moving_summary_buffer = await self.apredict_new_summary(
                pruned_memory, self.moving_summary_buffer
            )

_PROMPT_RESUMO = PromptTemplate(
    input_variables=["summary", "new_lines"],
    template="""Resuma progressivamente a conversa abaixo entre um Operador Comercial \
de eletropostos GoodWe e o ChargeGrid Assistant. Preserve fatos operacionais relevantes \
(IDs de carregadores e veículos, potências, limites de rede, valores/tarifas de \
faturamento, decisões já tomadas) e descarte saudações ou conversa fiada. Seja conciso \
(no máximo 5 frases), em português.

Resumo atual:
{summary}

Novas linhas da conversa:
{new_lines}

Novo resumo:""",
)

_SESSOES: dict[str, ConversationSummaryBufferMemory] = {}


def obter_historico(session_id: str, limite_tokens: int, llm: BaseChatModel) -> ConversationSummaryBufferMemory:
    """Memória da sessão: uma `ConversationSummaryBufferMemory` por `session_id`.

    `llm` é (re)atribuído a cada chamada, não só na criação, porque o operador pode
    trocar de provider/modelo no meio da mesma sessão (seletor multi-provider da UI) —
    essa classe usa `llm` tanto para contar tokens (`get_num_tokens_from_messages`,
    cálculo local, sem chamada de rede) quanto para gerar o resumo quando o buffer
    ultrapassa `max_token_limit` (aí sim uma chamada real ao modelo).
    """
    memoria = _SESSOES.get(session_id)
    if memoria is None:
        memoria = _MemoriaChargeGrid(
            llm=llm,
            prompt=_PROMPT_RESUMO,
            max_token_limit=limite_tokens,
            return_messages=True,
        )
        _SESSOES[session_id] = memoria
    else:
        memoria.llm = llm
        memoria.max_token_limit = limite_tokens
    return memoria


def mensagens_para_prompt(memoria: ConversationSummaryBufferMemory) -> list[BaseMessage]:
    """Histórico efetivo enviado à chain: resumo (se houver) + cauda literal.

    `load_memory_variables` já devolve isso pronto quando `return_messages=True`:
    o resumo vira um `SystemMessage` prefixado às mensagens literais mantidas no
    buffer (ver `ConversationSummaryBufferMemory.load_memory_variables`).
    """
    return memoria.load_memory_variables({})[memoria.memory_key]


def total_tokens(memoria: ConversationSummaryBufferMemory) -> int:
    """Tokens (aproximação via tiktoken, `src/tokens.py`) do histórico efetivo atual."""
    return sum(contar_tokens(str(m.content)) for m in mensagens_para_prompt(memoria))


def registrar_turno(memoria: ConversationSummaryBufferMemory, entrada: str, resposta: str) -> None:
    """Adiciona o turno e, se necessário, resume a parte mais antiga (`save_context`
    já aciona `prune()` internamente — ver `ConversationSummaryBufferMemory.save_context`).
    """
    memoria.save_context({"input": entrada}, {"output": resposta})


def obter_sessao_existente(session_id: str) -> ConversationSummaryBufferMemory | None:
    """Memória já criada da sessão, sem instanciar uma nova (nem exigir `llm`).

    Usado pela UI só para exibir estatísticas (tokens, resumo) no expander
    "Avançado" antes do primeiro turno — nesse ponto ainda não há motivo pra
    montar um `llm` só para popular o campo obrigatório de `obter_historico`.
    """
    return _SESSOES.get(session_id)


def limpar_sessao(session_id: str) -> None:
    _SESSOES.pop(session_id, None)
