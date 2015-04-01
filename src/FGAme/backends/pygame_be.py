# -*- coding: utf8 -*-

from math import trunc
import string
import pygame
import pygame.locals as pg
from pygame.locals import QUIT, KEYDOWN, KEYUP, MOUSEMOTION

from FGAme.core import env, Canvas, Input, MainLoop
from FGAme.draw import Color

pygame.init()


class PyGameCanvas(Canvas):

    '''Implementa a interface Canvas utilizando a biblioteca pygame'''

    def show(self):
        self._screen = pygame.display.set_mode((self.width, self.height))
        super(PyGameCanvas, self).show()

    def flip(self):
        pygame.display.update()

    def _map_point(self, point):
        x, y = point
        X, Y = self.width, self.height
        return (trunc(x), trunc(Y - y))

    def paint_circle(self, radius, pos, color='black', solid=True):
        pos = self._map_point(pos)
        color = Color(color)
        pygame.draw.circle(self._screen, color, pos, trunc(radius))

    def paint_poly(self, points, color='black', solid=True):
        points = [self._map_point(pt) for pt in points]
        color = Color(color)
        pygame.draw.polygon(self._screen, color.rgb, points)

    def paint_rect(self, rect, color='black', solid=True):
        color = Color(color)
        x, y, dx, dy = rect
        x, y = self._map_point((x, y + dy))
        pygame.draw.rect(self._screen, color, (x, y, dx, dy))

    def paint_line(self, pt1, pt2, color='black', solid=True):
        raise NotImplementedError

    def paint_pixel(self, pos, color='black'):
        x, y = self._map_point(*pos)
        # TODO: talvez use pygame.display.get_surface() para obter a tela
        # correta
        # http://stackoverflow.com/questions/10354638/pygame-draw-single-pixel
        self._screen.set_at(x, y, Color(color))

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
        D = dict(up=pg.K_UP, down=pg.K_DOWN, left=pg.K_LEFT, right=pg.K_RIGHT,
                 space=pg.K_SPACE,
                 )
        D['return'] = pg.K_RETURN

        # Adiciona as letras e números
        chars = '0123456789' + string.ascii_lowercase
        for c in chars:
            D[c] = getattr(pg, 'K_' + c)

        self._key_conversions = {v: k for (k, v) in D.items()}

    # Laço principal de escuta de eventos #####################################
    def query(self):
        D = self._key_conversions
        window_height = env.window_height

        for event in pygame.event.get():
            if event.type == QUIT:
                raise SystemExit
            elif event.type == KEYDOWN:
                self.process_key_down(D.get(event.key))
            elif event.type == KEYUP:
                self.process_key_up(D.get(event.key))
            elif event.type == MOUSEMOTION:
                x, y = event.pos
                y = window_height - y
                self.process_mouse_motion((x, y))

        self.process_long_press()


class PyGameMainLoop(MainLoop):
    pass
