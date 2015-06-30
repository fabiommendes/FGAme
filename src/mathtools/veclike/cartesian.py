#-*- coding: utf8 -*-
'''
Base classes for vector-like types.
'''

import math as m


def norm(vec):
    '''Return the norm of a vector'''

    try:
        return vec.norm()
    except AttributeError:
        if isinstance(vec, tuple):
            return m.sqrt(sum(x * x for x in vec))
        else:
            tname = type(vec).__name__
            raise TypeError('norm is not defined for %s object' % tname)


def normalize(obj):
    '''Return a normalized version of vector or tuple'''

    try:
        return obj.normalize()
    except AttributeError:
        if isinstance(obj, tuple):
            return vec(obj)
        else:
            tname = type(obj).__name__
            raise TypeError('normalize is not defined for %s object' % tname)


def vec(*args):
    '''Return a vector of the correct dimensionality from the given
    components'''

    return VecND(*args)


###############################################################################
#                             Abstract base classes
###############################################################################
class Cartesian(object):

    '''Base class for all cartesian objects'''

    #
    # Class constructors
    #
    @classmethod
    def from_seq(cls, data):
        '''Initializes from any sequence of two values'''

        if isinstance(data, cls):
            return data
        else:
            return cls.from_coords(*data)

    @classmethod
    def from_coords(cls, *args):
        '''Initializes from coordinates'''

        raise NotImplementedError

    @classmethod
    def null(cls):
        '''Returns the null vector'''

        raise NotImplementedError

    @classmethod
    def to_direction(cls, value):
        '''Creates a new Direction object from value'''

        raise NotImplementedError

    @classmethod
    def to_vector(cls, value):
        '''Creates a new vector object object from value'''

        raise NotImplementedError

    @classmethod
    def to_point(cls, value):
        '''Creates a new point object object from value'''

        raise NotImplementedError

    #
    # Geometric properties
    #
    def almost_equals(self, other, tol=1e-3):
        '''Return True if two vectors are almost equal to each other'''

        return (self - other).norm_sqr() < tol * tol

    def distance(self, other):
        '''Computes the distance between two objects'''

        if len(self) != len(other):
            N, M = len(self), len(other)
            raise IndexError('invalid dimensions: %s and %s' % (N, M))

        deltas = (x - y for (x, y) in zip(self, other))
        return m.sqrt(sum(x * x for x in deltas))

    def lerp(self, other, weight):
        '''Linear interpolation between two objects.

        The weight attribute defines how close the result will be from the
        argument. A weight of 0.5 corresponds to the middle point between
        the two objects.'''

        if not 0 <= weight <= 1:
            raise ValueError('weight must be between 0 and 1')

        return (other - self) * weight + self

    #
    # Representations
    #
    def as_tuple(self):
        '''Return a tuple of coordinates.'''

        return tuple(self)

    def as_vector(self):
        '''Returns a copy of object as a vector'''

        return self.to_vector(self)

    def as_direction(self):
        '''Returns a (normalized) copy of object as a direction'''

        return self.to_direction(self)

    def as_point(self):
        '''Returns a copy of object as a point'''

        return self.to_point(self)

    def copy(self, x=None, y=None, z=None, **kwds):
        '''Return a copy possibly overriding some components'''

        data = list(self)
        if x is not None:
            data[0] = x
        if y is not None:
            data[1] = y
        if z is not None:
            data[2] = z

        # Keywords of the form e1=foo, e2=bar, etc
        for k, v in kwds.items():
            if not k.startswith('e'):
                raise TypeError('invalid argument %r' % k)
            data[int(k[1:]) + 1] = v

        return self.from_seq(data)

    #
    # Magic methods
    #
    def _assure_match(self, other):
        if len(self) != len(other):
            raise TypeError('dimensions do not match')

    def __repr__(self):
        '''x.__repr__() <==> repr(x)'''

        data = ['%.1f' % x if x != int(x) else str(int(x)) for x in self]
        data = ', '.join(data)
        return '%s(%s)' % (type(self).__name__, data)

    def __str__(self):
        '''x.__str__() <==> str(x)'''

        return repr(self)

    def __hash__(self):
        return hash(self.as_tuple())

    #
    # Abstract methods
    #
    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __getitem__(self, idx):
        raise NotImplementedError


class Point(Cartesian):

    '''Base class for all point objects'''

    def __add__(self, other):
        self._assure_match(other)
        if isinstance(other, Point):
            raise TypeError('cannot add two points together')
        return self.from_data([x + y for (x, y) in zip(self, other)])

    def __radd__(self, other):
        self._assure_match(other)
        return self.from_data([x + y for (x, y) in zip(self, other)])

    def __sub__(self, other):
        self._assure_match(other)
        data = [x - y for (x, y) in zip(self, other)]
        return self.to_vector(data)

    def __rsub__(self, other):
        self._assure_match(other)
        return self.to_vector([x - y for (x, y) in zip(other, self)])


