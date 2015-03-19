import pygame
from FGAme.core.screen import Canvas
from FGAme.core.input import Input
from FGAme.core.mainloop import MainLoop

class PyGameCanvas(Canvas):
    '''Implementa a interface Canvas utilizando a biblioteca pygame'''

    def init(self):
        self._screen = pygame.display.set_mode((self.width, self.height))
        
    def flip(self):
        pygame.display.update()

    def _map_point(self, point):
        x, y = point
        X, Y = self.width, self.height
        return (trunc(x), trunc(Y - y))

    #===========================================================================
    # Desenho
    #===========================================================================
    def paint_circle(self, pos, radius, color='black', solid=True):
        pos = self._map_point(pos)
        color = Color(color)
        pygame.draw.circle(self._screen, color, pos, trunc(radius))

    def paint_poly(self, points, color='black', solid=True):
        points = [ self._map_point(pt) for pt in points ]
        color = Color(color)
        pygame.draw.polygon(self._screen, color.rgb, points)

    def paint_rect(self, pos, shape, color='black', solid=True):
        color = Color(color)
        x, y = self._map_point(pos)
        dx, dy = shape
        y -= dy/2
        x -= dx/2
        pygame.draw.rect(self._screen, color, (x, y, dx, dy))

    def paint_line(self, pt1, pt2, color='black', solid=True):
        raise NotImplementedError

    def clear_background(self, color=None):
        if color is None:
            if self.background is None:
                raise RuntimeError('background was not defined')
            self._screen.fill(self.background)
        else:
            self._screen.fill(Color(color))
        
class PyGameInput(Input):
    '''Implementa a interface Input através do Pygame.'''

    def __init__(self):
        super(PyGameInput, self).__init__()
        
        # Registra conversão de teclas
        import pygame.locals as pg
        
        D = dict(up=pg.K_UP, down=pg.K_DOWN, left=pg.K_LEFT, right=pg.K_RIGHT,
            space=pg.K_SPACE,
        )
        D['return'] = pg.K_RETURN

        # Adiciona as letras e números
        chars = '0123456789' + string.ascii_lowercase
        for c in chars:
            D[c] = getattr(pg, 'K_' + c)
        
        self._key_conversions = { v: k for (k, v) in D.items() }
        
    #===========================================================================
    # Laço principal de escuta de eventos
    #===========================================================================
    def query(self):
        from pygame.locals import QUIT, KEYDOWN, KEYUP, MOUSEMOTION
        import pygame
        pygame.init()
        D = self._key_conversions
        
        for event in pygame.event.get():
            if event.type == QUIT:
                raise SystemExit
            elif event.type == KEYDOWN:
                self.process_key_down(D.get(event.key))
            elif event.type == KEYUP:
                self.process_key_up(D.get(event.key))
            elif event.type == MOUSEMOTION:
                x, y = event.pos
                y = env.window_height - y
                self.process_mouse_motion((x, y))

        self.process_long_press()
        
class PyGameMainLoop(MainLoop):
    pass