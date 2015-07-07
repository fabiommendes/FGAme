# -*- coding: utf8 -*-
'''
Exemple
-------

Criamos um vetor chamando a classe com as componentes como argumento.

>>> v = Vec4(1, 1, 1, 1); print(v)
Vec4(1, 1, 1, 1)

Os métodos de listas funcionam para objetos do tipo Vec4:

>>> v[0], v[1], v[2], v[3], len(v)
(1.0, 1.0, 1.0, 1.0, 4)

Objetos do tipo Vec4 também aceitam operações matemáticas

>>> v + 2 * v
Vec4(3, 3, 3, 3)

Além de algumas funções de conveniência para calcular o módulo,
vetor unitário, etc.

>>> v.norm(); abs(v)
2.0
2.0

>>> v.normalize()
Vec4(0.5, 0.5, 0.5, 0.5)
'''

import cython as C
import math as m
from smallvectors.cartesian import Vec, Direction, Point


class Base4D(object):

    '''Base class for Vec4, Direction4 and Point4 classes'''

    def __init__(self, x, y, z, w):
        self.x = x + 0.0
        self.y = y + 0.0
        self.z = z + 0.0
        self.w = w + 0.0

    #
    # Abstract methods overrides
    #
    @classmethod
    def from_seq(cls, data):
        if isinstance(data, cls):
            return data
        else:
            x, y, z, w = data
            return cls.from_coords(x, y, z, w)

    @classmethod
    def from_coords(cls, x, y, z, w):
        new = Base4D.__new__(cls, x, y, z, w)
        new.x = x + 0.0
        new.y = y + 0.0
        new.z = z + 0.0
        new.w = w + 0.0
        return new

    @classmethod
    def null(cls):
        return null4D

    @classmethod
    def to_direction(cls, value):
        return Direction4.from_seq(value)

    @classmethod
    def to_vector(cls, value):
        return Vec4.from_seq(value)

    @classmethod
    def to_point(cls, value):
        return Point4.from_seq(value)

    def __len__(self):
        return 4

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z
        yield self.w

    def __getitem__(self, i):
        '''x.__getitem__(i) <==> x[i]'''

        if i == 0:
            return self.x
        elif i == 1:
            return self.y
        elif i == 2:
            return self.z
        elif i == 3:
            return self.w
        else:
            raise IndexError(i)

    #
    # Performance overrides
    #
    def copy(self, x=None, y=None, z=None, w=None):
        '''Return a copy possibly overriding the values for x and y'''

        if x is None:
            x = self.x
        if y is None:
            y = self.y
        if z is None:
            z = self.z
        if w is None:
            w = self.w
        return self.from_coords(x, y, z, w)


class VecAndDirectionBase4D(Base4D):

    '''Base class with common implementations for for Vec2 and Direction2'''


class Vec4(VecAndDirectionBase4D, Vec):

    '''A 4D vector'''

    def __init__(self, x_or_data, y=None, z=None, w=None):
        if y is None:
            x_or_data, y, z = x_or_data
        VecAndDirectionBase4D.__init__(self, x_or_data, y, z, w)


class Direction4(VecAndDirectionBase4D, Direction):

    '''A 2-dimensional direction/unity vector'''

    def __init__(self, *args):
        norm = m.sqrt(sum(x * x for x in args))
        VecAndDirectionBase4D.__init__(self, *(x / norm for x in args))


class Point4(Base4D, Point):

    '''A geometric point in 4D space'''


###############################################################################
# Module constant smallvectors
###############################################################################
null4D = Vec4(0, 0, 0, 0)
ux4D = Direction4(1, 0, 0, 0)
uy4D = Direction4(0, 1, 0, 0)
uz4D = Direction4(0, 0, 1, 0)
uw4D = Direction4(0, 0, 0, 1)
bases4D = ux4D, uy4D, uz4D, uw4D


if __name__ == '__main__' and not C.compiled:
    import doctest
    doctest.testmod()
