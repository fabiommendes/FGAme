# -*- coding: utf8 -*-

from FGAme.mathtools import null2D, shapes
from . import Body

__all__ = ['Circle']


class Circle(Body):

    '''Define um círculo e implementa a detecção de colisão comparando a
    distância entre os centros com a soma dos raios.


    Examples
    --------

    Os círculos devem ser inicializados fornecendo o raio e opcionalmente a
    posição, velocidade e massa ou densidade.

    >>> c1 = Circle(10, (10, 0))     # raio 10 e centro em (10, 10)
    >>> c2 = Circle(10, density=2)   # raio 10 e densidade de 2
    >>> c2.area()
    314.1592653589793
    '''

    __slots__ = []

    def __init__(self, radius, pos=(0, 0), vel=(0, 0),
                 mass=None, density=None, **kwds):

        self.cbb_radius = float(radius)
        super(Circle, self).__init__(
            pos, vel, mass=mass, density=density,
            baseshape=shapes.Circle(self.cbb_radius, null2D), ** kwds)

    @property
    def radius(self):
        return self.cbb_radius

    @radius.setter
    def radius(self, value):
        self.cbb_radius = value

    def rescale(self, scale, update_physics=False):
        self.cbb_radius *= scale
        super(Circle, self).rescale(scale, update_physics)

    # Caixa de contorno #######################################################
    @property
    def bounding_box(self):
        return self.cbb

    @property
    def xmin(self):
        return self._pos.x - self.cbb_radius

    @property
    def xmax(self):
        return self._pos.x + self.cbb_radius

    @property
    def ymin(self):
        return self._pos.y - self.cbb_radius

    @property
    def ymax(self):
        return self._pos.y + self.cbb_radius

    def __repr__(self):
        tname = type(self).__name__
        vel = ', '.join('%.1f' % x for x in self._vel)
        pos = ', '.join('%.1f' % x for x in self._pos)
        return '%s(pos=(%s), vel=(%s), radius=%.1f)' % (
            tname, pos, vel, self.radius)


if __name__ == '__main__':
    from doctest import testmod
    testmod()
