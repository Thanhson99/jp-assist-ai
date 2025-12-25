from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QKeySequence

try:
    from qhotkey import QHotkey
    _QHOTKEY_AVAILABLE = True
except Exception:
    QHotkey = None
    _QHOTKEY_AVAILABLE = False

try:
    from pynput import keyboard as _pynput_keyboard
    _PYNPUT_AVAILABLE = True
except Exception:
    _pynput_keyboard = None
    _PYNPUT_AVAILABLE = False


class GlobalHotkey(QObject):
    activated = Signal()

    def __init__(self, sequence: str, parent: QObject | None = None):
        super().__init__(parent)
        self._hotkey = None
        self._listener = None
        self._sequence = ""
        self.set_sequence(sequence)

    def available(self) -> bool:
        return _QHOTKEY_AVAILABLE or _PYNPUT_AVAILABLE

    def is_registered(self) -> bool:
        if self._hotkey is not None:
            return bool(self._hotkey.isRegistered())
        return self._listener is not None

    def set_sequence(self, sequence: str) -> None:
        if self._hotkey is not None:
            try:
                self._hotkey.activated.disconnect(self.activated.emit)
            except Exception:
                pass
            self._hotkey.deleteLater()
            self._hotkey = None
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

        self._sequence = sequence.strip() if sequence else ""
        if not self._sequence:
            return

        if _QHOTKEY_AVAILABLE:
            self._hotkey = QHotkey(QKeySequence(self._sequence), autoRegister=True, parent=self)
            self._hotkey.activated.connect(self.activated.emit)
            return

        if _PYNPUT_AVAILABLE:
            hotkey = _to_pynput_hotkey(self._sequence)
            if not hotkey:
                return
            self._listener = _pynput_keyboard.GlobalHotKeys({hotkey: self.activated.emit})
            self._listener.start()


def _to_pynput_hotkey(sequence: str) -> str:
    parts = [p.strip() for p in sequence.split("+") if p.strip()]
    if not parts:
        return ""

    mods = {
        "ctrl": "<ctrl>",
        "control": "<ctrl>",
        "shift": "<shift>",
        "alt": "<alt>",
        "option": "<alt>",
        "meta": "<cmd>",
        "cmd": "<cmd>",
        "command": "<cmd>",
    }

    mapped: list[str] = []
    for part in parts:
        key = part.lower()
        if key in mods:
            mapped.append(mods[key])
            continue
        if key == "space":
            mapped.append("<space>")
            continue
        if len(key) == 1:
            mapped.append(key)
            continue
        return ""

    return "+".join(mapped)
