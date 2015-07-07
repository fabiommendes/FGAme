# -*- coding: utf8 -*-
'''
Exemple
-------

Criamos um vetor chamando a classe com as componentes como argumento.

>>> v = Vec3(1, 2, 2); print(v)
Vec3(1, 2, 2)

Os métodos de listas funcionam para objetos do tipo Vec3:

>>> v[0], v[1], v[2], len(v)
(1.0, 2.0, 2.0, 3)

Objetos do tipo Vec3 também aceitam operações matemáticas

>>> v + 2 * v
Vec3(3, 6, 6)

Além de algumas funções de conveniência para calcular o módulo,
vetor unitário, etc.

>>> v.norm(); abs(v)
3.0
3.0

>>> v.normalize()
Vec3(0.3, 0.7, 0.7)
'''

import cython as C
import math as m
from smallvectors.cartesian import Vec, Direction, Point


class Base3D(object):

    '''Base class for Vec3, Direction3 and Point3 classes'''

    def __init__(self, x, y, z):
        self.x = x + 0.0
        self.y = y + 0.0
        self.z = z + 0.0

    #
    # Abstract methods overrides
    #
    @classmethod
    def from_seq(cls, data):
        if isinstance(data, cls):
            return data
        else:
            x, y, z = data
            return cls.from_coords(x, y, z)

    @classmethod
    def from_coords(cls, x, y, z):
        new = Base3D.__new__(cls, x, y, z)
        new.x = x + 0.0
        new.y = y + 0.0
        new.z = z + 0.0
        return new

    @classmethod
    def null(cls):
        return nullvec3

    @classmethod
    def to_direction(cls, value):
        return Direction3.from_seq(value)

    @classmethod
    def to_vector(cls, value):
        return Vec3.from_seq(value)

    @classmethod
    def to_point(cls, value):
        return Point3.from_seq(value)

    def __len__(self):
        return 3

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __getitem__(self, i):
        '''x.__getitem__(i) <==> x[i]'''

        if i == 0:
            return self.x
        elif i == 1:
            return self.y
        elif i == 2:
            return self.z
        else:
            raise IndexError(i)

    #
    # Performance overrides
    #
    def copy(self, x=None, y=None, z=None):
        '''Return a copy possibly overriding the values for x and y'''

        if x is None:
            x = self.x
        if y is None:
            y = self.y
        if z is None:
            z = self.z
        return self.from_coords(x, y, z)


class VecAndDirectionBase3D(Base3D):

    '''Base class with common implementations for for Vec2 and Direction2'''

    def cross(self, other):
        '''The cross product between two tridimensional smallvectors'''

        x, y, z = self
        a, b, c = other
        return Vec3(y * c - z * b, z * a - x * c, x * b - y * a)


class Vec3(VecAndDirectionBase3D, Vec):

    '''A 3D vector'''

    def __init__(self, x_or_data, y=None, z=None):
        if y is None:
            x_or_data, y, z = x_or_data
        VecAndDirectionBase3D.__init__(self, x_or_data, y, z)


class Direction3(VecAndDirectionBase3D, Direction):

    '''A 2-dimensional direction/unity vector'''

    def __init__(self, *args):
        norm = m.sqrt(sum(x * x for x in args))
        VecAndDirectionBase3D.__init__(self, *(x / norm for x in args))


class Point3(Base3D, Point):

    '''A geometric point in 3D space'''


###############################################################################
# Module constant smallvectors
###############################################################################
null3D = Vec3(0, 0, 0)
ux3D = Direction3(1, 0, 0)
uy3D = Direction3(0, 1, 0)
uz3D = Direction3(0, 0, 1)
bases3D = ux3D, uy3D, uz3D


if __name__ == '__main__' and not C.compiled:
    import doctest
    doctest.testmod()
