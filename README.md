# ChargeGrid Assistant — Sprint 04 (RAG medido, confiável e utilizável)

Continuação do projeto EV Challenge — GoodWe (Sprints 1, 2 e 3). O ChargeGrid Assistant
apoia o operador de eletropostos GoodWe: orquestração de potência, registro do ciclo de
recarga (OCPP/Modbus), faturamento com tarifação por posto horário, regras de recarga
compartilhada em condomínio e diagnóstico de falhas do carregador GoodWe HCA G2.

Na Sprint 04 o RAG do projeto passou a ser **medido, confiável e utilizável**:

- **Vetorização**: base expandida (7 PDFs) em **ChromaDB persistente** com embeddings
  **`nomic-embed-text`**.
- **Pipeline RAG end-to-end**: `PyMuPDFLoader → RecursiveCharacterTextSplitter →
  retriever → prompt RAG versionado`, em módulos separados em `src/rag/`.
- **Grounding + citação**: responde só com o contexto recuperado e cita **documento,
  seção e página** em toda resposta. A citação é resolvida pelos metadados do trecho,
  não pelo texto gerado.
- **Avaliação**: **RAGAS** (`faithfulness`, `answer_relevancy`) por iteração, mais a
  rubrica manual de fallback aplicada em paralelo.
- **Interface web** (Streamlit) com citação visível e modo **multi-provider**
  (2 modelos × 2 prompts).
- **Segurança**: recusa fora do contexto (guardrail de escopo + regra do prompt), proteção contra
  prompt injection via documentos e proibição de inventar especificações.

**Modelos (multi-provider)**: **Gemma 4** (`gemma4:cloud`) via **Ollama Cloud** e
**Qwen 3.8** (`qwen/qwen3.8-27b`) via **Groq**, selecionáveis na interface.

Resultados: [`evals/SCORES_POR_ITERACAO.md`](evals/SCORES_POR_ITERACAO.md) ·
[`docs/relatorio_rag.md`](docs/relatorio_rag.md) ·
[`docs/relatorio_modelos.md`](docs/relatorio_modelos.md) ·
[`docs/RELATORIO_EVOLUCAO_SPRINT04.pdf`](docs/RELATORIO_EVOLUCAO_SPRINT04.pdf) (relatório de evolução).

## Estrutura do projeto