class VecAndDirection(Cartesian):

    '''Base class with common implementation for Vec and Direction'''

    def angle(self, other):
        '''Angle between two vectors'''

        cos_t = self.dot(other) / (self.norm() * norm(other))
        return m.acos(cos_t)

    def reflect(self, direction):
        '''Reflect vector around the given direction'''

        return self - 2 * (self - self.project(direction))

    def project(self, direction):
        '''Returns the projection vector in the given direction'''

        direction = self.to_direction(direction)
        return self.dot(direction) * direction

    def clamp(self, min, max):
        '''Returns a new vector in which min <= abs(out) <= max.'''

        norm = new_norm = self.norm()
        if norm > max:
            new_norm = max
        elif norm < min:
            new_norm = min

        if new_norm != norm:
            return self.normalize() * new_norm
        else:
            return self

    def dot(self, other):
        '''Dot product between two vectors'''

        self._assure_match(other)
        return sum(x * y for (x, y) in zip(self, other))

    #
    # Arithmetic operations
    #
    def __mul__(self, other):
        return self.to_vector([x * other for x in self])

    def __rmul__(self, other):
        return self * other

    def __div__(self, other):
        return self.to_vector([x / other for x in self])

    def __truediv__(self, other):
        return self.to_vector([x / other for x in self])

    def __add__(self, other):
        self._assure_match(other)
        if isinstance(other, Point):
            return other + self
        return self.to_vector([x + y for (x, y) in zip(self, other)])

    def __radd__(self, other):
        self._assure_match(other)
        return self.to_vector([x + y for (x, y) in zip(self, other)])

    def __sub__(self, other):
        self._assure_match(other)
        data = [x - y for (x, y) in zip(self, other)]
        if isinstance(other, Point):
            return other.from_data(data)
        return self.to_vector(data)

    def __rsub__(self, other):
        self._assure_match(other)
        return self.to_vector([x - y for (x, y) in zip(other, self)])

    def __neg__(self):
        return self.from_data([-x for x in self])

    def __nonzero__(self):
        return True

    def __abs__(self):
        return self.norm()

    def __eq__(self, other):
        self._assure_match(other)
        return all(x == y for (x, y) in zip(self, other))


class Vec(VecAndDirection):

    '''Base class for all Vec types'''

    def is_null(self):
        '''Checks if vector has only null components'''

        return all(x == 0.0 for x in self)

    def is_unity(self, tol=1e-6):
        '''Return True if the norm equals one within the given tolerance'''

        return abs(self.norm() - 1) < tol

    def norm(self):
        '''Returns the norm of a vector'''

        return m.sqrt(self.norm_sqr())

    def norm_sqr(self):
        '''Returns the squared norm of a vector'''

        return sum(x * x for x in self)

    def normalize(self):
        '''Return a normalized version of vector'''

        return self / self.norm()


class Direction(VecAndDirection):

    '''Base class for all Direction types'''

    def is_null(self):
        '''Always False for Direction objects'''

        return False

    def is_unity(self, tol=1e-6):
        '''Always True for Direction objects'''

        return True

    def norm(self):
        '''Returns the norm of a vector'''

        return 1.0

    def norm_sqr(self):
        '''Returns the squared norm of a vector'''

        return 1.0

    def normalize(self):
        '''Return a normalized version of vector'''

        return self


###############################################################################
# N-Dimensional implementations
###############################################################################
class BaseND(object):

    '''Base class for all N-dimensional Cartesian subclasses.
    Only create objects with dimensions >= 5'''

    def __new__(cls, *args):
        N = len(args)
        if N == 1:
            return cls(*args[0])
        elif N > 4:
            new = object.__new__(cls)
            new._data = args
            return new
        elif N == 2:
            return cls._dim2(*args)
        elif N == 3:
            return cls._dim3(*args)
        elif N == 4:
            return cls._dim4(*args)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, idx):
        return self._data[idx]


class PointND(BaseND, Point):

    '''A point object with dimension greater than four.'''

    _dim2 = _dim3 = _dim4 = None


class VecND(BaseND, Vec):

    '''A vector object with dimension greater than four.'''

    _dim2 = _dim3 = _dim4 = None


class DirectionND(BaseND, Direction):

    '''A direction object with dimension greater than four.'''

    _dim2 = _dim3 = _dim4 = None

    def __new__(cls, *args):
        norm = m.sqrt(sum(x * x for x in args))
        return BaseND.__new__(cls, *tuple(x / norm for x in args))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
