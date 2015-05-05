# -*- coding: utf8 -*-

from FGAme.mathutils import pi, sqrt, Circle as _Circle
from FGAme.physics import LinearRigidBody, RigidBody

__all__ = ['Circle', 'Ball']


class CommonCircle(object):

    '''Classe Mix-in com definições comuns ao círculo'''

    _is_mixin_ = True

    def area(self):
        '''Retorna a área do círculo'''

        return pi * self.cbb_radius ** 2

    def ROG_sqr(self):
        '''Retorna o raio de giração do círculo ao quadrado'''

        return self.cbb_radius ** 2 / 2

    def ROG(self):
        '''Retorna o raio de giração do círculo'''

        return self.cbb_radius / sqrt(2)

    def primitive(self):
        return Circle(radius=self.radius, pos=self._pos)

    @property
    def radius(self):
        return self.cbb_radius

    @radius.setter
    def radius(self, value):
        self.cbb_radius = value

    def rescale(self, scale, update_physics=False):
        self.cbb_radius *= scale
        super(CommonCircle, self).rescale(scale, update_physics)

    # Caixa de contorno #######################################################
    @property
    def xmin(self):
        return self._pos._x - self.cbb_radius

    @property
    def xmax(self):
        return self._pos._x + self.cbb_radius

    @property
    def ymin(self):
        return self._pos.y - self.cbb_radius

    @property
    def ymax(self):
        return self._pos.y + self.cbb_radius

    @property
    def shape_bb(self):
        return _Circle(self.cbb_radius, self.pos)

    def __repr__(self):
        tname = type(self).__name__
        vel = ', '.join('%.1f' % x for x in self._vel)
        pos = ', '.join('%.1f' % x for x in self._pos)
        return '%s(_pos=(%s), _vel=(%s), radius=%.1f)' % (
            tname, pos, vel, self.radius)


class Circle(CommonCircle, LinearRigidBody):

    '''Define um círculo e implementa a detecção de colisão comparando a
    distância entre os centros com a soma dos raios.

    Objetos da classe Circle não realizam rotações. Caso deseje esta
    propriedade, utilize Ball.


    Examples
    --------

    Os círculos devem ser inicializados fornecendo o raio e opcionalmente a
    posição, velocidade e massa ou densidade.

    >>> c1 = Circle(10, (10, 0))     # raio 10 e centro em (10, 10)
    >>> c2 = Circle(10, density=2)   # raio 10 e densidade de 2
    '''

    __slots__ = ['_radius']

    def __init__(self, radius, pos=(0, 0), vel=(0, 0),
                 mass=None, density=None, **kwds):

        self.cbb_radius = float(radius)
        super(Circle, self).__init__(pos, vel, mass=mass, density=density,
                                     **kwds)


class Ball(CommonCircle, RigidBody):

    '''Define um círculo e implementa a detecção de colisão comparando a
    distância entre os centros com a soma dos raios.

    Objetos da classe Ball são capazes de realizar rotações.'''

    __slots__ = ['_radius']

    def __init__(self, radius, pos=(0, 0), vel=(0, 0), theta=0.0, omega=0.0,
                 mass=None, density=None, inertia=None, **kwds):

        self.cbb_radius = float(radius)
        super(Ball, self).__init__(pos, vel, theta, omega,
                                   mass=mass, density=density, inertia=inertia,
                                   **kwds)


if __name__ == '__main__':
    from doctest import testmod
    testmod()
