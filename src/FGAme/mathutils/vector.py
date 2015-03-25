# -*- coding: utf8 -*-

from math import sqrt, sin, cos

SQRT_2 = sqrt(2)

__all__ = ['Vector', 'VectorM', 'asvector', 'dot', 'cross']


class Vector(object):
    __slots__ = ['_x', '_y']

    def __init__(self, x, y):
        '''Representa um vetor bidimensional.

        Exemplo
        -------

        Criamos um vetor chamando a classe com as componentes como argumento.

        >>> v = Vector(3, 4); print(v)
        Vector(3, 4)

        Os métodos de listas funcionam para objetos do tipo Vector:

        >>> v[0], v[1], len(v)
        (3.0, 4.0, 2)

        Objetos do tipo Vector também aceitam operações matemáticas

        >>> v + 2 * v
        Vector(9, 12)

        Além de algumas funções de conveniência para calcular o módulo,
        vetor unitário, etc.

        >>> v.norm()
        5.0

        >>> v.normalized()
        Vector(0.6, 0.8)
        '''

        try:
            self._x = float(x)
            self._y = float(y)
        except TypeError:
            raise TypeError('invalid arguments: x=%r, y=%r' % (x, y))

    def as_tuple(self):
        '''Retorna a representação do vetor como uma tupla'''
        return (self._x, self._y)

    def norm(self):
        '''Retorna o módulo (norma) do vetor'''

        return sqrt(self._x ** 2 + self._y ** 2)

    def norm_sqr(self):
        '''Retorna o módulo do vetor ao quadrado'''

        return self._x ** 2 + self._y ** 2

    def normalized(self):
        '''Retorna um vetor unitário'''

        norm = self.norm()
        return self / norm if norm else Vector(*self)

    def rotated(self, theta, axis=(0, 0)):
        '''Retorna um vetor rotacionado por um ângulo theta'''

        x, y = self - axis
        cos_t, sin_t = cos(theta), sin(theta)
        return type(self)(x * cos_t - y * sin_t, x * sin_t + y * cos_t) + axis

    # Métodos mágicos --------------------------------------------------------
    def __len__(self):
        return 2

    def __repr__(self):
        '''x.__repr__() <==> repr(x)'''

        x, y = self
        x = str(x) if x != int(x) else str(int(x))
        y = str(y) if y != int(y) else str(int(y))
        tname = type(self).__name__
        return '%s(%s, %s)' % (tname, x, y)

    def __str__(self):
        '''x.__str__() <==> str(x)'''
        return repr(self)

    def __iter__(self):
        yield self._x
        yield self._y

    def __getitem__(self, i):
        '''x.__getitem__(i) <==> x[i]'''
        if i == 0:
            return self._x
        elif i == 1:
            return self._y
        else:
            raise IndexError(i)

    def __mul__(self, other):
        '''x.__mul__(y) <==> x * y'''
        return type(self)(self._x * other, self._y * other)

    def __rmul__(self, other):
        '''x.__rmul__(y) <==> y * x'''
        return self * other

    def __div__(self, other):
        '''x.__div__(y) <==> x / y'''
        return type(self)(self._x / other, self._y / other)

    __truediv__ = __div__  # Python 3

    def __add__(self, other):
        '''x.__add__(y) <==> x + y'''
        x, y = other
        return type(self)(self._x + x, self._y + y)

    def __radd__(self, other):
        '''x.__radd__(y) <==> y + x'''
        return self + other

    def __sub__(self, other):
        '''x.__sub__(y) <==> x - y'''
        x, y = other
        return type(self)(self._x - x, self._y - y)

    def __rsub__(self, other):
        '''x.__rsub__(y) <==> y - x'''
        x, y = other
        return type(self)(x - self._x, y - self._y)

    def __neg__(self):
        '''x.__neg() <==> -x'''
        return type(self)(-self._x, -self._y)

    def __nonzero__(self):
        return True

    def __eq__(self, other):
        x, y = other
        return self._x == x and self._y == y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y


class VectorM(Vector):

    '''Como Vector, mas com elementos mutáveis'''

    def __iadd__(self, other):
        '''x.__iadd__(y) <==> x += y'''

        self._x += other[0]
        self._y += other[1]
        return self

    def __isub__(self, other):
        '''x.__isub__(y) <==> x -= y'''

        self._x -= other[0]
        self._y -= other[1]
        return self

    def __imul__(self, other):
        '''x.__imul__(y) <==> x *= y'''

        self._x *= other
        self._y *= other
        return self

    def __idiv__(self, other):
        '''x.__idiv__(y) <==> x /= y'''

        self._x /= other
        self._y /= other
        return self

    __itruediv__ = __idiv__

    def rotate(self, theta, axis=(0, 0)):
        '''Realiza rotação *inplace*'''

        x, y = self - axis
        cos_t, sin_t = cos(theta), sin(theta)
        self._x = x * cos_t - y * sin_t + axis[0]
        self._y = x * sin_t + y * cos_t + axis[1]

    def copy_from(self, other):
        '''Copia as coordenadas x, y do objeto other'''

        try:
            self._x = other._x
            self._y = other._y
        except AttributeError:
            self._x = other[0]
            self._y = other[1]

    def copy(self):
        '''Retorna uma cópia de si mesmo'''

        return VectorM(self._x, self._y)

    x = property(Vector.x.fget)
    y = property(Vector.y.fget)

    @x.setter
    def x(self, value):
        self._x = float(value)

    @y.setter
    def y(self, value):
        self._y = float(value)


def asvector(v):
    '''Retorna o objeto como uma instância da classe Vetor'''

    if isinstance(v, Vector):
        return v
    else:
        return Vector(*v)


def dot(v1, v2):
    '''Calcula o produto escalar entre dois vetores'''

    return sum(x * y for (x, y) in zip(v1, v2))


def cross(v1, v2):
    '''Retorna a compontente z do produto vetorial de dois vetores
    bidimensionais'''

    x1, y1 = v1
    x2, y2 = v2
    return x1 * y2 - x2 * y1

if __name__ == '__main__':
    import doctest
    doctest.testmod()
