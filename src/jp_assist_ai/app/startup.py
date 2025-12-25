from __future__ import annotations

import os
import plistlib
import sys
from pathlib import Path


def _project_root() -> Path:
    here = Path(__file__).resolve()
    return here.parents[3]


def _plist_path() -> Path:
    return Path(os.path.expanduser("~/Library/LaunchAgents/com.jp-assist-ai.plist"))


def _plist_payload() -> dict:
    program = [sys.executable, "-m", "jp_assist_ai.app.main"]
    payload: dict = {
        "Label": "com.jp-assist-ai",
        "ProgramArguments": program,
        "RunAtLoad": True,
        "KeepAlive": False,
    }

    root = _project_root()
    src_path = root / "src" / "jp_assist_ai"
    if src_path.exists():
        payload["WorkingDirectory"] = str(root)
        payload["EnvironmentVariables"] = {"PYTHONPATH": str(root / "src")}

    return payload


def set_start_at_login(enabled: bool) -> bool:
    try:
        path = _plist_path()
        if enabled:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f:
                plistlib.dump(_plist_payload(), f)
        else:
            if path.exists():
                path.unlink()
        return True
    except Exception:
        return False