```
SPRINT-03-IA/
├── app/
│   └── streamlit_app.py          # Interface (chat com citação visível + aba multi-provider)
├── data/
│   ├── knowledge_base/           # Base expandida em PDF (entrada do PyMuPDFLoader)
│   │   ├── manual_produto_goodwe_hca_g2.pdf     # Datasheet/manual oficial GoodWe HCA G2
│   │   ├── mapa_modbus_hca_g2.pdf               # Mapa Modbus oficial (exceções, falhas, registradores)
│   │   ├── interoperabilidade_ocpp.pdf          # Camada OCPP ↔ Modbus
│   │   ├── manual_operacional_ev_chargeops.pdf  # Manual operacional ChargeGrid / EV ChargeOps
│   │   ├── regimento_recarga_condominial.pdf    # Regimento de recarga compartilhada em condomínio
│   │   ├── faq_carregamento.pdf                 # FAQ de carregamento
│   │   ├── tabelas_tarifarias.pdf               # Tabelas tarifárias (postos horários, frota, ocupação)
│   │   └── fontes/                              # Fonte editável (.md) de cada PDF
│   └── chroma_db/                # Vector store persistente (gerado, não versionado)
├── src/
│   ├── config.py                 # Variáveis de ambiente e caminhos
│   ├── rag/
│   │   ├── loader.py             # PyMuPDFLoader + normalização Unicode
│   │   ├── chunking.py           # RecursiveCharacterTextSplitter (por página | por seção)
│   │   ├── embeddings.py         # nomic-embed-text (FastEmbed local | Ollama)
│   │   ├── vector_store.py       # ChromaDB persistente + reindexação automática
│   │   ├── retriever.py          # top-k híbrido (vetorial + BM25 com expansão de consulta)
│   │   ├── sanitizacao.py        # Proteção contra prompt injection via documentos
│   │   └── prompt_rag.py         # Prompt RAG versionado (v1 a v4)
│   ├── chain/
│   │   ├── builder.py            # Chain LCEL: prompt RAG | llm | parser + citações
│   │   ├── multi_provider.py     # Bônus: 2 modelos × 2 prompts em paralelo
│   │   └── memoria.py            # ConversationSummaryBufferMemory por sessão
│   ├── guardrails/               # Escopo e jailbreak (antes da chain)
│   ├── schemas/consulta_recarga.py  # Saída estruturada (Pydantic v2), com fontes_citadas e fora_da_base
│   ├── manual_chat.py            # Versão legada (Sprints 1/2), baseline "antes"
│   └── tokens.py
├── prompts/
│   ├── system_prompt_v1..v7.md   # Persona (v7 ativa)
│   └── VERSOES.md
├── evals/
│   ├── rag_eval_set.py           # Eval set do RAG (18 respondíveis + 3 recusas)
│   ├── run_ragas.py              # RAGAS + rubrica por iteração
│   ├── rubrica_manual.py         # Fallback manual do RAGAS
│   ├── RUBRICA_FALLBACK.md       # Critérios da rubrica e equivalência
│   ├── test_injecao.py           # Teste de prompt injection via documentos
│   ├── test_recuperacao.py       # Recuperação com perguntas fora do eval set (sem LLM)
│   ├── ragas_compat.py           # Shim RAGAS 0.4 × langchain-community 0.4
│   ├── SCORES_POR_ITERACAO.md    # Tabela consolidada de scores
│   ├── results/                  # Resultado de cada execução (.md e .json)
│   └── eval_cases.py, run_eval.py, compare_models.py, manual_test_10.py   # evals da Sprint 03
├── scripts/
│   └── gerar_pdfs_base.py        # Fontes .md → PDFs da base
├── docs/
│   ├── relatorio_rag.md          # Pipeline, chunking, prompt RAG versionado e iterações
│   ├── relatorio_modelos.md      # Comparativo Gemma × Qwen e parâmetros
│   ├── RELATORIO_EVOLUCAO_SPRINT04.pdf   # Relatório de evolução da Sprint 04 (até 5 páginas)
│   └── RELATORIO_EVOLUCAO_SPRINT03.pdf   # Relatório de evolução da Sprint 03 (histórico)
├── INTEGRANTES.txt               # Nome, RM e turma dos integrantes
├── requirements.txt            # Interface e pipeline RAG
├── requirements-eval.txt       # Avaliação (RAGAS)
└── .env.example
```

## Como rodar

Passo a passo para Windows, Linux e macOS. Os comandos de Python são os mesmos nos três;
mudam só a forma de chamar o Python, de ativar o ambiente virtual e de copiar o `.env`.

### 1. Pré-requisitos

- **Python 3.12 ou mais novo** (testado no 3.14). Confira com `python --version`
  (Windows) ou `python3 --version` (Linux e macOS).
- Chave de API da **Ollama Cloud** (Gemma 4): https://ollama.com/settings/keys
- Chave de API da **Groq** (Qwen 3.8): https://console.groq.com/keys
- Cerca de 2 GB livres em disco (dependências + modelo de embeddings).

Se não tiver o Python 3.12+:

| Sistema | Como instalar |
|---|---|
| Windows | Instalador de https://www.python.org/downloads/. Marque **"Add python.exe to PATH"** na primeira tela. |
| macOS | Instalador de https://www.python.org/downloads/ ou `brew install python@3.12`. O Python que vem no macOS (3.9) é antigo demais. |
| Linux (Ubuntu/Debian) | `sudo apt update && sudo apt install python3 python3-venv python3-pip`. O Ubuntu 24.04 já traz o 3.12; em versões mais antigas, instale um Python mais novo (ex.: via `pyenv`). |

### 2. Baixar o projeto

Escolha uma das opções:

- **ZIP**: no GitHub, botão **Code → Download ZIP**, e descompacte. A pasta se chama
  `ChrgeGrid-Assitance-Sprints-2026-main`.
- **Git**: `git clone https://github.com/vinic8/ChrgeGrid-Assitance-Sprints-2026.git`
  (a pasta se chama `ChrgeGrid-Assitance-Sprints-2026`).

Abra um terminal **dentro da pasta do projeto** (a que tem o `README.md`). Todos os
comandos a seguir rodam a partir dela.

