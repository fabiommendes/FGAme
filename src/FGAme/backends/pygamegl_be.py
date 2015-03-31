from FGAme.backends.pygame import PyGameCanvas

class PyGameGLCanvas(PyGameCanvas):
    '''Implementa a interface Screen, utilizando a biblioteca Pygame'''

    def __init__(self, w, h, *args, **kwds):
        kwds['set_mode_args'] = [HWSURFACE|OPENGL|DOUBLEBUF]
        super(PyGameGLScreen, self).__init__(w, h, *args, **kwds)

    def show(self):
        pygame.display.flip()

    def draw_circle(self, pos, radius, color=(0, 0, 0), solid=True):
        x, y = self._map_point(pos)
        #pygame.gfxdraw.aacircle(self._screen, x, y, trunc(radius), color)
        #if solid:
        #    pygame.gfxdraw.filled_circle(self._screen, x, y, trunc(radius), color)

    def draw_poly(self, points, color=(0, 0, 0), solid=True):
        points = [ self._map_point(pt) for pt in points ]
        #pygame.gfxdraw.aapolygon(self._screen, points, color)
        #if solid:
        #    pygame.gfxdraw.filled_polygon(self._screen, points, color)

    def draw_rect(self, pos, shape, color=(0, 0, 0), solid=True):
        Screen.draw_rect(self, pos, shape, color, solid)

    def clear(self, color=None):
        R, G, B = color or self.background
        glClearColor(R/255., G/255., B/255., 0.0)
        