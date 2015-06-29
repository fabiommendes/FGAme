# -*- coding: utf8 -*-

import cython
import string
import pygame
from FGAme.core import Canvas, conf
from FGAme.input import Input
from FGAme.mainloop import MainLoop
from FGAme.draw import Color, rgb
from FGAme.util import autodoc
pygame.init()

black = Color('black')
white = Color('white')


@autodoc
class PyGameCanvas(Canvas):

    '''Implementa a interface Canvas utilizando a biblioteca pygame'''

    __slots__ = ['_screen']
    _pg_draw_circle = pygame.draw.circle
    _pg_draw_rect = pygame.draw.rect

    def get_screen(self):
        '''Retorna o objeto do tipo screen do Pygame'''

        return self._screen

    def show(self):
        self._screen = pygame.display.set_mode((self.width, self.height))
        super(PyGameCanvas, self).show()

    def flip(self):
        pygame.display.update()

    # Funções de desenho - chama as funções de pygame.draw
    def draw_raw_aabb_solid(self, aabb, color=black):
        self.draw_raw_aabb_border(aabb, 0, color)

    def draw_raw_aabb_border(self, aabb, width=1.0, color=black):
        Y = self.height
        x, x_, y, y_ = map(int, aabb)
        rect = (x, Y - y_, x_ - x, y_ - y)
        self._pg_draw_rect(
            self._screen,
            color,       # color
            rect,        # rect
            int(width))  # line width

    def draw_raw_circle_solid(self, circle, color=black):
        self.draw_raw_circle_border(circle, 0, color)

    def draw_raw_circle_border(self, circle, width=1.0, color=black):
        Y = self.height
        x, y = circle.pos
        self._pg_draw_circle(
            self._screen,
            color,                 # line color
            (int(x), Y - int(y)),  # center
            int(circle.radius),    # radius
            int(width))            # line width

    # TODO: refatorar para a nova API
    def paint_poly(self, points, color=Color(0, 0, 0), solid=True):
        points = [self._map_point(pt) for pt in points]
        pygame.draw.polygon(self._screen, rgb(color), points)

    def paint_rect(self, rect, color=Color(0, 0, 0), solid=True):
        x, y, dx, dy = rect
        x, y = self._map_point((x, y + dy))
        pygame.draw.rect(self._screen, rgb(color), (x, y, dx, dy))

    def paint_line(self, pt1, pt2, color=Color(0, 0, 0), width=1):
        pt1 = self._map_point(pt1)
        pt2 = self._map_point(pt2)
        pygame.draw.line(self._screen, rgb(color), pt1, pt2, width=width)

    def paint_pixel(self, pos, color=Color(0, 0, 0)):
        x, y = self._map_point(*pos)
        # TODO: talvez use pygame.display.get_surface() para obter a tela
        # correta
        # http://stackoverflow.com/questions/10354638/pygame-draw-single-pixel
        self._screen.set_at(x, y, rgb(color))

    def paint_image(self, pos, image):
        x, y, dx, dy = image.get_rect()
        x += pos[0]
        y += pos[1]
        self._screen.blit(image, (x, y, dx, dy))

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
        pg = pygame
        D = dict(
            up=pg.K_UP,
            down=pg.K_DOWN,
            left=pg.K_LEFT,
            right=pg.K_RIGHT,
            space=pg.K_SPACE,
        )
        D['return'] = pg.K_RETURN

        # Adiciona as letras e números
        chars = '0123456789' + string.ascii_lowercase
        for c in chars:
            D[c] = getattr(pg, 'K_' + c)

        self._key_conversions = {v: k for (k, v) in D.items()}
        self._mouse_conversions = {
            1: 'left',
            2: 'middle',
            3: 'right',
            4: 'wheel-up',
            5: 'wheel-down'
        }

    # Laço principal de escuta de eventos #####################################
    def poll(self):
        key_get = self._key_conversions.get
        mouse_button_get = self._mouse_conversions.get
        window_height = conf.window_height  # @UndefinedVariable
        pg = pygame

        for event in pygame.event.get():
            if event.type == pg.QUIT:
                raise SystemExit
            elif event.type == pg.KEYDOWN:
                self.process_key_down(key_get(event.key))
            elif event.type == pg.KEYUP:
                self.process_key_up(key_get(event.key))
            elif event.type == pg.MOUSEMOTION:
                x, y = event.pos
                y = window_height - y
                self.process_mouse_motion((x, y))
            elif event.type == pg.MOUSEBUTTONUP:
                x, y = event.pos
                y = window_height - y
                button = mouse_button_get(event.button)
                self.process_mouse_button_up(button, (x, y))
            elif event.type == pg.MOUSEBUTTONDOWN:
                x, y = event.pos
                y = window_height - y
                button = mouse_button_get(event.button)
                self.process_mouse_button_down(button, (x, y))

        self.process_long_press()
        self.process_mouse_longpress()


class PyGameMainLoop(MainLoop):
    pass
