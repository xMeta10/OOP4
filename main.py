import sys
from abc import ABC, abstractmethod

from PyQt6.QtCore import QPoint, QPointF, QRect, Qt, QSize, pyqtSignal
from PyQt6.QtGui import (
    QAction,
    QColor,
    QPainter,
    QPen,
    QBrush,
    QPolygonF,
    QKeyEvent,
    QMouseEvent,
    QPainterPath,
)
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QToolBar,
    QColorDialog,
    QStatusBar,
)

WINDOW_TITLE = "Лабораторная работа 4"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_MIN_SIZE = QSize(900, 600)

CANVAS_BACKGROUND_COLOR = QColor(245, 245, 245)

DEFAULT_SHAPE_WIDTH = 120
DEFAULT_SHAPE_HEIGHT = 80
MIN_SHAPE_SIZE = 24

DEFAULT_FILL_COLOR = QColor(100, 181, 246)
DEFAULT_BORDER_COLOR = QColor(33, 33, 33)

SELECTED_BORDER_COLOR = QColor(230, 81, 0)
SELECTED_BORDER_WIDTH = 3
DEFAULT_BORDER_WIDTH = 2

MOVE_STEP = 10
RESIZE_STEP = 10

STATUS_READY = "Готово"

class BaseShape(ABC):

    def __init__(self, rect: QRect):
        self._rect = QRect(rect)
        self._fill_color = QColor(DEFAULT_FILL_COLOR)
        self._border_color = QColor(DEFAULT_BORDER_COLOR)
        self._is_selected = False

    def rect(self):
        return QRect(self._rect)

    def select(self):
        self._is_selected = True

    def deselect(self):
        self._is_selected = False

    def toggle_selection(self):
        self._is_selected = not self._is_selected

    def is_selected(self):
        return self._is_selected

    def set_fill_color(self, color: QColor):
        self._fill_color = QColor(color)

    def move_by(self, dx, dy, canvas_rect):
        next_rect = QRect(self._rect)
        next_rect.translate(dx, dy)

        if not canvas_rect.contains(next_rect):
            return False

        self._rect = next_rect
        return True

    def resize_by(self, dw, dh, canvas_rect):
        next_rect = self._build_resized_rect(dw, dh)

        if next_rect.width() < MIN_SHAPE_SIZE:
            return False

        if next_rect.height() < MIN_SHAPE_SIZE:
            return False

        if not canvas_rect.contains(next_rect):
            return False

        self._rect = next_rect
        return True

    def ensure_inside(self, canvas_rect):
        return canvas_rect.contains(self._rect)

    def draw(self, painter: QPainter):

        painter.setPen(QPen(self._border_color, DEFAULT_BORDER_WIDTH))
        painter.setBrush(QBrush(self._fill_color))

        self._draw_shape(painter)

        if self._is_selected:
            pen = QPen(
                SELECTED_BORDER_COLOR,
                SELECTED_BORDER_WIDTH,
                Qt.PenStyle.DashLine,
            )
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self._rect.adjusted(-3, -3, 3, 3))

    def _build_resized_rect(self, dw, dh):
        new_width = self._rect.width() + dw
        new_height = self._rect.height() + dh

        center = self._rect.center()

        rect = QRect(0, 0, new_width, new_height)
        rect.moveCenter(center)

        return rect

    @abstractmethod
    def contains_point(self, point):
        pass

    @abstractmethod
    def _draw_shape(self, painter):
        pass


