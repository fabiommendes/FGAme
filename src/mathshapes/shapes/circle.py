# -*- coding: utf8 -*-
from copy import copy
from mathtools import dot, Vec2, Point2, pi, sqrt
from mathtools.shapes import Curve

SQRT_HALF = 1 / sqrt(2)


class CircleBase(Curve):

    '''Base class for Circle and mCircle classes'''

    __slots__ = ['_radius', '_x', '_y']

    def __init__(self, radius, pos=(0, 0)):
        self._radius = radius
        self._x, self._y = pos

    def __repr__(self):
        s_center = '%.1f, %.1f' % tuple(self.center)
        tname = type(self).__name__
        return '%s(%.1f, (%s))' % (tname, self._radius, s_center)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def pos(self):
        return Vec2(self._x, self._y)

    @property
    def center(self):
        return Point2(self._x, self._y)

    @property
    def area(self):
        return pi * self._radius * self._radius

    @property
    def ROG_sqr(self):
        return self._radius * self._radius / 2

    @property
    def ROG(self):
        return self._radius * SQRT_HALF

    # Métodos utilizado pelo SAT ##############################################
    def directions(self, n):
        '''Retorna a lista de direções exaustivas para o teste do SAT
        associadas ao objeto.

        A rigor esta lista é infinita para um círculo. Retornamos uma lista
        vazia de forma que somente as direções do outro objeto serão
        consideradas'''

        return []

    def shadow(self, n):
        '''Retorna as coordenadas da sombra na direção n dada.
        Assume n normalizado.'''

        p0 = dot(self._pos, n)
        r = self._radius
        return (p0 - r, p0 + r)

    # Cálculo de distâncias ###################################################
    def distance_center(self, other):
        '''Retorna a distância entre centros de dois círculos.'''

        return self._pos.distance(other.pos)

    def distance_circle(self, other):
        '''Retorna a distância para um outro círculo. Zero se eles se
        interceptam'''

        distance = self._pos.distance(other.pos)
        sum_radius = self._radius + other.radius
        return max(distance - sum_radius, 0)

    # Containement FGAme_tests ###############################################
    def contains_circle(self, other):
        return (self.contains_point(other.pos) and
                (self.distance_center(other) + other.radius < self._radius))

    def contains_point(self, point):
        return self._pos.distance(point) <= self._radius


class Circle(CircleBase):

    '''Representa um círculo imutável.'''

    __slots__ = []

    @property
    def radius(self):
        return self._radius


class mCircle(CircleBase):

    '''A mutable circle class'''

    __slots__ = []

    @Circle.radius.setter
    def radius(self, value):
        self._radius = float(value)

    @Circle.pos.setter
    def pos(self, value):
        self._x, self._y = value

# Late binding
Curve._Circle = CircleBase

if __name__ == '__main__':
    import doctest
    doctest.testmod()
