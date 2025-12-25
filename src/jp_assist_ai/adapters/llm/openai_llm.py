from __future__ import annotations

import base64
import io
import os

from PIL import Image
from openai import OpenAI

from jp_assist_ai.adapters.llm.base import Translator


class OpenAITranslator(Translator):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required.")
        self._client = OpenAI(api_key=api_key)
        self._model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def translate_image(self, image: Image.Image, src_lang: str, dst_lang: str) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode("ascii")

        prompt = (
            "You are a professional translator. Extract all readable text from the image, "
            f"then translate from {src_lang} to {dst_lang}. "
            "Return concise output with clear separation between original and translation."
        )

        resp = self._client.responses.create(
            model=self._model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": f"data:image/png;base64,{b64}"},
                    ],
                }
            ],
        )
        return resp.output_text.strip()
