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


@dataclass(frozen=True)
class Settings:
    ollama_api_key: str
    ollama_host: str
    model_primary: str
    groq_api_key: str
    model_groq: str
    temperature: float
    max_tokens: int
    memoria_limite_tokens: int
    system_prompt_version: str

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
        temperature=float(os.getenv("TEMPERATURE", "0.2")),
        max_tokens=int(os.getenv("MAX_TOKENS", "600")),
        memoria_limite_tokens=int(os.getenv("MEMORIA_LIMITE_TOKENS", "1500")),
        system_prompt_version=os.getenv("SYSTEM_PROMPT_VERSION", "v6"),
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
