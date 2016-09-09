from math import trunc

import pyglet
from FGAme.screen import Canvas


class PyGletCanvas(Canvas):
    def __init__(self, width, height, **kwargs):
        global WINDOW

        super().__init__(width, height, **kwargs)
        self._window = pyglet.window.Window(width, height)
        WINDOW = self._window

    def show(self):
        self._window.flip()

    def _map_point(self, point):
        x, y = super()._map_point(point)
        X, Y = self.width, self.height
        x += 0.5 * X
        y = 0.5 * Y - y
        return (trunc(x), trunc(y))

    def draw_circle(self, pos, radius, fillcolor=(0, 0, 0), solid=True):
        pos = self._map_point(pos)
        # pygame.draw.circle(self._screen, fillcolor, pos, trunc(radius))

    def draw_poly(self, points, fillcolor=(0, 0, 0), solid=True):
        points = [self._map_point(pt) for pt in points]
        # pygame.draw.polygon(self._screen, fillcolor, points)

    def draw_rect(self, pos, shape, color=(0, 0, 0), solid=True):
        x, y = self._map_point(pos)
        dx, dy = shape
        dx = trunc(dx * self.zoom)
        dy = trunc(dy * self.zoom)
        y -= dy
        # pygame.draw.rect(self._screen, color, (x, y, dx, dy))
        pyglet.graphics.draw(2, pyglet.gl.GL_POINTS,
                             ('v2i', (10, 15, 30, 35))
                             )

    def draw_line(self, pt1, pt2, color=(0, 0, 0), solid=True):
        raise NotImplementedError

    def clear(self, color=None):
        # color = color or self.background
        # self._screen.fill(color)
        self._window.clear()
        R, G, B = self.background
        pyglet.gl.glClearColor(R / 255., G / 255., B / 255., 1)

        win = self._window
        verts = [(win.width * 0.9, win.height * 0.9),
                 (win.width * 0.5, win.height * 0.1),
                 (win.width * 0.1, win.height * 0.9), ]
        colors = [(255, 000, 000),
                  (000, 255, 000),
                  (000, 000, 255), ]
        glBegin(GL_TRIANGLES)
        for idx in range(len(verts)):
            glColor3ub(*colors[idx])
            glVertex2f(*verts[idx])
        glEnd()
