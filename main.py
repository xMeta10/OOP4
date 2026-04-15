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

class RectangleShape(BaseShape):

    def contains_point(self, point):
        return self._rect.contains(point)

    def _draw_shape(self, painter):
        painter.drawRect(self._rect)


class SquareShape(RectangleShape):

    def _build_resized_rect(self, dw, dh):

        delta = dw if abs(dw) > abs(dh) else dh
        new_size = self._rect.width() + delta

        center = self._rect.center()

        rect = QRect(0, 0, new_size, new_size)
        rect.moveCenter(center)

        return rect


class EllipseShape(BaseShape):

    def contains_point(self, point):

        rx = self._rect.width() / 2
        ry = self._rect.height() / 2

        cx = self._rect.center().x()
        cy = self._rect.center().y()

        dx = point.x() - cx
        dy = point.y() - cy

        return (dx * dx) / (rx * rx) + (dy * dy) / (ry * ry) <= 1

    def _draw_shape(self, painter):
        painter.drawEllipse(self._rect)


class CircleShape(EllipseShape):

    def _build_resized_rect(self, dw, dh):

        delta = dw if abs(dw) > abs(dh) else dh
        new_size = self._rect.width() + delta

        center = self._rect.center()

        rect = QRect(0, 0, new_size, new_size)
        rect.moveCenter(center)

        return rect


class TriangleShape(BaseShape):

    def _polygon(self):

        top = QPointF(self._rect.center().x(), self._rect.top())
        left = QPointF(self._rect.left(), self._rect.bottom())
        right = QPointF(self._rect.right(), self._rect.bottom())

        return QPolygonF([top, left, right])

    def contains_point(self, point):

        path = QPainterPath()
        path.addPolygon(self._polygon())

        return path.contains(QPointF(point))

    def _draw_shape(self, painter):
        painter.drawPolygon(self._polygon())

class ShapeFactory:

    RECTANGLE = "rectangle"
    SQUARE = "square"
    ELLIPSE = "ellipse"
    CIRCLE = "circle"
    TRIANGLE = "triangle"

    TITLES = {
        RECTANGLE: "Прямоугольник",
        SQUARE: "Квадрат",
        ELLIPSE: "Эллипс",
        CIRCLE: "Круг",
        TRIANGLE: "Треугольник",
    }

    @classmethod
    def create(cls, shape_type, point):

        if shape_type == cls.RECTANGLE:
            return RectangleShape(
                QRect(point.x(), point.y(), DEFAULT_SHAPE_WIDTH, DEFAULT_SHAPE_HEIGHT)
            )

        if shape_type == cls.SQUARE:
            return SquareShape(
                QRect(point.x(), point.y(), DEFAULT_SHAPE_WIDTH, DEFAULT_SHAPE_WIDTH)
            )

        if shape_type == cls.ELLIPSE:
            return EllipseShape(
                QRect(point.x(), point.y(), DEFAULT_SHAPE_WIDTH, DEFAULT_SHAPE_HEIGHT)
            )

        if shape_type == cls.CIRCLE:
            return CircleShape(
                QRect(point.x(), point.y(), DEFAULT_SHAPE_WIDTH, DEFAULT_SHAPE_WIDTH)
            )

        if shape_type == cls.TRIANGLE:
            return TriangleShape(
                QRect(point.x(), point.y(), DEFAULT_SHAPE_WIDTH, DEFAULT_SHAPE_HEIGHT)
            )

    @classmethod
    def get_title(cls, shape_type):
        return cls.TITLES[shape_type]

class ShapeStorage:

    def __init__(self):
        self._items = []

    def add(self, shape):
        self._items.append(shape)

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def clear_selection(self):

        for s in self._items:
            s.deselect()

    def selected_shapes(self):

        return [s for s in self._items if s.is_selected()]

    def remove_selected(self):

        before = len(self._items)
        self._items = [s for s in self._items if not s.is_selected()]
        return before - len(self._items)

    def get_shapes_at_point(self, point):

        result = []

        for s in reversed(self._items):
            if s.contains_point(point):
                result.append(s)

        return result

    def bring_to_front(self, target):

        if target not in self._items:
            return

        self._items.remove(target)
        self._items.append(target)

