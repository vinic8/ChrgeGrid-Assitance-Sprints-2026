"""Configuração central do projeto: variáveis de ambiente e caminhos.

Todo módulo que precisa de host/chave/modelo/parâmetros importa daqui —
nada de os.getenv espalhado pelo código.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT_DIR / "prompts"
DATA_DIR = ROOT_DIR / "data"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
CHROMA_DIR = DATA_DIR / "chroma_db"
FASTEMBED_CACHE_DIR = DATA_DIR / ".fastembed_cache"


@dataclass(frozen=True)
class Settings:
    ollama_api_key: str
    ollama_host: str
    model_primary: str
    groq_api_key: str
    model_groq: str
    temperature: float
    top_p: float
    max_tokens: int
    memoria_limite_tokens: int
    system_prompt_version: str
    # --- RAG (Sprint 04) ---
    rag_prompt_version: str
    rag_k: int
    rag_estrategia_chunking: str
    rag_limiar_relevancia: float
    rag_busca: str
    embeddings_backend: str
    embeddings_model: str
    ollama_embeddings_host: str

    @property
    def system_prompt_path(self) -> Path:
        return PROMPTS_DIR / f"system_prompt_{self.system_prompt_version}.md"


def load_settings() -> Settings:
    return Settings(
        ollama_api_key=os.getenv("OLLAMA_API_KEY", ""),
        ollama_host=os.getenv("OLLAMA_HOST", "https://ollama.com"),
        model_primary=os.getenv("MODEL_PRIMARY", "gemma4:cloud"),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        model_groq=os.getenv("MODEL_GROQ", "qwen/qwen3.8-27b"),
        temperature=float(os.getenv("TEMPERATURE", "0")),
        top_p=float(os.getenv("TOP_P", "0.9")),
        max_tokens=int(os.getenv("MAX_TOKENS", "800")),
        memoria_limite_tokens=int(os.getenv("MEMORIA_LIMITE_TOKENS", "1500")),
        system_prompt_version=os.getenv("SYSTEM_PROMPT_VERSION", "v7"),
        rag_prompt_version=os.getenv("RAG_PROMPT_VERSION", "v4"),
        rag_k=int(os.getenv("RAG_K", "6")),
        rag_estrategia_chunking=os.getenv("RAG_CHUNKING", "por_secao_tabelas"),
        rag_limiar_relevancia=float(os.getenv("RAG_LIMIAR_RELEVANCIA", "0")),
        rag_busca=os.getenv("RAG_BUSCA", "hibrida_expandida"),
        embeddings_backend=os.getenv("EMBEDDINGS_BACKEND", "fastembed"),
        embeddings_model=os.getenv("EMBEDDINGS_MODEL", "nomic-embed-text"),
        ollama_embeddings_host=os.getenv("OLLAMA_EMBEDDINGS_HOST", "http://localhost:11434"),
    )


def extract_system_prompt_body(markdown_path: Path) -> str:
    """Extrai o bloco ```text ... ``` de um arquivo prompts/system_prompt_vN.md.

    O prompt "de verdade" (o que vai pro LLM) fica dentro do primeiro bloco de
    código do markdown; o resto do arquivo é documentação/racional para humanos.
    """
    content = markdown_path.read_text(encoding="utf-8")
    marker = "```text"
    start = content.index(marker) + len(marker)
    end = content.index("```", start)
    return content[start:end].strip()
