# -*- coding: utf8 -*-

from FGAme.mathutils import pi, sqrt, Circle
from FGAme.physics.elements import LinearRB, RigidBody


class CommonCircle(object):

    '''Classe Mix-in com definições comuns ao círculo'''

    _slots_ = ['_radius']
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
        LinearRB.scale(scale, update_physics)

    def __repr__(self):
        tname = type(self).__name__
        vel = ', '.join('%.1f' % x for x in self.vel)
        pos = ', '.join('%.1f' % x for x in self.pos)
        return '%s(pos=(%s), vel=(%s), radius=%.1f)' % (
            tname, pos, vel, self.radius)


class PhysCircle(CommonCircle, LinearRB):

    '''Define um círculo e implementa a detecção de colisão comparando a
    distância entre os centros com a soma dos raios.

    Objetos da classe PhysCircle não realizam rotações. Caso deseje esta
    propriedade, utilize PhysBall.'''

    def __init__(self,
                 pos=(0, 0), vel=(0, 0),
                 mass=None, density=None,
                 radius=None):

        if radius is None:
            raise ValueError('radius must be defined')

        self._radius = float(radius)
        xmin, xmax = pos[0] - radius, pos[0] + radius
        ymin, ymax = pos[1] - radius, pos[1] + radius

        super(PhysCircle, self).__init__(pos, vel, mass, density,
                                         xmin, xmax, ymin, ymax)


class PhysBall(CommonCircle, RigidBody):

    '''Define um círculo e implementa a detecção de colisão comparando a
    distância entre os centros com a soma dos raios.

    Objetos da classe PhysBall são capazes de realizar rotações.'''

    def __init__(self,
                 pos=(0, 0), vel=(0, 0),
                 mass=None, density=None,
                 theta=0.0, omega=0.0, inertia=None,
                 radius=None):

        if radius is None:
            raise ValueError('radius must be defined')

        self._radius = float(radius)
        xmin, xmax = pos[0] - radius, pos[0] + radius
        ymin, ymax = pos[1] - radius, pos[1] + radius

        super(PhysBall, self).__init__(pos, vel, mass, density,
                                       theta, omega, inertia,
                                       xmin, xmax, ymin, ymax)


if __name__ == '__main__':
    from doctest import testmod
    testmod()
