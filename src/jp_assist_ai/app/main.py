from __future__ import annotations

from PySide6.QtWidgets import QApplication

from jp_assist_ai.app.tray import TrayApp


def main():
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    tray = TrayApp()
    tray.show()
    app.exec()


if __name__ == "__main__":
    main()
