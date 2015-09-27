# -*- coding: utf8 -*-

import string
import pygame
from FGAme import conf
from FGAme.core import Canvas
from FGAme.input import Input
from FGAme.mainloop import MainLoop
from FGAme.draw import Color, rgb
from FGAme.util import autodoc
pygame.init()  # @UndefinedVariable

black = Color('black')
white = Color('white')


@autodoc
class PyGameCanvas(Canvas):

    '''Implementa a interface Canvas utilizando a biblioteca pygame'''

    _pg_draw_circle = pygame.draw.circle
    _pg_draw_rect = pygame.draw.rect
    _pg_draw_poly = pygame.draw.polygon
    _pg_segment = pygame.draw.line

    def show(self):
        self._screen = pygame.display.set_mode((self.width, self.height))
        super(PyGameCanvas, self).show()

    def get_pygame_screen(self):
        return self._screen

    def flip(self):
        pygame.display.update()

    #
    # Funções de desenho - chama as funções de pygame.draw
    #
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

    def draw_raw_poly_solid(self, poly, color=black):
        self.draw_raw_poly_border(poly, 0, color)

    def draw_raw_poly_border(self, poly, width=1.0, color=black):
        Y = self.height
        vertices = [(int(x), int(Y - y)) for (x, y) in poly]
        self._pg_draw_poly(
            self._screen,
            color,        # line color
            vertices,     # center
            int(width))   # line width

    def draw_raw_segment(self, segment, width=1.0, color=black):
        Y = self.height
        pt1, pt2 = [(int(x), int(Y - y)) for (x, y) in segment]
        self._pg_segment(self._screen, color, pt1, pt2, int(width))

    def draw_raw_texture(self, texture, pos=(0, 0)):
        try:
            pg_texture = texture.data
        except AttributeError:
            pil_data = texture.get_pil_data()
            if pil_data.mode not in 'RGB' or 'RGBA':
                pil_data = pil_data.convert('RGBA')
            pg_texture = pygame.image.fromstring(
                pil_data.tostring(),
                texture.shape, pil_data.mode)
            texture.set_data(pg_texture)

        x, y, dx, dy = pg_texture.get_rect()
        x += pos[0]
        y += pos[1] + dy
        self._screen.blit(pg_texture, (x, self.height - y, dx, dy))

    def paint_pixel(self, pos, color=Color(0, 0, 0)):
        x, y = self._map_point(*pos)
        # TODO: talvez use pygame.display.get_surface() para obter a tela
        # correta
        # http://stackoverflow.com/questions/10354638/pygame-draw-single-pixel
        self._screen.set_at(x, y, rgb(color))

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
        _pg = pygame
        D = dict(
            up=_pg.K_UP,
            down=_pg.K_DOWN,
            left=_pg.K_LEFT,
            right=_pg.K_RIGHT,
            space=_pg.K_SPACE,
        )
        D['return'] = _pg.K_RETURN

        # Adiciona as letras e números
        for c in '0123456789' + string.ascii_lowercase:
            D[c] = getattr(_pg, 'K_' + c)

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
        window_height = conf.get_resolution()[1]
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
