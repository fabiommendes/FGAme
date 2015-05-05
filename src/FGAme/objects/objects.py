# -*- coding: utf8 -*-

from FGAme import physics
from FGAme.objects.mixins import ObjectMixin


class AABB(ObjectMixin, physics.AABB):
    _init_physics = physics.AABB.__init__

    def paint(self, screen):
        screen.paint_rect(self.rect, self.color)


class Circle(ObjectMixin, physics.Circle):
    _init_physics = physics.Circle.__init__

    def paint(self, screen):
        if self._color is not None:
            screen.paint_circle(self.radius, self.pos, self._color)
        if self._linecolor is not None:
            screen.paint_circle(self.radius, self.pos,
                                self._linecolor,
                                self._linewwidth)


class Ball(ObjectMixin, physics.Ball):
    _init_physics = physics.Ball.__init__

    def paint(self, screen):
        screen.paint_circle(self.radius, self.pos, self.color)


class Poly(ObjectMixin, physics.Poly):
    _init_physics = physics.Poly.__init__

    def paint(self, screen):
        screen.paint_poly(self.vertices, self.color)


class Rectangle(ObjectMixin, Poly, physics.Rectangle):
    _init_physics = physics.Rectangle.__init__


class RegularPoly(ObjectMixin, Poly, physics.RegularPoly):
    _init_physics = physics.RegularPoly.__init__


if __name__ == '__main__':
    x = AABB(shape=(100, 200), world=set())
    type(x)
    print(x.mass)
