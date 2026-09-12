# ChargeGrid Assistant — Sprint 03 (Refactory LangChain LCEL)

Continuação do projeto EV Challenge — GoodWe (Sprints 1 e 2), resolvendo o desafio
ChargeGrid Intelligence: orquestrar a recarga comercial de eletropostos GoodWe reais
(linha HCA G2), registrar o ciclo da sessão (via dados de OCPP e Modbus/RS485) e aplicar
políticas de tarifação dinâmica. Núcleo conversacional em **LangChain LCEL**
(`chain = retrieval | prompt | llm | parser`), com **RAG sobre uma base de conhecimento
técnica real** (`knowledge/*.md`, vetor store FAISS), memória por sessão em **summary
memory**, **saída estruturada validada em Pydantic v2**, **context engineering
(XML tagging)** e **guardrails** de escopo/jailbreak — tudo em código Python modular,
com interface gráfica em **Streamlit**.

O relatório de evolução (resumo Sprints 1/2 → Sprint 03, decisões de refactory,
tabela comparativa antes/depois, comparativo multi-provider e problemas/soluções)
é entregue em PDF em `docs/` — o conteúdo-fonte está em
[`docs/RELATORIO_EVOLUCAO.pdf`](docs/RELATORIO_EVOLUCAO.pdf).

**Multi-provider**: o chatbot roda sobre dois providers, selecionáveis na própria
interface — **Provider A: Ollama Cloud** (`gemma4:cloud`) e **Provider B: Groq**
(`qwen/qwen3.8-27b`). O plano era reintroduzir o Llama 3.3 das Sprints 1/2 via Groq,
mas esse modelo foi descontinuado nesse provider durante o desenvolvimento — ver
`docs/RELATORIO_EVOLUCAO.pdf` para o detalhamento da troca.

## O que mudou desde as Sprints 1/2

| | Sprints 1/2 | Sprint 03 |
|---|---|---|
| Execução | Google Colab, célula a célula | Python modular + Streamlit |
| Orquestração | Chamadas diretas ao SDK da Groq | LangChain LCEL (`prompt \| llm \| parser`) |
| Modelo/Provider | Llama 3.3 70B via Groq (único provider) | Multi-provider: `gemma4:cloud` via **Ollama Cloud** + `qwen/qwen3.8-27b` via **Groq** |
| Memória | Lista de mensagens sem limite | `ConversationSummaryBufferMemory` por sessão (ver seção "Memória conversacional") |
| Conhecimento técnico | Só o que estava no prompt (texto corrido) | RAG sobre `knowledge/*.md` (OCPP, Modbus, tarifação dinâmica, specs reais GoodWe) |
| Saída | Texto livre | Schema Pydantic v2 validado (`ConsultaRecarga`) |
| Prompt | Texto corrido | Versionado, com XML tagging (`prompts/`) |
| Segurança | Só instrução no prompt | Guardrails em código + instrução no prompt + orientação a profissional habilitado |
| Avaliação | Qualitativa (P1-P5, manual) | Eval set automático reexecutável (13 casos, incl. RAG) |

## Estrutura do projeto

