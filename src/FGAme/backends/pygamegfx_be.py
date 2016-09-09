from pygame import gfxdraw
from FGAme.draw import Color
from FGAme.backends.pygame_be import PyGameCanvas, PyGameInput, PyGameMainLoop
black = Color('black')


class PyGameGFXCanvas(PyGameCanvas):
    _gfx_circle_border = gfxdraw.aacircle
    _gfx_circle = gfxdraw.filled_circle
    _gfx_poly_border = gfxdraw.aapolygon
    _gfx_poly = gfxdraw.filled_polygon
    _gfx_line = gfxdraw.line

    def raw_circle_solid(self, circle, color=black):
        x, y = map(int, circle.pos)
        y = self.height - y
        r = int(circle.radius)
        self._gfx_circle(self._screen, x, y, r, color)
        self._gfx_circle_border(self._screen, x, y, r, color)

    def raw_circle_border(self, circle, width=1.0, color=black):
        if width == 1.0:
            x, y = map(int, circle.pos)
            y = self.height - y
            r = int(circle.radius)
            self._gfx_circle_border(self._screen, x, y, r, color)
        else:
            super(PyGameGFXCanvas, self) \
                .raw_circle_border(circle, width, color)

    def raw_poly_solid(self, poly, color=black):
        Y = self.height
        vertices = [(int(x), int(Y - y)) for (x, y) in poly]
        self._gfx_poly_border(self._screen, vertices, color)
        self._gfx_poly(self._screen, vertices, color)

    def raw_poly_border(self, poly, width=1.0, color=black):
        if width == 1.0:
            Y = self.height
            vertices = [(int(x), int(Y - y)) for (x, y) in poly]
            self._gfx_poly_border(self._screen, vertices, color)
        else:
            super(PyGameGFXCanvas, self) \
                .raw_poly_border(poly, width, color)

    def raw_segment(self, segment, width=1.0, color=black):
        Y = self.height
        pt1, pt2 = [(int(x), int(Y - y)) for (x, y) in segment]
        x1, y1 = pt1
        x2, y2 = pt2
        self._gfx_line(self._screen, x1, y1, x2, y2, color)
