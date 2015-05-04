# -*- coding: utf8 -*-

from FGAme import physics
from FGAme.objects.mixins import ObjectMixin

from pygame import draw
from math import trunc


class AABB(ObjectMixin, physics.AABB):
    _init_physics = physics.AABB.__init__


class Circle(ObjectMixin, physics.Circle):
    _init_physics = physics.Circle.__init__
    _circle = draw.circle

    def draw(self, screen):
        H = screen.height
        x, y = self._pos.trunc()
        x_, y_ = (self._pos - self._vel * 0.02).trunc()
        self._circle(
            screen._screen, (200, 200, 200), (x_, H - y_), 10)
        self._circle(
            screen._screen, (0, 0, 0), (x, H - y), 10)
        return
        try:
            return self._draw()
        except AttributeError:
            pgscreen = screen._screen
            radius = trunc(self.cbb_radius)
            height = screen.height
            painter = self._circle

            def draw():
                x, y = self._pos.trunc()
                painter(
                    pgscreen, (0, 0, 0), (x, height - y), radius)
                #screen.paint_circle(self.cbb_radius, self.pos, self.color)
            self._draw = draw
            draw()


class Ball(ObjectMixin, physics.Ball):
    _init_physics = physics.Ball.__init__


class Poly(ObjectMixin, physics.Poly):
    _init_physics = physics.Poly.__init__


class Rectangle(ObjectMixin, physics.Rectangle):
    _init_physics = physics.Rectangle.__init__


class RegularPoly(ObjectMixin, physics.RegularPoly):
    _init_physics = physics.RegularPoly.__init__

if __name__ == '__main__':
    x = AABB(shape=(100, 200), world=set())
    type(x)
    type(x).__bases__
    print(x.mass)
