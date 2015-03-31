from FGAme.backends.pygame import PyGameCanvas

class PyGameGFXCanvas(PyGameCanvas):
    '''Implementa a interface Canvas, utilizando a biblioteca Pygame e as 
    funções pygame.gfxdraw, ao invés das usuais pygame.draw'''

    def init(self):
        import pygame.gfxdraw
        self.gfx = pygame.gfxdraw
        super(PyGameGFXCanvas, self).init()

    def paint_circle(self, pos, radius, color='black', solid=True):
        x, y = self._map_point(pos)
        color = Color(color)
        self.gfx.aacircle(self._screen, x, y, trunc(radius), color)
        if solid:
            self.gfx.filled_circle(self._screen, x, y, trunc(radius), color)

    def draw_poly(self, points, color='black', solid=True):
        points = [ self._map_point(pt) for pt in points ]
        color = Color(color)
        self.pygame.gfxdraw.aapolygon(self._screen, points, color)
        if solid:
            self.pygame.gfxdraw.filled_polygon(self._screen, points, color)