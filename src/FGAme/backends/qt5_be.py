import sys
import time
from functools import partial

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.Qt import QColor
from PyQt5.QtCore import QPointF

from FGAme import draw
from FGAme.draw import Color
from FGAme.input import Input
from FGAme.mainloop import MainLoop
from FGAme.screen import Screen

black = Color('black')
white = Color('white')


class QFGAmeWindow(QtWidgets.QWidget):
    def __init__(self, parent=None, *, shape=None, title=None):
        super().__init__(parent)
        if shape:
            width, height = shape
            self.setFixedSize(*shape)
        else:
            raise TypeError('shape must be set!')
        if title:
            self.setWindowTitle(title)

        self._scene = QtWidgets.QGraphicsScene()
        self._view = QtWidgets.QGraphicsView(self._scene)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self._view)
        self._view.setAlignment(QtCore.Qt.Alignment(0))
        self._view.scale(1, -1)
        self._view.translate(-width / 2, -height / 2)

    def runner(self):
        return self._runner

    def setRunner(self, runner, dt):
        self._runner = runner
        self._interval = dt
        self.startTimer(dt)

    def timerEvent(self, timer):
        self._runner(self._interval)

    def scene(self):
        return self._scene

    def view(self):
        return self._view


class QtScreen(Screen):
    """Implementa a interface Canvas utilizando a biblioteca Qt"""

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self._brushes = {}
        self.application = QtWidgets.QApplication(sys.argv)
        self.window = QFGAmeWindow(title='FGAme game', shape=self.shape)
        self.scene = self.window.scene()
        self.view = self.window.view()

    def show(self):
        super().show()
        self.window.show()

    def set_runner(self, runner, dt):
        self.window.setRunner(runner, dt)

    def get_brush(self, color):
        try:
            return self._brushes[color]
        except KeyError:
            R, G, B, A = color
            brush = QtGui.QBrush(QColor(R, G, B, A))
            self._brushes[color] = brush
            return brush

    def get_handle(self, obj):
        if isinstance(obj, draw.Poly):
            poly = QtGui.QPolygonF([QPointF(*pt) for pt in obj])
            handle = QtWidgets.QGraphicsPolygonItem(poly)
        elif isinstance(obj, draw.AABB):
            x, y, dx, dy = obj.rect
            y -= dy
            handle = QtWidgets.QGraphicsRectItem(x, y, dx, dy)
        elif isinstance(obj, draw.Circle):
            x, y = obj.pos
            r = obj.radius
            handle = QtWidgets.QGraphicsEllipseItem(x, y, r, r)
        else:
            print(obj, type(obj))
            return None

        handle.setBrush(self.get_brush(obj.color))
        self.scene.addItem(handle)
        return handle

    def update_handle(self, handle, obj):
        handle.setPos(*obj.pos)


class QtInput(Input):
    def poll(self):
        pass


class QtMainLoop(MainLoop):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.application = self.screen.application

    def run(self, state, timeout=None, maxiter=None, wait=True):
        dt = self.dt
        runner = partial(self.main_runner, state)
        self.screen.show()
        self.screen.set_runner(runner, dt)
        sys.exit(self.application.exec_())

    def main_runner(self, state, dt):
        start_time = time.time()
        self.trigger_frame_enter()

        # Update one shot actions
        Q = self._action_queue
        while Q and (self.time > Q[0].time):
            x = Q.popleft()
            x.action(*x.args, **x.kwds)

        self.input.poll()
        state.update(self.dt)

        # Draw objects
        self.trigger_pre_draw(self.screen)
        state.render_tree().screen_update(self.screen)
        self.trigger_post_draw(self.screen)

        # Finish frame
        time_interval = time.time() - start_time
        self.sleep_time = self.dt - time_interval
        self.trigger_frame_leave()
