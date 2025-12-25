from __future__ import annotations

from typing import List
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR


class PaddleOcrEngine:
    """
    OCR engine for Japanese/English.
    Note: Initialization is heavy; keep one instance for reuse.
    """
    def __init__(self):
        self._ocr = PaddleOCR(
            use_angle_cls=True,
            lang="japan",   # Japanese model (includes kanji/kana)
            show_log=False,
        )

    def recognize(self, image: Image.Image) -> str:
        # PaddleOCR expects numpy array (BGR/RGB both OK in many cases)
        img = np.array(image.convert("RGB"))
        result = self._ocr.ocr(img, cls=True)

        lines: List[str] = []
        if not result:
            return ""

        # result format: [[(box, (text, score)), ...]]
        for block in result:
            for _box, (text, _score) in block:
                if text and text.strip():
                    lines.append(text.strip())

        return "\n".join(lines)
