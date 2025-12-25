from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict

from PySide6.QtCore import QStandardPaths


@dataclass(frozen=True)
class AppSettings:
    hotkey: str = "Ctrl+Shift+X"
    start_at_login: bool = False


def _settings_path() -> str:
    base = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
    if not base:
        base = os.path.join(os.path.expanduser("~"), ".config", "jp-assist-ai")
    return os.path.join(base, "settings.json")


def load_settings() -> AppSettings:
    path = _settings_path()
    if not os.path.exists(path):
        return AppSettings()

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        hotkey = str(data.get("hotkey", "")).strip()
        start_at_login = bool(data.get("start_at_login", False))
        if "hotkey" not in data:
            hotkey = AppSettings().hotkey
        return AppSettings(hotkey=hotkey, start_at_login=start_at_login)
    except Exception:
        return AppSettings()


def save_settings(settings: AppSettings) -> None:
    path = _settings_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(settings), f, indent=2)
