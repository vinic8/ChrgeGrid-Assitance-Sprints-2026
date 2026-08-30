"""Núcleo conversacional em LCEL: prompt | llm | parser.

Este é o coração do refactory da Sprint 03. Comparar com `src/manual_chat.py`,
que reproduz a versão manual das Sprints 1/2 (f-strings + histórico concatenado à
mão, sem schema, sem guardrail).

Multi-provider (Bloco B): a mesma chain roda sobre dois providers diferentes,
selecionados por `provider`:
- **Provider A** — Ollama Cloud, modelo `MODEL_PRIMARY` (default `gpt-oss:120b-cloud`).
- **Provider B** — Groq, modelo `MODEL_GROQ` (default `qwen/qwen3.8-27b`). O plano
  era reintroduzir o Llama 3.3 (Sprints 1/2) via Groq, mas ele foi descontinuado
  nesse provider; `qwen/qwen3.8-27b` é a alternativa open-weight que respondeu de
  forma limpa nos testes (ver `docs/RELATORIO_EVOLUCAO.txt`, nota "Mudança de
  provider").
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from src.chain.memoria import obter_historico
from src.config import extract_system_prompt_body, load_settings
from src.guardrails.moderation import MENSAGEM_RECUSA_PADRAO, checar_jailbreak
from src.guardrails.scope_validator import checar_escopo
from src.rag.indexer import formatar_contexto, obter_retriever
from src.schemas import ConsultaRecarga, Decisao
from src.tokens import contar_tokens

_parser = PydanticOutputParser(pydantic_object=ConsultaRecarga)

PROVIDERS = {
    "ollama": "Provider A — Ollama Cloud",
    "groq": "Provider B — Groq",
}


@dataclass
class RespostaChat:
    resultado: ConsultaRecarga
    latencia_s: float
    tokens_entrada: int
    tokens_saida: int
    bloqueado_por_guardrail: bool
    fontes_rag: list[str] = None  # docs de knowledge/ usados nesta resposta (vazio se bloqueado por guardrail)

    def __post_init__(self):
        if self.fontes_rag is None:
            self.fontes_rag = []


def modelo_padrao(provider: str, settings=None) -> str:
    """Modelo default de cada provider, conforme o .env."""
    settings = settings or load_settings()
    return settings.model_groq if provider == "groq" else settings.model_primary


_TIMEOUT_S = 90  # nenhum dos dois providers tinha timeout - uma chamada trava sem
# resposta prende a UI/eval indefinidamente (achado real: compare_models.py ficou
# >20min parado numa unica chamada Groq durante o desenvolvimento).


def _montar_llm(model: str | None = None, provider: str = "ollama") -> BaseChatModel:
    settings = load_settings()
    if provider == "groq":
        return ChatGroq(
            model=model or settings.model_groq,
            api_key=settings.groq_api_key,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            request_timeout=_TIMEOUT_S,
        )
    return ChatOllama(
        model=model or settings.model_primary,
        base_url=settings.ollama_host,
        temperature=settings.temperature,
        num_predict=settings.max_tokens,
        client_kwargs={
            "headers": {"Authorization": f"Bearer {settings.ollama_api_key}"},
            "timeout": _TIMEOUT_S,
        },
    )


def _resposta_bloqueio(justificativa: str) -> ConsultaRecarga:
    return ConsultaRecarga(decisao=Decisao.NAO_APLICAVEL, justificativa=justificativa)


def construir_chain(llm: BaseChatModel):
    """Monta a chain LCEL `retrieval | prompt | llm | parser` em torno de um LLM já
    instanciado.

    `RunnablePassthrough.assign(contexto_tecnico=...)` é o passo de RAG: recupera
    os chunks mais relevantes da base de conhecimento (`knowledge/*.md`, indexada
    em FAISS por `src/rag/indexer.py`) para a pergunta atual e os injeta no prompt
    como `<base_de_conhecimento>`, antes do LLM ver a pergunta. Sem isso, o modelo
    "inventaria" códigos de erro Modbus/OCPP ou aplicaria uma tarifa fixa genérica
    em vez da política de tarifação dinâmica real.

    O último passo (`RunnableLambda(_parse_com_correcao)`) é o "parser": tenta
    validar contra `ConsultaRecarga` e, se a primeira tentativa vier malformada
    (comum quando o modelo não segue o JSON à risca), pede uma correção pontual
    ao próprio LLM antes de desistir. Ver docs/RELATORIO_EVOLUCAO.txt, seção 4
    (problema 2).
    """
    settings = load_settings()
    system_prompt = extract_system_prompt_body(settings.system_prompt_path)
    retriever = obter_retriever(k=6)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt + "\n\n{format_instructions}"),
            ("system", "<base_de_conhecimento>\n{contexto_tecnico}\n</base_de_conhecimento>"),
            MessagesPlaceholder("historico"),
            ("human", "{entrada}"),
        ]
    ).partial(format_instructions=_parser.get_format_instructions())

    def _recuperar(inputs: dict) -> str:
        documentos = retriever.invoke(inputs["entrada"])
        return formatar_contexto(documentos)

    def _parse_com_correcao(ai_message: AIMessage) -> ConsultaRecarga:
        texto = ai_message.content
        try:
            return _parser.parse(texto)
        except Exception as primeiro_erro:  # noqa: BLE001 - queremos capturar qualquer falha de parsing
            prompt_correcao = (
                "A saída abaixo deveria ser um JSON válido conforme as instruções de "
                f"formato, mas falhou na validação com o erro: {primeiro_erro}\n\n"
                f"Instruções de formato:\n{_parser.get_format_instructions()}\n\n"
                f"Saída original:\n{texto}\n\n"
                "Responda APENAS com o JSON corrigido, sem texto adicional."
            )
            correcao = llm.invoke(prompt_correcao)
            return _parser.parse(correcao.content)

    etapa_rag = RunnablePassthrough.assign(contexto_tecnico=RunnableLambda(_recuperar))
    return etapa_rag | prompt | llm | RunnableLambda(_parse_com_correcao)


def recuperar_fontes(entrada: str, k: int = 6) -> list[str]:
    """Nomes dos documentos de `knowledge/` usados para responder `entrada`.

    Chamado separadamente de `construir_chain` (que já recupera o mesmo contexto
    internamente) só para expor a proveniência ao chamador (UI/eval) sem precisar
    remodelar o retorno da chain — o custo de recuperar 2x é irrelevante (busca
    vetorial local em milissegundos).
    """
    documentos = obter_retriever(k).invoke(entrada)
    vistos: list[str] = []
    for doc in documentos:
        fonte = doc.metadata.get("fonte", "?")
        if fonte not in vistos:
            vistos.append(fonte)
    return vistos


def conversar(
    session_id: str,
    entrada: str,
    model: str | None = None,
    provider: str = "ollama",
    ignorar_guardrails: bool = False,
) -> RespostaChat:
    """Ponto de entrada usado pela UI Streamlit e pelo eval harness.

    Faz a checagem de guardrails (barata, sem chamar o LLM) e só então invoca
    a chain LCEL. Em qualquer um dos dois caminhos, atualiza a memória da sessão
    (`registrar_turno`, que também aciona o resumo automático quando o histórico
    estoura `MEMORIA_LIMITE_TOKENS`) para que o próximo turno tenha o contexto certo.
    """
    settings = load_settings()
    historico = obter_historico(session_id, settings.memoria_limite_tokens)
    llm = _montar_llm(model, provider)
    inicio = time.perf_counter()

    if not ignorar_guardrails:
        moderacao = checar_jailbreak(entrada)
        if not moderacao.seguro:
            resultado = _resposta_bloqueio(MENSAGEM_RECUSA_PADRAO)
            historico.registrar_turno(HumanMessage(entrada), AIMessage(resultado.justificativa), llm)
            return RespostaChat(
                resultado=resultado,
                latencia_s=time.perf_counter() - inicio,
                tokens_entrada=contar_tokens(entrada),
                tokens_saida=contar_tokens(resultado.justificativa),
                bloqueado_por_guardrail=True,
            )

        escopo = checar_escopo(entrada)
        if not escopo.dentro_do_escopo:
            resultado = _resposta_bloqueio(
                f"{escopo.motivo} Posso ajudar com orquestração de potência, faturamento "
                "ou diagnóstico de carregadores GoodWe."
            )
            historico.registrar_turno(HumanMessage(entrada), AIMessage(resultado.justificativa), llm)
            return RespostaChat(
                resultado=resultado,
                latencia_s=time.perf_counter() - inicio,
                tokens_entrada=contar_tokens(entrada),
                tokens_saida=contar_tokens(resultado.justificativa),
                bloqueado_por_guardrail=True,
            )

    tokens_contexto_previo = historico.total_tokens()  # contexto que será realmente enviado ao LLM

    chain = construir_chain(llm)
    resultado: ConsultaRecarga = chain.invoke(
        {"entrada": entrada, "historico": historico.mensagens_para_prompt()}
    )

    historico.registrar_turno(HumanMessage(entrada), AIMessage(resultado.justificativa), llm)

    return RespostaChat(
        resultado=resultado,
        latencia_s=time.perf_counter() - inicio,
        tokens_entrada=contar_tokens(entrada) + tokens_contexto_previo,
        tokens_saida=contar_tokens(resultado.justificativa),
        bloqueado_por_guardrail=False,
        fontes_rag=recuperar_fontes(entrada),
    )
