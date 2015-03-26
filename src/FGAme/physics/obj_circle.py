# -*- coding: utf8 -*-

from FGAme.mathutils import pi, sqrt, Circle
from FGAme.physics.obj_all import LinearRigidBody, RigidBody

__all__ = ['Circle', 'Ball']


class CommonCircle(object):

    '''Classe Mix-in com definições comuns ao círculo'''

    _is_mixin_ = True

    def area(self):
        '''Retorna a área do círculo'''

        return pi * self._radius ** 2

    def ROG_sqr(self):
        '''Retorna o raio de giração do círculo ao quadrado'''

        return self._radius ** 2 / 2

    def ROG(self):
        '''Retorna o raio de giração do círculo'''

        return self._radius / sqrt(2)

    def primitive(self):
        return Circle(radius=self.radius, pos=self.pos)

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

        # Atualiza a caixa de contorno
        x, y = self._pos
        self._xmin = x - value
        self._xmax = x + value
        self._ymin = y - value
        self._ymax = y + value

    def scale(self, scale, update_physics=False):
        self._radius *= scale
        LinearRigidBody.scale(scale, update_physics)

    def __repr__(self):
        tname = type(self).__name__
        vel = ', '.join('%.1f' % x for x in self.vel)
        pos = ', '.join('%.1f' % x for x in self.pos)
        return '%s(pos=(%s), vel=(%s), radius=%.1f)' % (
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
                 mass=None, density=None):

        self._radius = float(radius)
        xmin, xmax = pos[0] - radius, pos[0] + radius
        ymin, ymax = pos[1] - radius, pos[1] + radius
        del radius

        LinearRigidBody.__init__(**locals())


class Ball(CommonCircle, RigidBody):

    '''Define um círculo e implementa a detecção de colisão comparando a
    distância entre os centros com a soma dos raios.

    Objetos da classe Ball são capazes de realizar rotações.'''

    __slots__ = ['_radius']

    def __init__(self, radius, pos=(0, 0), vel=(0, 0), theta=0.0, omega=0.0,
                 mass=None, density=None, inertia=None):

        self._radius = float(radius)
        xmin, xmax = pos[0] - radius, pos[0] + radius
        ymin, ymax = pos[1] - radius, pos[1] + radius
        del radius

        RigidBody.__init__(**locals())


if __name__ == '__main__':
    from doctest import testmod
    testmod()
