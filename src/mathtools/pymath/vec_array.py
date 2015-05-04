# -*- coding: utf8 -*-

from collections import MutableSequence
from mathtools import Vec2, mVec2
from mathtools.pymath import RotMatrix, Array

__all__ = ['VecArray']


class VecArray(MutableSequence):
    __slots__ = ['_data']

    def __init__(self, data):
        '''Implementa um array de vetores bidimensionais. As operações
        matemáticas podem ser aplicadas diretamente ao array

        Exemplo
        -------

        Criamos um array inicializando com uma lista de vetores ou uma lista
        de duplas

        >>> a = VecArray([(0, 0), (1, 0), (0, 1)]); a
        VecArray([(0, 0), (1, 0), (0, 1)])

        Sob muitos aspectos, um VecArray funciona como uma lista de vetores

        >>> a[0], a[1]
        (Vec2(0, 0), Vec2(1, 0))

        As operações matemáticas ocorrem termo a termo

        >>> a + (1, 1)
        VecArray([(1, 1), (2, 1), (1, 2)])

        Já as funções de vetores são propagadas para cada elemento e retornam
        um Array numérico ou um VecArray

        >>> a.norm()
        Array([0, 1, 1])
        '''

        self._data = list(mVec2(x) for x in data)

    def _new(self, data):
        return self.__class__(data)

    def as_tuple(self):
        '''Retorna uma lista de tuplas'''
        return [u.as_tuple() for u in self._data]

    def norm(self):
        '''Retorna um Array com o módulo de cada vetor'''

        return Array([u.norm() for u in self._data])

    def norm_sqr(self):
        '''Retorna o módulo do vetor ao quadrado'''

        return Array([u.norm_sqr() for u in self._data])

    def normalize(self):
        '''Retorna um vetor unitário'''

        return VecArray([u.normalize() for u in self._data])

    def rotate(self, theta, axis=None):
        '''Retorna um vetor rotacionado por um ângulo theta'''

        axis = Vec2(axis)
        R = RotMatrix(theta)
        if axis is None:
            return VecArray([R * u for u in self._data])
        else:
            v = axis
            return VecArray([v + R * (u - v) for u in self._data])

    # Métodos inplace #########################################################
    def irotate(self, theta, axis=None):
        pass

    # Métodos mágicos #########################################################
    def __len__(self):
        return len(self._data)

    def __repr__(self):
        '''x.__repr__() <==> repr(x)'''

        out = []
        for v in self:
            x, y = v
            x = str(x) if x != int(x) else str(int(x))
            y = str(y) if y != int(y) else str(int(y))
            out.append('(%s, %s)' % (x, y))

        tname = type(self).__name__
        return '%s([%s])' % (tname, ', '.join(out))

    def __str__(self):
        '''x.__str__() <==> str(x)'''
        return repr(self)

    def __iter__(self):
        return iter(Vec2(u) for u in self._data)

    def __getitem__(self, i):
        '''x.__getitem__(i) <==> x[i]'''

        return Vec2(self._data[i])

    def __setitem__(self, i, value):
        self._data[i].update(value)

    def __delitem__(self, i):
        del self._data[i]

    def insert(self, idx, value):
        self._data.insert(idx, mVec2(value))

    # Operações matemáticas ###################################################
    def __mul__(self, other):
        '''x.__mul__(y) <==> x * y'''

        return self._new(u * other for u in self._data)

    def __rmul__(self, other):
        '''x.__rmul__(y) <==> y * x'''

        return self._new(other * u for u in self._data)

    def __div__(self, other):
        '''x.__div__(y) <==> x / y'''

        return self._new(u / other for u in self._data)

    __truediv__ = __div__  # Python 3

    def __add__(self, other):
        '''x.__add__(y) <==> x + y'''

        other = Vec2(other)
        return self._new(u + other for u in self._data)

    def __radd__(self, other):
        '''x.__radd__(y) <==> y + x'''

        return self + other

    def __sub__(self, other):
        '''x.__sub__(y) <==> x - y'''

        other = Vec2(other)
        return self._new(u - other for u in self._data)

    def __rsub__(self, other):
        '''x.__rsub__(y) <==> y - x'''

        other = Vec2(other)
        return self._new(other - u for u in self._data)

    def __neg__(self):
        '''x.__neg() <==> -x'''

        return self._new(-u for u in self._data)

    def __nonzero__(self):
        return len(self) != 0

    def __eq__(self, other):
        return all(u == other for u in self._data)

    @property
    def _x(self):
        return Array([u._x for u in self._data])

    @property
    def y(self):
        return Array([u.y for u in self._data])


if __name__ == '__main__':
    import doctest
    doctest.testmod()
