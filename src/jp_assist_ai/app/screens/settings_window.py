from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QKeySequenceEdit,
    QVBoxLayout,
)


class SettingsWindow(QDialog):
    def __init__(self, hotkey: str):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setMinimumWidth(360)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        root = QVBoxLayout(self)

        row = QHBoxLayout()
        row.addWidget(QLabel("Capture hotkey:"))
        self._edit = QKeySequenceEdit()
        if hotkey:
            self._edit.setKeySequence(QKeySequence(hotkey))
        row.addWidget(self._edit)
        root.addLayout(row)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def selected_hotkey(self) -> str:
        return self._edit.keySequence().toString()
