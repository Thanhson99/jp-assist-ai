from __future__ import annotations

from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QColor, QImage, QPainter, QPen
from PySide6.QtWidgets import QWidget


class AnnotationCanvas(QWidget):
    MODE_RECT = "rect"
    MODE_BRUSH = "brush"
    MODE_ERASER = "eraser"

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self._mode = self.MODE_RECT
        self._base_color = QColor(255, 230, 0)
        self._fill_alpha = 50
        self._stroke_alpha = 200
        self._brush_alpha = 80
        self._pen_width = 14
        self._background = None  # type: QImage | None
        self._image = QImage(self.size(), QImage.Format_ARGB32_Premultiplied)
        self._image.fill(Qt.transparent)
        self._start = None  # type: QPoint | None
        self._end = None  # type: QPoint | None
        self._last = None  # type: QPoint | None

    def set_mode(self, mode: str) -> None:
        self._mode = mode
        self._start = None
        self._end = None
        self._last = None

    def set_color(self, color: QColor) -> None:
        self._base_color = QColor(color)
        self._base_color.setAlpha(255)
        self.update()

    def color(self) -> QColor:
        return QColor(self._base_color)

    def _fill_color(self) -> QColor:
        color = QColor(self._base_color)
        color.setAlpha(self._fill_alpha)
        return color

    def _stroke_color(self) -> QColor:
        color = QColor(self._base_color)
        color.setAlpha(self._stroke_alpha)
        return color

    def _brush_color(self) -> QColor:
        color = QColor(self._base_color)
        color.setAlpha(self._brush_alpha)
        return color

    def clear(self) -> None:
        self._image.fill(Qt.transparent)
        self.update()

    def set_background(self, image: QImage) -> None:
        self._background = image
        if not image.isNull():
            self._image = QImage(image.size(), QImage.Format_ARGB32_Premultiplied)
            self._image.fill(Qt.transparent)
            self.resize(image.size())
        self.update()

    def background_size(self) -> tuple[int, int]:
        if self._background is None:
            return (0, 0)
        return (self._background.width(), self._background.height())

    def annotation_bounds(self) -> QRect | None:
        if self._image.isNull():
            return None
        rect = self._image.rect()
        min_x, min_y = rect.right(), rect.bottom()
        max_x, max_y = rect.left(), rect.top()
        found = False
        for y in range(rect.top(), rect.bottom() + 1):
            for x in range(rect.left(), rect.right() + 1):
                if QColor(self._image.pixel(x, y)).alpha() > 0:
                    found = True
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
        if not found:
            return None
        return QRect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    def resizeEvent(self, event):
        if self.width() <= 0 or self.height() <= 0:
            return
        if self._image.size() == event.size():
            return
        new_img = QImage(event.size(), QImage.Format_ARGB32_Premultiplied)
        new_img.fill(Qt.transparent)
        painter = QPainter(new_img)
        painter.drawImage(0, 0, self._image)
        painter.end()
        self._image = new_img

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        if self._mode == self.MODE_RECT:
            self._start = event.position().toPoint()
            self._end = self._start
        else:
            self._last = event.position().toPoint()
            self._draw_line(self._last, self._last)
        self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.LeftButton:
            return
        if self._mode == self.MODE_RECT and self._start:
            self._end = event.position().toPoint()
        else:
            current = event.position().toPoint()
            self._draw_line(self._last, current)
            self._last = current
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        if self._mode == self.MODE_RECT and self._start and self._end:
            self._draw_rect(self._start, self._end)
        self._start = None
        self._end = None
        self._last = None
        self.update()

    def _draw_rect(self, start: QPoint, end: QPoint) -> None:
        rect = QRect(start, end).normalized()
        painter = QPainter(self._image)
        painter.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(self._stroke_color())
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(self._fill_color())
        painter.drawRect(rect)
        painter.end()

    def _draw_line(self, start: QPoint | None, end: QPoint) -> None:
        if start is None:
            return
        painter = QPainter(self._image)
        painter.setRenderHint(QPainter.Antialiasing, True)
        if self._mode == self.MODE_ERASER:
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            pen = QPen(Qt.transparent)
        else:
            pen = QPen(self._brush_color())
        pen.setWidth(self._pen_width)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(start, end)
        painter.end()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        if self._background is not None:
            painter.drawImage(0, 0, self._background)
        painter.setPen(QPen(QColor(0, 180, 255, 200), 2))
        painter.drawRect(self.rect().adjusted(1, 1, -2, -2))
        painter.drawImage(0, 0, self._image)
        if self._mode == self.MODE_RECT and self._start and self._end:
            rect = QRect(self._start, self._end).normalized()
            pen = QPen(self._stroke_color())
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(self._fill_color())
            painter.drawRect(rect)
        painter.end()

    def export_annotation(self) -> QImage:
        return self._image.copy()
