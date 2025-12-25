from __future__ import annotations

import os

from jp_assist_ai.adapters.llm.base import Translator
from jp_assist_ai.adapters.llm.openai_llm import OpenAITranslator


def get_translator() -> Translator:
    provider = os.getenv("JP_ASSIST_TRANSLATOR", "openai").lower()
    if provider == "openai":
        return OpenAITranslator()
    raise ValueError(f"Unsupported translator provider: {provider}")
