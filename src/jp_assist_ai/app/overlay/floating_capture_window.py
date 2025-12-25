from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime

from PIL import ImageQt, Image
from PySide6.QtCore import Qt, QPoint, QThread, Signal, QObject, QTimer
from PySide6.QtGui import QGuiApplication, QScreen
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QTextEdit,
    QColorDialog,
    QSizeGrip,
)

from jp_assist_ai.adapters.capture.mac_capture import capture_region, Region as CapRegion
from jp_assist_ai.app.overlay.annotation_canvas import AnnotationCanvas
from jp_assist_ai.services.translate_service import get_translator


@dataclass(frozen=True)
class CaptureResult:
    raw_path: str
    marked_path: str | None
    chat_path: str | None


class _TranslateWorker(QObject):
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, image: Image.Image, src_lang: str, dst_lang: str):
        super().__init__()
        self._image = image
        self._src = src_lang
        self._dst = dst_lang

    def run(self) -> None:
        try:
            translator = get_translator()
            result = translator.translate_image(self._image, self._src, self._dst)
            self.finished.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))


class _DragHandle(QLabel):
    def __init__(self, parent: QWidget):
        super().__init__("Drag", parent)
        self._offset = None  # type: QPoint | None
        self.setFixedSize(36, 22)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.SizeAllCursor)
        self.setStyleSheet("background: rgba(0,0,0,0.2); border-radius: 4px;")

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        self._offset = event.globalPosition().toPoint() - self.window().pos()

    def mouseMoveEvent(self, event):
        if self._offset is None:
            return
        self.window().move(event.globalPosition().toPoint() - self._offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._offset = None


class FloatingCaptureWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JP Assist AI")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMinimumSize(640, 420)

        self._thread = None
        self._worker = None
        self._base_image = None  # type: Image.Image | None
        self._scale_factor = 1.0

        self._canvas = AnnotationCanvas()
        self._canvas.setAttribute(Qt.WA_TranslucentBackground, True)
        self._canvas.setStyleSheet("background: transparent;")
        self._toolbar_widget = self._build_toolbar()
        self._chat_widget = self._build_chat()

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(8, 8, 8, 8)
        self._root.setSpacing(8)
        self._root.addWidget(self._toolbar_widget)
        self._root.addWidget(self._chat_widget)
        self._root.addWidget(self._canvas, 1)
        self._grip_widget = QWidget()
        grip_row = QHBoxLayout(self._grip_widget)
        grip_row.setContentsMargins(0, 0, 0, 0)
        grip_row.addStretch(1)
        grip_row.addWidget(QSizeGrip(self))
        self._root.addWidget(self._grip_widget)

        self._update_screen_buttons()

    def _build_toolbar(self) -> QWidget:
        wrapper = QWidget()
        row = QHBoxLayout(wrapper)

        self._drag = _DragHandle(self)
        self._btn_rect = QPushButton("Rectangle")
        self._btn_brush = QPushButton("Brush")
        self._btn_eraser = QPushButton("Eraser")
        self._btn_clear = QPushButton("Clear")
        self._btn_color = QPushButton("Color")

        self._btn_translate_sel = QPushButton("Translate highlight")
        self._btn_translate_all = QPushButton("Translate all")
        self._btn_capture = QPushButton("Capture")
        self._btn_screen1 = QPushButton("Screen 1")
        self._btn_screen2 = QPushButton("Screen 2")
        self._btn_cancel = QPushButton("Cancel")

        self._save_mode = QComboBox()
        self._save_mode.addItems(["Save: image only", "Save: with marks", "Save: with marks + chat"])

        row.addWidget(self._drag)
        for btn in [
            self._btn_rect,
            self._btn_brush,
            self._btn_eraser,
            self._btn_clear,
            self._btn_color,
        ]:
            row.addWidget(btn)

        row.addSpacing(8)
        row.addWidget(self._btn_translate_sel)
        row.addWidget(self._btn_translate_all)
        row.addSpacing(8)
        row.addWidget(self._save_mode)
        row.addWidget(self._btn_capture)
        row.addWidget(self._btn_screen1)
        row.addWidget(self._btn_screen2)
        row.addWidget(self._btn_cancel)
        row.addStretch(1)

        self._btn_rect.clicked.connect(lambda: self._canvas.set_mode(AnnotationCanvas.MODE_RECT))
        self._btn_brush.clicked.connect(lambda: self._canvas.set_mode(AnnotationCanvas.MODE_BRUSH))
        self._btn_eraser.clicked.connect(lambda: self._canvas.set_mode(AnnotationCanvas.MODE_ERASER))
        self._btn_clear.clicked.connect(self._canvas.clear)
        self._btn_color.clicked.connect(self._pick_color)
        self._btn_capture.clicked.connect(self._capture)
        self._btn_cancel.clicked.connect(self.close)
        self._btn_translate_sel.clicked.connect(self._translate_highlight)
        self._btn_translate_all.clicked.connect(self._translate_all)
        self._btn_screen1.clicked.connect(lambda: self._capture_screen(0))
        self._btn_screen2.clicked.connect(lambda: self._capture_screen(1))

        return wrapper

    def _build_chat(self) -> QWidget:
        widget = QWidget()
        wrapper = QVBoxLayout(widget)
        top = QHBoxLayout()
        top.addWidget(QLabel("From:"))
        self._src_lang = QComboBox()
        self._src_lang.addItems(["JP", "EN", "VI"])
        self._src_lang.setCurrentText("JP")
        top.addWidget(self._src_lang)

        top.addWidget(QLabel("To:"))
        self._dst_lang = QComboBox()
        self._dst_lang.addItems(["VI", "EN", "JP"])
        self._dst_lang.setCurrentText("VI")
        top.addWidget(self._dst_lang)
        top.addStretch(1)

        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setMinimumHeight(120)

        wrapper.addLayout(top)
        wrapper.addWidget(self._output)
        return widget

    def _pick_color(self) -> None:
        color = QColorDialog.getColor(self._canvas.color(), self, "Select highlight color")
        if color.isValid():
            self._canvas.set_color(color)

    def _capture(self) -> None:
        result = self._capture_images()
        if result is None:
            return
        message = f"Saved: {result.raw_path}"
        if result.marked_path:
            message += f"\nSaved with marks: {result.marked_path}"
        if result.chat_path:
            message += f"\nSaved with chat: {result.chat_path}"
        self._output.setPlainText(message)

    def _capture_screen(self, index: int) -> None:
        screens = QGuiApplication.screens()
        if index >= len(screens):
            self._output.setPlainText("Screen not available.")
            return

        screen = screens[index]
        geo = screen.geometry()
        img = capture_region(CapRegion(geo.x(), geo.y(), geo.width(), geo.height()))
        os.makedirs("tmp", exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_path = os.path.join("tmp", f"screen_{index + 1}_{stamp}.png")
        img.save(raw_path)
        self._output.setPlainText(f"Saved screen {index + 1}: {raw_path}")

    def _update_screen_buttons(self) -> None:
        count = len(QGuiApplication.screens())
        self._btn_screen1.setEnabled(count >= 1)
        self._btn_screen2.setEnabled(count >= 2)

    def _capture_images(self) -> CaptureResult | None:
        if self._base_image is None:
            return None

        raw = self._base_image.copy()

        os.makedirs("tmp", exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_path = os.path.join("tmp", f"capture_{stamp}.png")
        raw.save(raw_path)

        marked_path = None
        chat_path = None
        if self._save_mode.currentIndex() == 1:
            marked = raw.copy()
            overlay = ImageQt.fromqimage(self._canvas.export_annotation())
            if self._scale_factor != 1.0:
                overlay = overlay.resize(raw.size, resample=Image.BILINEAR)
            marked.paste(overlay, (0, 0), overlay)
            marked_path = os.path.join("tmp", f"capture_{stamp}_marked.png")
            marked.save(marked_path)
        elif self._save_mode.currentIndex() == 2:
            marked = raw.copy()
            overlay = ImageQt.fromqimage(self._canvas.export_annotation())
            if self._scale_factor != 1.0:
                overlay = overlay.resize(raw.size, resample=Image.BILINEAR)
            marked.paste(overlay, (0, 0), overlay)
            marked_path = os.path.join("tmp", f"capture_{stamp}_marked.png")
            marked.save(marked_path)

            pixmap = self.grab()
            chat_path = os.path.join("tmp", f"capture_{stamp}_chat.png")
            pixmap.save(chat_path, "PNG")

        return CaptureResult(raw_path=raw_path, marked_path=marked_path, chat_path=chat_path)

    def _translate_all(self) -> None:
        if self._base_image is None:
            return
        self._run_translate(self._base_image.copy())

    def _translate_highlight(self) -> None:
        bounds = self._canvas.annotation_bounds()
        if bounds is None:
            self._output.setPlainText("No highlighted area to translate.")
            return
        if self._base_image is None:
            return
        if bounds.width() < 5 or bounds.height() < 5:
            return
        x, y, w, h = self._scale_bounds(bounds.x(), bounds.y(), bounds.width(), bounds.height())
        crop = self._base_image.crop((x, y, x + w, y + h))
        self._run_translate(crop)

    def _run_translate(self, image: Image.Image) -> None:
        self._output.setPlainText("Translating...")

        if self._thread is not None:
            self._thread.quit()
            self._thread.wait()

        self._thread = QThread()
        self._worker = _TranslateWorker(
            image=image,
            src_lang=self._src_lang.currentText(),
            dst_lang=self._dst_lang.currentText(),
        )
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_translation_done)
        self._worker.failed.connect(self._on_translation_error)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.start()

    def _on_translation_done(self, text: str) -> None:
        self._output.setPlainText(text)

    def _on_translation_error(self, msg: str) -> None:
        self._output.setPlainText(f"Translation failed: {msg}")

    def open_with_image(self, image: Image.Image, screen: QScreen | None) -> None:
        self._base_image = image
        if screen is None:
            screen = QGuiApplication.primaryScreen()
        geo = screen.availableGeometry()
        controls_height = (
            self._toolbar_widget.sizeHint().height()
            + self._chat_widget.sizeHint().height()
            + self._grip_widget.sizeHint().height()
            + 24
        )
        max_canvas_w = max(200, geo.width() - 40)
        max_canvas_h = max(200, geo.height() - controls_height)
        scale = min(1.0, max_canvas_w / image.width, max_canvas_h / image.height)
        self._scale_factor = 1.0 / scale if scale > 0 else 1.0
        disp_w = int(image.width * scale)
        disp_h = int(image.height * scale)
        qt_image = ImageQt.ImageQt(image).scaled(disp_w, disp_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._canvas.set_background(qt_image)
        self._canvas.setMinimumSize(disp_w, disp_h)
        self.resize(self.sizeHint())
        x = geo.x() + (geo.width() - self.width()) // 2
        y = geo.y() + (geo.height() - self.height()) // 2
        self.move(x, y)
        self.show()
        QTimer.singleShot(0, self.activateWindow)

    def _scale_bounds(self, x: int, y: int, w: int, h: int) -> tuple[int, int, int, int]:
        if self._scale_factor == 1.0:
            return x, y, w, h
        sx = int(x * self._scale_factor)
        sy = int(y * self._scale_factor)
        sw = int(w * self._scale_factor)
        sh = int(h * self._scale_factor)
        if self._base_image is None:
            return sx, sy, sw, sh
        max_w, max_h = self._base_image.size
        sx = max(0, min(sx, max_w - 1))
        sy = max(0, min(sy, max_h - 1))
        sw = max(1, min(sw, max_w - sx))
        sh = max(1, min(sh, max_h - sy))
        return sx, sy, sw, sh