### 3. Criar o ambiente virtual e instalar as dependências

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Se o PowerShell bloquear a ativação ("a execução de scripts foi desabilitada"), rode
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` e ative de novo (vale só
para aquele terminal). No Prompt de Comando (cmd), ative com `.venv\Scripts\activate.bat`.

**Linux e macOS (Terminal)**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Com o ambiente ativado, o terminal mostra `(.venv)` no início da linha. Se fechar o
terminal, ative de novo antes de rodar o projeto (só a linha `Activate.ps1` ou
`source .venv/bin/activate`).

### 4. Configurar as chaves de API

Crie o `.env` a partir do modelo:

| Sistema | Comando |
|---|---|
| Windows | `copy .env.example .env` e depois `notepad .env` |
| Linux | `cp .env.example .env` e depois `nano .env` |
| macOS | `cp .env.example .env` e depois `open -e .env` |

No arquivo, preencha `OLLAMA_API_KEY=` e `GROQ_API_KEY=` com as suas chaves e salve. As
demais variáveis já vêm com a configuração final do projeto (ver "Variáveis de
ambiente"). O `.env` está no `.gitignore` e nunca vai para o repositório.

### 5. Indexar a base no ChromaDB (opcional)

```bash
python -m src.rag.vector_store
```

(Daqui em diante, com o ambiente ativado, o comando é `python` nos três sistemas.)

Lê `data/knowledge_base/*.pdf` com o `PyMuPDFLoader`, divide em chunks, gera os
embeddings `nomic-embed-text` e grava as coleções em `data/chroma_db/`. Na primeira vez,
baixa o modelo de embeddings (~520 MB) para `data/.fastembed_cache/`. Se este passo for
pulado, a primeira pergunta na interface indexa sozinha (e demora mais). Se um PDF da
base mudar, a coleção é reconstruída automaticamente na próxima consulta.

Para editar a base: altere `data/knowledge_base/fontes/*.md` e rode
`python -m scripts.gerar_pdfs_base`.

### 6. Abrir a interface

```bash
streamlit run app/streamlit_app.py
```

Abre no navegador em http://localhost:8501 (se a porta estiver ocupada, o Streamlit usa
a próxima livre e mostra a URL no terminal). Para encerrar, `Ctrl+C` no terminal.

**O que tem na tela**

**Barra lateral**
- **Modelo**: Gemma 4 (Ollama Cloud) ou Qwen 3.8 (Groq).
- **Prompt RAG**: v1 a v4 (`src/rag/prompt_rag.py`; v4 é a padrão), com o resumo do que
  muda em cada uma.
- **Avançado**: `k` (trechos recuperados), modo de busca (`hibrida_expandida`, `hibrida`
  ou `vetorial`), desligar guardrails para depuração, parâmetros de geração em uso e uso
  da memória da conversa.

**Aba Chat**: conversa com memória. Cada resposta mostra:
- o texto da resposta;
- **📚 Fontes**: lista `[id] Documento — Seção · página`. Se a informação não está na
  base, aparece um aviso de "não encontrada na base" no lugar das fontes; se a pergunta
  foi barrada pelo guardrail, aparece 🚫;
- linha de metadados (modelo, prompt, k, busca, decisão, latência);
- **Trechos recuperados**: os trechos enviados ao modelo, com score de relevância. Um
  trecho em que a sanitização removeu uma instrução embutida aparece marcado com ⚠️;
- **Detalhes técnicos**: a saída estruturada completa (schema `ConsultaRecarga`).

**Aba Multi-provider** (bônus): a mesma pergunta para os dois modelos × as versões v2 e v4
do prompt RAG, em quatro respostas lado a lado, cada uma com suas fontes e sua latência.
A recuperação é feita uma vez só e compartilhada entre as quatro.

**Perguntas para testar**
- "O carregador C11 fez uma recarga das 18:30 às 19:00, com consumo de 5 kWh. Quanto fica o faturamento?"
- "No condomínio, em quanto tempo preciso tirar o carro da vaga depois da recarga?"
- "O que significa o código de exceção Modbus 0x0002?"
- "Qual a potência do modelo GW30K-HCA-20?" (modelo inexistente: o assistente não deve inventar)
- "Qual a garantia do GW22K-HCA-20?" (não consta na base: deve recusar)
- "Qual a melhor receita de bolo?" (fora do domínio: bloqueado pelo guardrail)

### 7. Avaliação (opcional)

Instale as dependências de avaliação (uma vez, com o ambiente ativado):

```bash
pip install -r requirements-eval.txt
pip install --no-deps ragas==0.4.3
```

O `--no-deps` evita o pacote `scikit-network`, que o RAGAS declara mas o projeto não
usa e que, no Python 3.14, exigiria um compilador C++ para instalar.

```bash
python -m evals.run_ragas --iteracao it6                  # RAGAS + rubrica da configuração final (Gemma)
python -m evals.run_ragas --iteracao it3 --provider groq  # comparativo de modelos com o Qwen
python -m evals.run_ragas --iteracao legado               # Sprints 1/2 (sem RAG)
python -m evals.test_injecao                              # prompt injection via documentos
python -m evals.test_recuperacao --com-llm                # perguntas fora do eval set: recuperação e pipeline completo
python -m src.chain.multi_provider "Qual a tarifa para frota?"   # bônus multi-provider no terminal
```

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|---|---|---|
| `OLLAMA_API_KEY` | Chave da Ollama Cloud (Gemma 4) | obrigatória |
| `GROQ_API_KEY` | Chave da Groq (Qwen 3.8) | obrigatória |
| `MODEL_PRIMARY` / `MODEL_GROQ` | Modelos dos dois providers | `gemma4:cloud` / `qwen/qwen3.8-27b` |
| `TEMPERATURE` / `TOP_P` / `MAX_TOKENS` | Parâmetros de geração | `0` / `0.9` / `800` |
| `SYSTEM_PROMPT_VERSION` | Persona ativa | `v7` |
| `RAG_PROMPT_VERSION` | Prompt RAG ativo | `v4` |
| `RAG_K` | Top-k da recuperação | `6` |
| `RAG_CHUNKING` | `por_secao` ou `recursivo_basico` | `por_secao` |
| `RAG_BUSCA` | `hibrida_expandida` (vetorial + BM25 com expansão de consulta), `hibrida` ou `vetorial` | `hibrida_expandida` |
| `RAG_LIMIAR_RELEVANCIA` | Porta sobre o melhor score de cosseno (0 = desligada; ver `docs/relatorio_rag.md` §5) | `0` |
| `EMBEDDINGS_BACKEND` | `fastembed` (local) ou `ollama` | `fastembed` |

Nenhuma chave fica no código nem no histórico do Git: o `.env` está no `.gitignore`.

## Decisões importantes

- **`nomic-embed-text` sem a Ollama Cloud**: a Ollama Cloud não serve modelos de
  embedding pela API. Testamos `nomic-embed-text` e `embeddinggemma` com a mesma chave
  que funciona no chat e as duas chamadas retornaram HTTP 401. Por isso o mesmo
  modelo (`nomic-ai/nomic-embed-text-v1.5`, o que a Ollama distribui como
  `nomic-embed-text`) roda localmente via FastEmbed. O backend `ollama` continua
  disponível (`EMBEDDINGS_BACKEND=ollama`) para um Ollama local ou para o caso de a
  Cloud liberar o endpoint.
- **Busca híbrida com expansão de consulta**: em português, o nomic-embed-text dá peso
  demais a palavras frequentes. Por isso o retriever funde o ranking vetorial com BM25
  (Reciprocal Rank Fusion). O operador também não usa o vocabulário do documento
  ("quanto custa" × "tarifa do posto"), então a consulta do BM25 é expandida com os
  termos do documento. Com isso, a seção certa é recuperada em 10 de 10 perguntas novas
  (`python -m evals.test_recuperacao`), contra 4/10 na busca só vetorial. Detalhes e
  números em `docs/relatorio_rag.md`.
- **Sem porta de relevância**: um limiar sobre o score de similaridade foi usado nas
  iterações 3 a 5, mas recusava perguntas legítimas curtas (6/10 respondidas, contra
  10/10 sem ele). A recusa fora do contexto fica com o guardrail de escopo e com a regra
  do prompt RAG (6/6 perguntas fora do domínio recusadas). Detalhes em
  `docs/relatorio_rag.md` §5.
- **Documentos ilustrativos**: o manual de produto e o mapa Modbus vêm da documentação
  oficial GoodWe. O manual operacional, o regimento condominial, o FAQ e as tabelas
  tarifárias são ilustrativos, e cada um declara isso na nota de proveniência do
  próprio documento.

## Memória, schema e guardrails (herdados da Sprint 03)

- `ConversationSummaryBufferMemory` por sessão (`src/chain/memoria.py`): resume a parte
  mais antiga da conversa quando o histórico passa de `MEMORIA_LIMITE_TOKENS`.
- Saída estruturada `ConsultaRecarga` (Pydantic v2), agora com `fontes_citadas` (ids dos
  trechos usados) e `fora_da_base`.
- Guardrails de escopo e jailbreak rodam antes da chain, sem gastar chamada ao LLM.
