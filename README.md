# ChargeGrid Assistant

Assistente com IA para a operação de eletropostos GoodWe, desenvolvido no EV Challenge
GoodWe (FIAP, Prompt and Artificial Intelligence, 2026.2). Este repositório contém a
entrega da Sprint 04, que dá continuidade às Sprints 1, 2 e 3.

O assistente responde a perguntas do operador sobre tarifação e faturamento de recargas,
regras de recarga compartilhada em condomínio, códigos de erro e registradores Modbus do
carregador GoodWe HCA G2, ciclo de sessão em OCPP, Load Balancing e procedimentos
operacionais. As respostas são baseadas em uma base de documentos (RAG) e sempre indicam
de qual documento, seção e página a informação foi tirada.

## Sumário

1. [O que foi feito na Sprint 04](#o-que-foi-feito-na-sprint-04)
2. [Como o assistente funciona](#como-o-assistente-funciona)
3. [Organização do projeto](#organização-do-projeto)
4. [Instalação e execução](#instalação-e-execução)
5. [Usando a interface](#usando-a-interface)
6. [Avaliação](#avaliação)
7. [Configuração](#configuração)
8. [Resultados](#resultados)
9. [Decisões técnicas](#decisões-técnicas)
10. [Documentação](#documentação)

## O que foi feito na Sprint 04

- **Base de conhecimento expandida**: 7 documentos em PDF (manual de produto e mapa Modbus
  do GoodWe HCA G2, interoperabilidade OCPP, manual operacional EV ChargeOps, regimento de
  recarga em condomínio, FAQ de carregamento e tabelas tarifárias).
- **Vetorização**: ChromaDB persistente com embeddings `nomic-embed-text`.
- **Pipeline RAG completo**: `PyMuPDFLoader`, `RecursiveCharacterTextSplitter`, retriever
  e prompt RAG versionado, cada etapa em um módulo de `src/rag/`.
- **Grounding e citação de fonte**: o assistente responde só com o conteúdo recuperado e
  cita documento, seção e página em toda resposta.
- **Avaliação com RAGAS** (`faithfulness` e `answer_relevancy`) a cada iteração, com uma
  rubrica manual equivalente aplicada em paralelo.
- **Segurança**: recusa de perguntas fora do contexto, proteção contra prompt injection
  embutido nos documentos e proibição de inventar especificações de produto.
- **Interface web** em Streamlit, com as fontes visíveis em cada resposta.
- **Multi-provider**: dois modelos, Gemma 4 (`gemma4:cloud`, via Ollama Cloud) e Qwen 3.8
  (`qwen/qwen3.8-27b`, via Groq), e um modo que compara os dois modelos com duas versões
  do prompt lado a lado.

## Como o assistente funciona

Cada pergunta passa pelas etapas abaixo. O código de cada uma está indicado entre
parênteses.

1. **Guardrails** (`src/guardrails/`): perguntas fora do domínio ou tentativas de jailbreak
   são barradas antes de qualquer chamada ao modelo.
2. **Recuperação** (`src/rag/retriever.py`): busca os 6 trechos mais relevantes no
   ChromaDB, combinando busca vetorial e busca por palavras-chave (BM25).
3. **Sanitização** (`src/rag/sanitizacao.py`): remove dos trechos qualquer instrução
   dirigida ao assistente, para que um documento adulterado não consiga mudar o
   comportamento do modelo.
4. **Prompt RAG** (`src/rag/prompt_rag.py`): monta o prompt com a persona do assistente, as
   regras de uso dos documentos e os trechos numerados.
5. **Modelo** (`src/chain/builder.py`): Gemma 4 ou Qwen 3.8 gera a resposta em um formato
   estruturado (`src/schemas/consulta_recarga.py`), incluindo os números dos trechos usados.
6. **Citação**: os números citados são convertidos em documento, seção e página a partir
   dos metadados dos trechos. Por isso o modelo não consegue citar uma fonte que não foi
   recuperada.

A conversa tem memória por sessão (`src/chain/memoria.py`): quando o histórico fica longo,
a parte mais antiga é resumida.

## Organização do projeto

```
.
├── app/
│   └── streamlit_app.py          Interface web
├── assets/                       Logo usado na interface
├── data/
│   ├── knowledge_base/           Base de conhecimento em PDF (lida pelo PyMuPDFLoader)
│   │   └── fontes/               Texto-fonte em Markdown de cada PDF
│   └── chroma_db/                Vector store (gerado na primeira execução, não versionado)
├── src/
│   ├── config.py                 Leitura do .env e caminhos do projeto
│   ├── rag/                      Pipeline RAG
│   │   ├── loader.py             Carregamento dos PDFs
│   │   ├── chunking.py           Divisão em trechos
│   │   ├── embeddings.py         Modelo de embeddings nomic-embed-text
│   │   ├── vector_store.py       ChromaDB persistente
│   │   ├── retriever.py          Busca dos trechos
│   │   ├── sanitizacao.py        Proteção contra prompt injection
│   │   └── prompt_rag.py         Versões do prompt RAG (v1 a v4)
│   ├── chain/
│   │   ├── builder.py            Execução de uma pergunta de ponta a ponta
│   │   ├── memoria.py            Memória da conversa
│   │   └── multi_provider.py     Comparação entre modelos e prompts
│   ├── guardrails/               Filtros de escopo e de jailbreak
│   ├── schemas/                  Formato estruturado da resposta
│   ├── manual_chat.py            Versão das Sprints 1/2, usada como comparação
│   └── tokens.py                 Contagem de tokens
├── prompts/                      Persona do assistente, versões v1 a v7 (v7 ativa)
├── evals/
│   ├── rag_eval_set.py           Perguntas de avaliação com respostas de referência
│   ├── run_ragas.py              Avaliação RAGAS e rubrica por iteração
│   ├── rubrica_manual.py         Rubrica manual equivalente ao RAGAS
│   ├── RUBRICA_FALLBACK.md       Critérios da rubrica
│   ├── test_recuperacao.py       Teste com perguntas fora do conjunto de avaliação
│   ├── test_injecao.py           Teste de prompt injection via documentos
│   ├── ragas_compat.py           Ajuste de compatibilidade do RAGAS
│   ├── SCORES_POR_ITERACAO.md    Tabela com os resultados de todas as iterações
│   ├── results/                  Resultado detalhado de cada execução
│   └── eval_cases.py, run_eval.py, compare_models.py, manual_test_10.py
│                                 Avaliações da Sprint 03, usadas como teste de regressão
├── scripts/
│   └── gerar_pdfs_base.py        Gera os PDFs da base a partir de data/knowledge_base/fontes
├── docs/
│   ├── relatorio_rag.md          Relatório técnico do RAG
│   ├── relatorio_modelos.md      Comparativo de modelos e parâmetros
│   ├── RELATORIO_EVOLUCAO_SPRINT04.pdf
│   └── RELATORIO_EVOLUCAO_SPRINT03.pdf
├── .env.example                  Modelo do arquivo de configuração
├── requirements.txt              Dependências da interface e do pipeline
├── requirements-eval.txt         Dependências adicionais da avaliação
└── INTEGRANTES.txt               Integrantes do grupo
```

Sobre a base de conhecimento: o manual de produto e o mapa Modbus foram montados a partir
da documentação oficial da GoodWe para o HCA G2. O manual operacional, o regimento de
condomínio, o FAQ e as tabelas tarifárias foram criados para o projeto, e cada um deles
informa isso no próprio texto. Para alterar a base, edite os arquivos de
`data/knowledge_base/fontes/` e gere os PDFs de novo (comando no fim da seção de
instalação). O vector store detecta a mudança e se reconstrói sozinho.

## Instalação e execução

### Requisitos

- Python 3.12 ou mais novo (testado no 3.14).
- Uma chave de API da Ollama Cloud, para o Gemma 4: https://ollama.com/settings/keys
- Uma chave de API da Groq, para o Qwen 3.8: https://console.groq.com/keys
- Cerca de 2 GB livres em disco (dependências e modelo de embeddings).

### Passo 1. Instalar o Python

Verifique se já existe uma versão 3.12 ou mais nova.

Windows:

```powershell
python --version
```

Linux e macOS:

```bash
python3 --version
```

Se não houver, instale:

- **Windows**: baixe o instalador em https://www.python.org/downloads/ e marque a opção
  "Add python.exe to PATH" na primeira tela.
- **macOS**: baixe o instalador em https://www.python.org/downloads/ ou use o Homebrew. O
  Python que já vem no macOS (3.9) é antigo demais para o projeto.

  ```bash
  brew install python@3.12
  ```

- **Linux (Ubuntu e Debian)**: o Ubuntu 24.04 já traz o Python 3.12. Instale também o
  módulo de ambientes virtuais:

  ```bash
  sudo apt update
  sudo apt install python3 python3-venv python3-pip
  ```

### Passo 2. Baixar o projeto

Opção 1: no GitHub, clique em **Code**, depois em **Download ZIP**, e descompacte o
arquivo.

Opção 2: com o Git instalado:

```bash
git clone https://github.com/vinic8/ChrgeGrid-Assitance-Sprints-2026.git
```

Em seguida, abra um terminal dentro da pasta do projeto (a pasta que contém o
`README.md`). Todos os comandos abaixo devem ser executados a partir dela.

### Passo 3. Criar o ambiente virtual e instalar as dependências

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Se o PowerShell recusar a ativação com a mensagem "a execução de scripts foi
desabilitada neste sistema", libere a execução apenas para o terminal atual e ative de
novo:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

Windows (Prompt de Comando):

```bat
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

Linux e macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Quando o ambiente está ativo, o terminal mostra `(.venv)` no começo da linha. Ao abrir um
terminal novo, é preciso ativar o ambiente de novo (somente a linha de ativação).

### Passo 4. Configurar as chaves de API

Crie o arquivo `.env` a partir do modelo e abra-o para edição.

Windows:

```powershell
copy .env.example .env
notepad .env
```

Linux:

```bash
cp .env.example .env
nano .env
```

macOS:

```bash
cp .env.example .env
open -e .env
```

Preencha as duas linhas abaixo com as suas chaves e salve o arquivo:

```
OLLAMA_API_KEY=sua_chave_da_ollama
GROQ_API_KEY=sua_chave_da_groq
```

As demais variáveis já vêm com a configuração usada na entrega. O `.env` está no
`.gitignore` e não é enviado ao repositório.

### Passo 5. Indexar a base de conhecimento

Com o ambiente ativo, o comando é o mesmo nos três sistemas:

```bash
python -m src.rag.vector_store
```

Este passo lê os PDFs de `data/knowledge_base/`, divide o texto em trechos, gera os
embeddings e grava tudo em `data/chroma_db/`. Na primeira execução ele baixa o modelo de
embeddings (cerca de 520 MB). O passo é opcional: se for pulado, a indexação acontece na
primeira pergunta feita na interface, que então demora mais e avisa que está preparando
a base. As avaliações das iterações 1 e 2 usam outras coleções, que são criadas
automaticamente quando necessário; para criá-las de uma vez, use
`python -m src.rag.vector_store --todas`.

### Passo 6. Abrir a interface

```bash
streamlit run app/streamlit_app.py
```

A interface abre no navegador em http://localhost:8501. Se a porta estiver ocupada, o
Streamlit usa a próxima livre e mostra o endereço no terminal. Para encerrar, use Ctrl+C
no terminal.

### Para editar a base de conhecimento

Depois de alterar os arquivos de `data/knowledge_base/fontes/`, gere os PDFs de novo:

```bash
python -m scripts.gerar_pdfs_base
```

## Usando a interface

**Barra lateral**

- Modelo: Gemma 4 (Ollama Cloud) ou Qwen 3.8 (Groq).
- Prompt RAG: versão do prompt, de v1 a v4. A v4 é a padrão.
- Avançado: quantidade de trechos recuperados (k), tipo de busca (vale para as duas abas), opção de desligar os
  guardrails para depuração, parâmetros de geração em uso e ocupação da memória da
  conversa.

**Aba Chat**

Conversa com memória. Com o chat vazio, a tela mostra quatro perguntas de exemplo que
podem ser enviadas com um clique. Abaixo de cada resposta aparecem:

- as fontes usadas, no formato `[número] Documento - Seção - página`. Quando a informação
  não existe na base, aparece um aviso no lugar das fontes. Quando a pergunta é barrada
  pelo guardrail, isso também é indicado;
- modelo, versão do prompt, k, tipo de busca e tempo de resposta;
- os trechos recuperados, com o score de cada um. Se a sanitização removeu alguma
  instrução embutida em um trecho, isso é indicado;
- a resposta estruturada completa, em "Detalhes técnicos".

**Aba Multi-provider**

Envia a mesma pergunta para os dois modelos, cada um com as versões v2 e v4 do prompt, e
mostra as quatro respostas lado a lado com suas fontes e tempos. A busca é feita uma vez
e os mesmos trechos são usados nas quatro respostas.

**Perguntas para testar**

```
O carregador C11 fez uma recarga das 18:30 às 19:00, com consumo de 5 kWh. Quanto fica o faturamento?
No condomínio, em quanto tempo preciso tirar o carro da vaga depois da recarga?
O que significa o código de exceção Modbus 0x0002?
Qual a potência do modelo GW30K-HCA-20?
Qual a garantia do GW22K-HCA-20?
Qual a melhor receita de bolo?
```

As três últimas testam a segurança: o GW30K-HCA-20 não existe (o assistente não deve
inventar uma potência), a garantia não consta na base (deve recusar) e a última está fora
do domínio (é barrada pelo guardrail).

## Avaliação

A avaliação precisa de dependências adicionais. Instale uma vez, com o ambiente ativo:

```bash
pip install -r requirements-eval.txt
pip install --no-deps ragas==0.4.3
```

O RAGAS é instalado com `--no-deps` porque declara o pacote `scikit-network`, que o projeto
não usa e que, no Python 3.14, só instala com um compilador C++.

Avaliação RAGAS da configuração final (Gemma 4):

```bash
python -m evals.run_ragas --iteracao it6
```

Mesma configuração usada no comparativo de modelos, com o Qwen 3.8:

```bash
python -m evals.run_ragas --iteracao it3 --provider groq
```

Versão das Sprints 1/2, sem RAG, como referência:

```bash
python -m evals.run_ragas --iteracao legado
```

Teste com perguntas fora do conjunto de avaliação (recuperação e pipeline completo):

```bash
python -m evals.test_recuperacao --com-llm
```

Teste de prompt injection via documentos:

```bash
python -m evals.test_injecao
```

Comparação entre modelos e prompts pelo terminal:

```bash
python -m src.chain.multi_provider "Qual a tarifa para veículos de frota?"
```

Cada execução grava o resultado em `evals/results/` e atualiza a tabela
`evals/SCORES_POR_ITERACAO.md`.

## Configuração

Todas as opções ficam no arquivo `.env`.

| Variável | Descrição | Valor padrão |
|---|---|---|
| `OLLAMA_API_KEY` | Chave da Ollama Cloud (Gemma 4) | obrigatória |
| `GROQ_API_KEY` | Chave da Groq (Qwen 3.8) | obrigatória |
| `MODEL_PRIMARY` | Modelo da Ollama Cloud | `gemma4:cloud` |
| `MODEL_GROQ` | Modelo da Groq | `qwen/qwen3.8-27b` |
| `TEMPERATURE` | Temperatura de geração | `0` |
| `TOP_P` | Top-p de geração | `0.9` |
| `MAX_TOKENS` | Limite de tokens da resposta | `800` |
| `SYSTEM_PROMPT_VERSION` | Versão da persona | `v7` |
| `RAG_PROMPT_VERSION` | Versão do prompt RAG | `v4` |
| `RAG_K` | Quantidade de trechos recuperados | `6` |
| `RAG_CHUNKING` | Estratégia de divisão: `por_secao_tabelas`, `por_secao` ou `recursivo_basico` | `por_secao_tabelas` |
| `RAG_BUSCA` | Tipo de busca: `hibrida_expandida`, `hibrida` ou `vetorial` | `hibrida_expandida` |
| `RAG_LIMIAR_RELEVANCIA` | Score mínimo para enviar trechos ao modelo (0 desliga) | `0` |
| `EMBEDDINGS_BACKEND` | Onde roda o nomic-embed-text: `fastembed` (local) ou `ollama` | `fastembed` |
| `MEMORIA_LIMITE_TOKENS` | Tamanho do histórico antes de resumir | `1500` |

## Resultados

Mesmo conjunto de avaliação (21 perguntas) em todas as versões, com o Gemma 4 como modelo
e como juiz. Tabela completa em `evals/SCORES_POR_ITERACAO.md`.

| Versão | Faithfulness (RAGAS) | Answer relevancy (RAGAS) | Citação de fonte | Acerto factual |
|---|---|---|---|---|
| Sprints 1/2 (sem RAG) | 0,137 | 0,732 | 0% | 33,3% |
| Sprint 03 | 0,497 | 0,655 | 0% | 55,6% |
| Sprint 04, iteração 1 | 0,751 | 0,717 | 5,6% | 77,8% |
| Sprint 04, iteração 2 | 0,856 | 0,767 | 94,4% | 88,9% |
| Sprint 04, iteração 4 | 0,902 | 0,821 | 100% | 100% |
| Sprint 04, iteração 6 (final) | 0,895 | 0,777 | 100% | 100% |

Na configuração final, o assistente também responde corretamente 10 de 10 perguntas
escritas fora do conjunto de avaliação, recusa 6 de 6 perguntas fora do domínio e
resiste aos 4 ataques de prompt injection testados. A queda de answer relevancy da
iteração 6 vem de um único caso e está explicada no relatório do RAG.

## Decisões técnicas

- **Embeddings locais**: a Ollama Cloud não disponibiliza modelos de embedding pela API (as
  chamadas para `nomic-embed-text` retornaram HTTP 401). O mesmo modelo,
  `nomic-ai/nomic-embed-text-v1.5`, roda localmente com o FastEmbed. Para usar um Ollama
  local, configure `EMBEDDINGS_BACKEND=ollama`.
- **Busca híbrida com expansão de consulta**: em português, a busca só vetorial
  favorecia trechos com palavras frequentes, como "recarga". A busca combina o ranking
  vetorial com o BM25, e a consulta do BM25 recebe os termos usados nos documentos
  ("quanto custa" passa a incluir "tarifa" e "posto tarifário"). Em perguntas novas, a
  seção certa passou de 4 em 10 (só vetorial) para 10 em 10.
- **Sem limiar de relevância**: um score mínimo para enviar trechos ao modelo foi testado,
  mas recusava perguntas legítimas curtas. A recusa fica com o guardrail de escopo e com a
  regra do prompt RAG.
- **Tabelas dos PDFs**: as tabelas são extraídas linha a linha, para que código, nome,
  causa e ação de cada linha não se misturem com as linhas vizinhas.

## Documentação

- `docs/RELATORIO_EVOLUCAO_SPRINT04.pdf`: relatório de evolução da Sprint 04.
- `docs/relatorio_rag.md`: pipeline, decisões de chunking, versões do prompt RAG,
  iterações e segurança.
- `docs/relatorio_modelos.md`: comparativo entre Gemma 4 e Qwen 3.8 e parâmetros usados.
- `evals/RUBRICA_FALLBACK.md`: rubrica manual equivalente ao RAGAS.
- `prompts/VERSOES.md`: histórico das versões da persona.
- `INTEGRANTES.txt`: integrantes do grupo.
