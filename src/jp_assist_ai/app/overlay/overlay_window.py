from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QApplication


class OverlayWindow(QWidget):
    def __init__(self, title: str, text: str):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setMinimumSize(560, 320)

        root = QVBoxLayout(self)

        btn_row = QHBoxLayout()
        copy_btn = QPushButton("Copy")
        close_btn = QPushButton("Close (ESC)")
        btn_row.addWidget(copy_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(close_btn)
        root.addLayout(btn_row)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setText(f"{title}\n\n{text}".strip())
        root.addWidget(self.text)

        copy_btn.clicked.connect(self._copy)
        close_btn.clicked.connect(self.close)

    def _copy(self):
        QApplication.clipboard().setText(self.text.toPlainText())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
