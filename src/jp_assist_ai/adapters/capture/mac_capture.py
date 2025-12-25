from __future__ import annotations

from dataclasses import dataclass
from PIL import Image
import mss


@dataclass(frozen=True)
class Region:
    x: int
    y: int
    w: int
    h: int


def _clip(val: int, lo: int, hi: int) -> int:
    return max(lo, min(val, hi))


def capture_region(region: Region) -> Image.Image:
    with mss.mss() as sct:
        desktop = sct.monitors[0]  # virtual desktop across all displays
        left0, top0 = desktop["left"], desktop["top"]
        right0 = left0 + desktop["width"]
        bot0 = top0 + desktop["height"]

        x1 = int(region.x)
        y1 = int(region.y)
        x2 = int(region.x + region.w)
        y2 = int(region.y + region.h)

        # Clip to virtual desktop bounds to avoid out-of-range grabs (often returns black)
        x1 = _clip(x1, left0, right0 - 1)
        y1 = _clip(y1, top0, bot0 - 1)
        x2 = _clip(x2, left0 + 1, right0)
        y2 = _clip(y2, top0 + 1, bot0)

        monitor = {"left": x1, "top": y1, "width": x2 - x1, "height": y2 - y1}
        shot = sct.grab(monitor)
        return Image.frombytes("RGB", shot.size, shot.rgb)
