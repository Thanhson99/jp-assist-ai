from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, QRect, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QGuiApplication


@dataclass(frozen=True)
class Region:
    x: int
    y: int
    w: int
    h: int


class _FrameOverlay(QWidget):
    regionSelected = Signal(object)
    cancelled = Signal()

    def __init__(self, screen_geo: QRect):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint
            | Qt.FramelessWindowHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow, True)
        self.setCursor(Qt.CrossCursor)
        self.setGeometry(screen_geo)

        self._start = None  # type: tuple[int, int] | None
        self._end = None  # type: tuple[int, int] | None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            p = event.globalPosition()
            self._start = (int(p.x()), int(p.y()))
            self._end = self._start
            self.update()

    def mouseMoveEvent(self, event):
        if self._start is not None:
            p = event.globalPosition()
            self._end = (int(p.x()), int(p.y()))
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._start and self._end:
            x1, y1 = self._start
            x2, y2 = self._end
            x = int(min(x1, x2))
            y = int(min(y1, y2))
            w = int(abs(x2 - x1))
            h = int(abs(y2 - y1))

            if w > 5 and h > 5:
                self.regionSelected.emit(Region(x=x, y=y, w=w, h=h))
            else:
                self.cancelled.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.cancelled.emit()

    def _rect(self) -> QRect | None:
        if not (self._start and self._end):
            return None
        x1g, y1g = self._start
        x2g, y2g = self._end

        gx = self.geometry().left()
        gy = self.geometry().top()

        x1 = x1g - gx
        y1 = y1g - gy
        x2 = x2g - gx
        y2 = y2g - gy

        return QRect(
            int(min(x1, x2)),
            int(min(y1, y2)),
            int(abs(x2 - x1)),
            int(abs(y2 - y1)),
        )

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        rect = self._rect()
        if rect:
            pen = QPen(QColor(0, 180, 255, 230))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(rect)


class RegionFrameSelector(QWidget):
    regionSelected = Signal(object)

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self._overlays: list[_FrameOverlay] = []

        screens = QGuiApplication.screens()
        if not screens:
            ov = _FrameOverlay(QGuiApplication.primaryScreen().geometry())
            self._attach_overlay(ov)
            return

        for s in screens:
            ov = _FrameOverlay(s.geometry())
            self._attach_overlay(ov)

    def _attach_overlay(self, ov: _FrameOverlay) -> None:
        ov.regionSelected.connect(self._on_region_selected)
        ov.cancelled.connect(self.close)
        self._overlays.append(ov)

    def show(self) -> None:
        for ov in self._overlays:
            ov.show()
            ov.raise_()
            ov.activateWindow()

    def close(self) -> None:
        for ov in self._overlays:
            try:
                ov.close()
            except Exception:
                pass
        self._overlays.clear()
        super().close()

    def _on_region_selected(self, region: Region) -> None:
        self.regionSelected.emit(region)
        self.close()