```
SPRINT-03-IA/
├── app.py                        # Interface Streamlit (chat + comparativo ao vivo)
├── .streamlit/
│   └── config.toml               # Tema de cores GoodWe (vermelho da marca)
├── knowledge/                    # Base de conhecimento do RAG (fonte de verdade técnica)
│   ├── ocpp.md                   # Mensagens do ciclo de sessão e códigos de erro OCPP
│   ├── modbus_rs485.md           # Códigos de exceção Modbus e diagnóstico físico
│   ├── politica_tarifaria.md     # Tarifação dinâmica por posto horário, frota, descontos
│   └── charger_goodwe.md         # Specs reais do EV Charger GoodWe (linha HCA G2)
├── data/
│   └── faiss_index/               # Índice vetorial (gerado, não versionado - ver .gitignore)
├── prompts/
│   ├── system_prompt_v1.md       # Baseline (Sprints 1/2), sem marcação
│   ├── system_prompt_v2.md       # XML tagging (context engineering)
│   ├── system_prompt_v3.md       # v2 + bloco <idioma> (reforço anti-jailbreak)
│   ├── system_prompt_v4.md       # + <base_de_conhecimento> (RAG) e <limites_de_atuacao>
│   ├── system_prompt_v5.md       # v4 + contenção de distração por RAG irrelevante
│   ├── system_prompt_v6.md       # Versão ativa: generaliza para eletropostos GoodWe reais (fim da premissa FIAP)
│   └── VERSOES.md                # Tabela de versões: o que mudou, por quê, ganho medido
├── src/
│   ├── config.py                 # Variáveis de ambiente e caminhos centralizados
│   ├── tokens.py                 # Contagem de tokens (aproximação via tiktoken)
│   ├── manual_chat.py            # Reconstrução da versão manual (Sprints 1/2) p/ comparativo
│   ├── chain/
│   │   ├── builder.py            # Chain LCEL retrieval | prompt | llm | parser + guardrails
│   │   └── memoria.py            # ConversationSummaryBufferMemory (LangChain) por sessão
│   ├── rag/
│   │   └── indexer.py            # Indexação FAISS de knowledge/*.md e retriever
│   ├── schemas/
│   │   └── consulta_recarga.py   # Schema Pydantic v2 do domínio EV
│   └── guardrails/
│       ├── scope_validator.py    # Recusa de pedidos fora do domínio GoodWe
│       └── moderation.py         # Recusa de jailbreak/prompt injection
├── evals/
│   ├── eval_cases.py             # Eval set (P1-P5 + guardrail/memória/RAG/limites de atuação)
│   ├── run_eval.py               # Reexecuta o eval: legado vs LCEL (relatório §3)
│   ├── compare_models.py         # Reexecuta o eval multi-provider (Bloco B, relatório §3.1)
│   └── results/                  # Saída de cada execução (.json não versionado, .md versionado)
├── docs/
│   └── RELATORIO_EVOLUCAO.pdf    # Conteúdo-fonte do relatório (entregue em PDF na pasta docs/)
├── requirements.txt
└── .env.example
```

## Como rodar

### 1. Pré-requisitos

- Python 3.11+ recomendado (ver nota de compatibilidade abaixo se estiver no 3.14).
- Uma API key da **Ollama Cloud** (Provider A): crie em https://ollama.com/settings/keys.
  Não é necessário instalar o Ollama localmente — o projeto fala direto com
  `https://ollama.com`.
- Uma API key da **Groq** (Provider B): crie em https://console.groq.com/keys.

### 2. Instalação

```bash
cd C:\PROJETOS\SPRINT-03-IA
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# edite o .env e preencha OLLAMA_API_KEY e GROQ_API_KEY
```

### 3. Indexar a base de conhecimento (RAG)

```bash
python -m src.rag.indexer
```

Lê `knowledge/*.md`, gera embeddings locais (FastEmbed, sem API key) e salva o
índice FAISS em `data/faiss_index/`. **Passo único** — só precisa rodar de novo se
editar os arquivos em `knowledge/`. Se pular este passo, a primeira pergunta feita
no chat ou no eval constrói o índice automaticamente (mais lento na primeira vez).

### 4. Rodar a interface

```bash
streamlit run app.py
```

Abre automaticamente no navegador em **http://localhost:8501** (se essa porta estiver
ocupada, o Streamlit sobe na próxima livre, ex.: `:8502`, e mostra a URL no terminal).

### 5. Rodar o eval set (gera a tabela antes/depois do relatório)

```bash
python -m evals.run_eval
```

Isso chama o modelo de verdade (Ollama Cloud) nas duas versões (legada e LCEL) para
cada caso de `evals/eval_cases.py` (13 casos, incluindo RAG e limites de atuação), e
grava `evals/results/comparativo_<timestamp>.md` com a tabela pronta para colar no
relatório §3.

