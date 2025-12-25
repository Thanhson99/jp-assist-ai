from __future__ import annotations

from PySide6.QtCore import QObject, QPoint
from PySide6.QtGui import QIcon, QAction, QGuiApplication
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QMenu,
    QStyle,
    QSystemTrayIcon,
    QMessageBox,
)

from jp_assist_ai.app.overlay.floating_capture_window import FloatingCaptureWindow
from jp_assist_ai.app.overlay.region_frame_selector import RegionFrameSelector, Region as UiRegion
from jp_assist_ai.adapters.capture.mac_capture import capture_region, Region as CapRegion
from jp_assist_ai.app.screens.settings_window import SettingsWindow
from jp_assist_ai.app.startup import set_start_at_login
from jp_assist_ai.config.settings import AppSettings, load_settings, save_settings
from jp_assist_ai.adapters.hotkeys.mac_hotkeys import GlobalHotkey


class _CaptureController(QObject):
    def __init__(self):
        super().__init__()
        self._window: FloatingCaptureWindow | None = None
        self._selector: RegionFrameSelector | None = None

    def start_capture(self) -> None:
        if self._selector is not None:
            return
        selector = RegionFrameSelector()
        selector.regionSelected.connect(self._on_region)
        selector.destroyed.connect(self._on_selector_destroyed)
        self._selector = selector
        selector.show()

    def _on_window_destroyed(self) -> None:
        self._window = None

    def _on_selector_destroyed(self) -> None:
        self._selector = None

    def _on_region(self, region: UiRegion) -> None:
        if self._window is None:
            self._window = FloatingCaptureWindow()
            self._window.destroyed.connect(self._on_window_destroyed)
        img = capture_region(CapRegion(region.x, region.y, region.w, region.h))
        screen = QGuiApplication.screenAt(QPoint(region.x, region.y))
        self._window.open_with_image(img, screen)


class TrayApp(QObject):
    def __init__(self):
        super().__init__()
        self._settings = load_settings()
        self._capture = _CaptureController()
        self._hotkey = GlobalHotkey(self._settings.hotkey, parent=self)
        self._hotkey.activated.connect(self._capture.start_capture)

        self._tray = QSystemTrayIcon(self._tray_icon())
        self._tray.setToolTip("JP Assist AI")

        menu = QMenu()
        self._action_capture = QAction("Capture region")
        self._action_settings = QAction("Set hotkey...")
        self._action_startup = QAction("Start at login")
        self._action_startup.setCheckable(True)
        self._action_startup.setChecked(self._settings.start_at_login)
        self._action_quit = QAction("Quit")

        self._action_capture.triggered.connect(self._capture.start_capture)
        self._action_settings.triggered.connect(self._open_settings)
        self._action_startup.toggled.connect(self._toggle_startup)
        self._action_quit.triggered.connect(QApplication.quit)

        menu.addAction(self._action_capture)
        menu.addSeparator()
        menu.addAction(self._action_settings)
        menu.addAction(self._action_startup)
        menu.addSeparator()
        menu.addAction(self._action_quit)

        self._tray.setContextMenu(menu)

    def show(self) -> None:
        self._tray.show()
        self._ensure_hotkey_registered()
        if self._settings.start_at_login:
            set_start_at_login(True)

    def _tray_icon(self) -> QIcon:
        icon = QIcon.fromTheme("camera")
        if icon.isNull():
            icon = QApplication.style().standardIcon(QStyle.SP_DesktopIcon)
        return icon

    def _open_settings(self) -> None:
        dialog = SettingsWindow(self._settings.hotkey)
        QTimer.singleShot(0, dialog.raise_)
        QTimer.singleShot(0, dialog.activateWindow)
        if dialog.exec() != QDialog.Accepted:
            return

        new_hotkey = dialog.selected_hotkey()
        if new_hotkey == self._settings.hotkey:
            return

        self._settings = AppSettings(hotkey=new_hotkey)
        save_settings(self._settings)
        self._hotkey.set_sequence(new_hotkey)
        self._ensure_hotkey_registered()

    def _ensure_hotkey_registered(self) -> None:
        if not self._settings.hotkey:
            return

        if not self._hotkey.available():
            QMessageBox.warning(
                None,
                "Hotkey unavailable",
                "Global hotkey support is not available. Install QHotkey or pynput.",
            )
            return

        if self._settings.hotkey and not self._hotkey.is_registered():
            QMessageBox.warning(
                None,
                "Hotkey not registered",
                f"Could not register hotkey: {self._settings.hotkey}",
            )

    def _toggle_startup(self, enabled: bool) -> None:
        if set_start_at_login(enabled):
            self._settings = AppSettings(
                hotkey=self._settings.hotkey,
                start_at_login=enabled,
            )
            save_settings(self._settings)
            self._tray.showMessage(
                "Start at login",
                "Enabled. It will start automatically on next login."
                if enabled
                else "Disabled.",
            )
            return

        self._action_startup.blockSignals(True)
        self._action_startup.setChecked(not enabled)
        self._action_startup.blockSignals(False)
        self._tray.showMessage(
            "Start at login",
            "Failed to update login item.",
        )
