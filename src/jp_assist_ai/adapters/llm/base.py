from __future__ import annotations

from abc import ABC, abstractmethod
from PIL import Image


class Translator(ABC):
    @abstractmethod
    def translate_image(self, image: Image.Image, src_lang: str, dst_lang: str) -> str:
        raise NotImplementedError