### 6. Rodar o comparativo multi-provider (Bloco B)

```bash
python -m evals.compare_models
```

Roda os mesmos 13 casos na mesma chain LCEL, variando só o provider (Ollama Cloud vs.
Groq), e grava `evals/results/modelos_<timestamp>.md`. Resultado consolidado no
relatório §3.1.

## Variáveis de ambiente

| Variável | Descrição | Obrigatória |
|---|---|---|
| `OLLAMA_API_KEY` | Chave da Ollama Cloud — Provider A (https://ollama.com/settings/keys) | ✅ Sim |
| `OLLAMA_HOST` | Host da API (default `https://ollama.com`) | Não |
| `MODEL_PRIMARY` | Modelo do Provider A (default `gemma4:cloud`) | Não |
| `GROQ_API_KEY` | Chave da Groq — Provider B (https://console.groq.com/keys) | ✅ Sim |
| `MODEL_GROQ` | Modelo do Provider B (default `qwen/qwen3.8-27b`) | Não |
| `TEMPERATURE` | Temperatura de geração, usada nos dois providers (default `0.2`) | Não |
| `MAX_TOKENS` | Máximo de tokens de saída por resposta (default `600`) | Não |
| `MEMORIA_LIMITE_TOKENS` | Limite de tokens da memória por sessão (default `1500`) | Não |
| `SYSTEM_PROMPT_VERSION` | Versão do prompt ativa: `v1` a `v6` (default `v6`) | Não |

Nenhuma chave deve aparecer no código nem ser commitada — `.env` está no `.gitignore`.

## Nota de compatibilidade (Python 3.14)

Esta máquina tem Python 3.14 instalado. É uma versão muito recente; se `pip install`
falhar ao compilar alguma dependência nativa (`pydantic-core`, `tiktoken`), crie o
venv com uma versão mais testada (3.11–3.12) — `py -3.12 -m venv .venv`, se disponível
— e repita a instalação.

## Memória conversacional

O chatbot usa **`ConversationSummaryBufferMemory`**, a classe do próprio LangChain
(`src/chain/memoria.py`, importada de `langchain_classic.memory` — requisito
obrigatório do desafio). Ela guarda o histórico literal da sessão até
`MEMORIA_LIMITE_TOKENS` (default 1500) e, ao estourar, envia a parte mais antiga da
conversa para o próprio LLM (o mesmo provider/modelo em uso) gerar um **resumo em
texto livre**, que substitui as mensagens resumidas — comportamento nativo da
classe (`save_context` → `prune()` → `predict_new_summary()`), não reimplementado
à mão. O prompt de resumo (`_PROMPT_RESUMO`) foi customizado em português, pedindo
para preservar fatos operacionais (IDs de carregador/veículo, potências, limites,
tarifas, decisões) e descartar conversa fiada.

**Nota de depreciação (decisão consciente)**: `ConversationSummaryBufferMemory` está
marcada para remoção no LangChain 2.0 (movida para `langchain_classic`; o próprio
time recomenda `RunnableWithMessageHistory`/checkpointing como substituto). Optamos
por usá-la mesmo assim porque é um requisito explícito do desafio, aceitando o aviso
de depreciação em troca de aderência literal. Detalhe técnico: a classe conta tokens
via `llm.get_num_tokens_from_messages`, que por padrão exige o pacote `transformers`
(tokenizer GPT-2 baixado da internet) — para não introduzir essa dependência pesada,
`_MemoriaChargeGrid` (subclasse de `ConversationSummaryBufferMemory`, mesmo tipo,
só esse um método trocado) substitui só a contagem de tokens por `tiktoken`
(`src/tokens.py`), mantendo o resto do comportamento herdado sem alteração.

Na interface, o expander "Avançado" mostra o resumo atual da sessão
(`memoria.moving_summary_buffer`) sempre que ele existir. A memória é por
`session_id` (`st.session_state.session_id` no Streamlit) — cada aba/sessão do
navegador tem seu próprio histórico, isolado em memória de processo (não persiste
em disco nem banco).

## RAG — base de conhecimento (`knowledge/`)

O assistente resolve o problema real do desafio ChargeGrid Intelligence (não só
conversa sobre ele) consultando uma base de conhecimento técnica antes de responder:

- **`modbus_rs485.md`** — extraído do mapa de registradores Modbus **real** do
  GoodWe HCA G2 (documento oficial do fabricante): os 4 códigos de exceção que
  o equipamento realmente define (`0x0001`–`0x0004`), os bits de falha reais
  (registradores `10001`–`10008`, incluindo `falha de aterramento` no bit1 do
  registrador `10002`) e registradores operacionais (status, limite de
  disjuntor, potência máxima).
- **`charger_goodwe.md`** — specs **reais** do datasheet GoodWe HCA G2: os
  3 modelos por potência (GW7K/11K/22K-HCA-20), proteções, certificações e o
  protocolo de comunicação declarado pelo fabricante (**Modbus TCP**, não OCPP
  — ver nota abaixo). O limite de rede/disjuntor não tem valor padrão fixo:
  cada eletroposto real tem o seu, informado na conversa ou lido dos
  registradores Modbus `10026`/`10039` daquele equipamento.
- **`ocpp.md`** — como a documentação oficial confirma que o HCA G2 fala Modbus
  TCP e não OCPP nativamente, este documento foi reformulado como uma **camada
  de tradução/interoperabilidade**: uma tabela mapeando cada conceito OCPP
  (`StartTransaction`, `meterStop`, `StatusNotification.errorCode` etc.) para o
  registrador Modbus real equivalente — cobrindo o requisito de OCPP do
  desafio sem afirmar que o hardware suporta um protocolo que ele não suporta.
- **`politica_tarifaria.md`** — a única base explicitamente **ilustrativa**
  (postos tarifários, tarifa de frota, descontos): não existe uma tarifa
  pública da GoodWe para isso, então o documento diz isso abertamente, embora
  aponte que o carregador real já expõe um registrador de valor monetário
  (`10061`, "Charge amount"), o que torna a ideia compatível com o hardware.

As duas primeiras bases foram reescritas depois de receber a documentação
oficial da GoodWe (datasheet, manual e mapa Modbus) — a primeira versão usava
códigos de erro plausíveis mas não confirmados, corrigidos para os dados reais
do equipamento.

Arquitetura (`src/rag/indexer.py` + `src/chain/builder.py`): os `.md` são divididos
em chunks **por seção** (nunca fundindo seções vizinhas — ver decisão no relatório,
Problema 4), embarcados com FastEmbed (`paraphrase-multilingual-MiniLM-L12-v2`,
roda em CPU, sem API key) e indexados em FAISS (`data/faiss_index/`). A cada
pergunta, a chain LCEL recupera os `k=6` chunks mais relevantes e os injeta no
prompt como `<base_de_conhecimento>` (`system_prompt_v5.md`), com instrução
explícita para o modelo tratar esse conteúdo como fonte de verdade — sem essa
instrução, testamos e o modelo **ignorava** a política recuperada (ver Problema 4
do relatório). As fontes usadas em cada resposta aparecem na UI (📚) e em
`RespostaChat.fontes_rag`.

## Domínio do chatbot

Persona: Gestor de Operações de eletropostos GoodWe. O assistente **faz**: validação
de aumento de potência contra o limite da rede, cálculo de faturamento com
tarifação dinâmica (kWh × tarifa do posto horário, via RAG), registro do ciclo da
sessão com base em dados de OCPP, tradução de erros técnicos (OCPP e Modbus/RS485,
via RAG) e sugestão de Load Balancing. **Não faz, mas orienta a quem procurar**
(`<limites_de_atuacao>` no prompt): manutenção física do hardware, processamento
real de pagamento e decisões de segurança elétrica que dependam de inspeção
física — nesses casos, o assistente indica o profissional habilitado a acionar em
vez de recusar genericamente ou tentar resolver sozinho.
