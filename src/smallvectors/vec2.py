# -*- coding: utf8 -*-
'''
Exemple
-------

Criamos um vetor chamando a classe com as componentes como argumento.

>>> v = Vec2(3, 4); print(v)
Vec2(3, 4)

Os métodos de listas funcionam para objetos do tipo Vec2:

>>> v[0], v[1], len(v)
(3.0, 4.0, 2)

Objetos do tipo Vec2 também aceitam operações matemáticas

>>> v + 2 * v
Vec2(9, 12)

Além de algumas funções de conveniência para calcular o módulo,
vetor unitário, etc.

>>> v.norm(); abs(v)
5.0
5.0

>>> v.normalize()
Vec2(0.6, 0.8)
'''
from math import cos, sin, sqrt, atan2
from smallvectors import Vec, Direction, Point


class Base2D(object):

    '''Base class for Vec2, Direction2 and Point2 classes'''

    def __init__(self, x, y):
        self.x = x + 0.0
        self.y = y + 0.0

    #
    # Abstract methods overrides
    #
    @classmethod
    def from_seq(cls, data):
        if isinstance(data, cls):
            return data
        else:
            x, y = data
            return cls.from_coords(x, y)

    @classmethod
    def from_coords(cls, x, y):
        new = Base2D.__new__(cls, x, y)
        new.x = x + 0.0
        new.y = y + 0.0
        return new

    @classmethod
    def null(cls):
        return null2D

    @classmethod
    def to_direction(cls, value):
        return Direction2.from_seq(value)

    @classmethod
    def to_vector(cls, value):
        return Vec2.from_seq(value)

    @classmethod
    def to_point(cls, value):
        return Point2.from_seq(value)

    def __len__(self):
        return 2

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, i):
        '''x.__getitem__(i) <==> x[i]'''

        if i == 0:
            return self.x
        elif i == 1:
            return self.y
        else:
            raise IndexError(i)

    #
    # Performance overrides
    #
    def distance(self, other):
        '''Computes the distance between two objects'''

        return sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

    def copy(self, x=None, y=None):
        '''Return a copy possibly overriding the values for x and y'''

        if x is None:
            x = self.x
        if y is None:
            y = self.y
        return self.from_coords(x, y)

    def __hash__(self):
        return hash(self.x) ^ hash(self.y)


class VecAndDirectionBase2D(Base2D):

    '''Base class with common implementations for for Vec2 and Direction2'''

    #
    # Performance overrides
    #

    def angle(self, other):
        '''Computes the angle between two smallvectors'''

        cos_t = self.dot(other)
        sin_t = self.cross(other)
        return atan2(sin_t, cos_t)

    #
    # 2D specific geometric properties and operations
    #
    def polar(self):
        '''Return a tuple with the (radius, theta) polar coordinates '''

        return (self.norm(), atan2(self.y, self.x))

    def perp(self, ccw=True):
        '''Return the counterclockwise perpendicular vector.

        If ccw is False, do the rotation in the clockwise direction.
        '''

        if ccw:
            return Vec2(-self.y, self.x)
        else:
            return Vec2(self.y, -self.x)

    def rotate(self, theta):
        '''Rotate vector by an angle theta around origin'''

        x, y = self
        cos_t, sin_t = cos(theta), sin(theta)
        return self.from_coords(
            x * cos_t - y * sin_t,
            x * sin_t + y * cos_t)

    def rotate_axis(self, axis, theta):
        '''Rotate vector around given axis by the angle theta'''

        dx, dy = self - axis
        cos_t, sin_t = cos(theta), sin(theta)
        return Vec2(
            dx * cos_t - dy * sin_t + axis[0],
            dx * sin_t + dy * cos_t + axis[1])

    def cross(self, other):
        '''The z component of the cross product between two bidimensional
        smallvectors'''

        x, y = other
        return self.x * y - self.y * x


class Vec2(VecAndDirectionBase2D, Vec):

    '''A 2D vector'''

    def __init__(self, x_or_data, y=None):
        if y is None:
            x, y = x_or_data
        else:
            x = x_or_data
        self.x = x + 0.0
        self.y = y + 0.0

    def is_null(self):
        '''Checks if vector has only null components'''

        if self.x == 0.0 and self.y == 0.0:
            return True
        else:
            return False

    def is_unity(self, tol=1e-6):
        '''Return True if the norm equals one within the given tolerance'''

        return abs(self.x * self.x + self.y * self.y - 1) < 2 * tol

    def norm(self):
        '''Returns the norm of a vector'''

        return sqrt(self.x ** 2 + self.y ** 2)

    def norm_sqr(self):
        '''Returns the squared norm of a vector'''

        return self.x ** 2 + self.y ** 2


class Direction2(VecAndDirectionBase2D, Direction):

    '''A 2-dimensional direction/unity vector'''

    def __init__(self, x_or_data, y=None):
        if y is None:
            x, y = x_or_data
        else:
            x = x_or_data
        norm = sqrt(x * x + y * y)
        if norm == 0:
            raise ValueError('null vector does not define a valid direction')

        self.x = (x + 0.0) / norm
        self.y = (y + 0.0) / norm

    def rotate(self, theta):
        '''Rotate vector by an angle theta around origin'''

        x, y = self
        cos_t, sin_t = cos(theta), sin(theta)
        new = Base2D.__new__(Direction2, x, y)
        new.x = x * cos_t - y * sin_t
        new.y = x * sin_t + y * cos_t
        return new


class Point2(Base2D, Point):

    '''A geometric point in 2D space'''


###############################################################################
# Module constants
###############################################################################
null2D = Vec2(0, 0)
ux2D = Direction2(1, 0)
uy2D = Direction2(0, 1)
bases2D = ux2D, uy2D

if __name__ == '__main__':
    import doctest
    doctest.testmod()