class EditorController:

    def __init__(self, storage):
        self._storage = storage

    def add_shape(self, shape_type, point, canvas_rect):

        shape = ShapeFactory.create(shape_type, point)

        if not shape.ensure_inside(canvas_rect):
            return None

        self._storage.add(shape)
        self._storage.bring_to_front(shape)

        return shape

    def handle_click_selection(self, point, ctrl_pressed):

        shapes = self._storage.get_shapes_at_point(point)

        if not shapes:

            if not ctrl_pressed:
                self._storage.clear_selection()

            return None

        top = shapes[0]

        if ctrl_pressed:
            top.toggle_selection()
        else:
            self._storage.clear_selection()
            top.select()

        self._storage.bring_to_front(top)

        return top

    def delete_selected(self):
        return self._storage.remove_selected()

    def move_selected(self, dx, dy, canvas_rect):

        moved = 0

        for s in self._storage.selected_shapes():
            if s.move_by(dx, dy, canvas_rect):
                moved += 1

        return moved

    def resize_selected(self, dw, dh, canvas_rect):

        resized = 0

        for s in self._storage.selected_shapes():
            if s.resize_by(dw, dh, canvas_rect):
                resized += 1

        return resized

    def recolor_selected(self, color):

        count = 0

        for s in self._storage.selected_shapes():
            s.set_fill_color(color)
            count += 1

        return count

    def get_shape_title(self, shape_type):
        return ShapeFactory.get_title(shape_type)

class CanvasWidget(QWidget):

    status_message_changed = pyqtSignal(str)

    def __init__(self, storage, controller, parent=None):
        super().__init__(parent)

        self._storage = storage
        self._controller = controller
        self._current_tool = ShapeFactory.RECTANGLE

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), CANVAS_BACKGROUND_COLOR)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def set_current_tool(self, tool):
        self._current_tool = tool

    def tool_label(self):
        return self._controller.get_shape_title(self._current_tool)

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for shape in self._storage:
            shape.draw(painter)

    def mousePressEvent(self, event: QMouseEvent):

        if event.button() != Qt.MouseButton.LeftButton:
            return

        point = event.position().toPoint()

        ctrl = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)

        selected = self._controller.handle_click_selection(point, ctrl)

        if selected is None:

            shape = self._controller.add_shape(
                self._current_tool,
                point,
                self.rect(),
            )

            if shape:
                self._storage.clear_selection()
                shape.select()

        self.update()

    def keyPressEvent(self, event: QKeyEvent):

        key = event.key()
        shift = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        ctrl = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)

        if key == Qt.Key.Key_Delete:

            self._controller.delete_selected()
            self.update()
            return

        if ctrl and shift and key == Qt.Key.Key_C:

            color = QColorDialog.getColor(parent=self)

            if color.isValid():
                self._controller.recolor_selected(color)

            self.update()
            return

        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):

            if shift:
                self._resize_key(key)
            else:
                self._move_key(key)

            self.update()

    def _move_key(self, key):

        dx = 0
        dy = 0

        if key == Qt.Key.Key_Left:
            dx = -MOVE_STEP
        elif key == Qt.Key.Key_Right:
            dx = MOVE_STEP
        elif key == Qt.Key.Key_Up:
            dy = -MOVE_STEP
        elif key == Qt.Key.Key_Down:
            dy = MOVE_STEP

        self._controller.move_selected(dx, dy, self.rect())

    def _resize_key(self, key):

        dw = 0
        dh = 0

        if key == Qt.Key.Key_Left:
            dw = -RESIZE_STEP
        elif key == Qt.Key.Key_Right:
            dw = RESIZE_STEP
        elif key == Qt.Key.Key_Up:
            dh = -RESIZE_STEP
        elif key == Qt.Key.Key_Down:
            dh = RESIZE_STEP

        self._controller.resize_selected(dw, dh, self.rect())

