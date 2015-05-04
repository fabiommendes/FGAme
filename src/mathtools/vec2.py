# -*- coding: utf8 -*-

import cython as C
import mathtools as m
from mathtools.base import auto_public
from mathtools.util import pyinject

__all__ = ['Vec2', 'mVec2']


###############################################################################
#                              Vector 2D
###############################################################################
class Vec2(object):

    '''Representa um vetor bidimensional.

    Exemplo
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

    >>> v.norm()
    5.0

    >>> v.normalize()
    Vec2(0.6, 0.8)
    '''

    if not C.compiled:
        __slots__ = ['_x', '_y']
    else:
        __slots__ = []

    def __init__(self, x_or_data, y=None):
        if y is None:
            x, y = x_or_data
        else:
            x = x_or_data
        self._x = x
        self._y = y

    @classmethod
    def from_seq(cls, data):
        '''Inicializa vetor a partir de uma sequência com as coordenadas x e
        y'''
        x, y = data
        return cls.from_coords(x, y)

    @staticmethod
    @C.locals(x='double', y='double', new='double')
    def from_coords(x, y):
        '''Inicializa vetor a partir das coordenadas'''

        # Um pouco mais rápido que chamar Vec2(x, y) diretamente.
        # Evita um pouco da lógica dentro do método __init__
        new = Vec2.__new__(Vec2, x, y)
        new._x = x
        new._y = y
        return new

    @C.locals(x='double', y='double', new='Vec2')
    def _from_coords(self, x, y):
        new = Vec2.__new__(Vec2, x, y)
        new._x = x
        new._y = y
        return new

    def as_tuple(self):
        '''Retorna a representação do vetor como uma tupla'''

        return (self._x, self._y)

    def norm(self):
        '''Retorna o módulo (norma) do vetor'''

        return m.sqrt(self._x ** 2 + self._y ** 2)

    def norm_sqr(self):
        '''Retorna o módulo do vetor ao quadrado'''

        return self._x ** 2 + self._y ** 2

    def normalize(self):
        '''Retorna um vetor unitário'''

        norm = self.norm()
        return (self._from_coords(self._x / norm, self._y / norm)
                if norm else self._from_coords(0, 0))

    @C.locals(theta='double', x='double', y='double',
              dx='double', dy='double', cos_t='double', sin_t='double')
    def rotate(self, theta, axis=(0, 0)):
        '''Retorna um vetor rotacionado por um ângulo theta'''

        x, y = axis
        dx = self._x - x
        dy = self._y - y
        cos_t, sin_t = m.cos(theta), m.sin(theta)
        return self._from_coords(
            dx * cos_t - dy * sin_t + x,
            dx * sin_t + dy * cos_t + y)

    @C.locals(x='double')
    def flip_x(self, x=0.0):
        '''Retorna uma cópia com a coordenada x espelhada em torno do ponto
        dado'''

        return self._from_coords(x - self._x, self._y)

    @C.locals(y='double')
    def flip_y(self, y=0.0):
        '''Retorna uma cópia com a coordenada x espelhada em torno do ponto
        dado'''

        return self._from_coords(self._x, y - self._y)

    @C.locals(height='int')
    def screen_coords(self, height=600):
        '''Converte o vetor para um sistema de coordenadas onde o eixo y aponta
        para baixo a partir do topo da tela. É necessário especificar a altura
        da tela para realizar a conversão. Retorna uma tupla com os valores
        truncados.'''

        return m.trunc(self._x), height - m.trunc(self._y)

    def trunc(self):
        '''Retorna uma tupla com os valores das coordenadas x e y truncados'''

        return m.trunc(self._x), m.trunc(self._y)

    @C.locals(vec='Vec2', x='double', y='double')
    def dot(self, other):
        '''Retorna o resultado do produto escalar com outro vetor'''

        try:
            vec = other
            return vec._x * self._x + vec._y * self._y
        except (TypeError, AttributeError):
            x, y = other
            return self._x * x + self._y * y

    @C.locals(vec='Vec2', x='double', y='double')
    def cross(self, other):
        '''Retorna o resultado da componente z do produto vetorial com outro
        vetor'''
        try:
            vec = other
            return self._y * vec._x - self._y * vec._x
        except (TypeError, AttributeError):
            x, y = other
            return self._y * x - self._x * y

    # Métodos mágicos #########################################################
    def __repr__(self):
        '''_x.__repr__() <==> repr(_x)'''

        x, y = self
        x = str(x) if x != int(x) else str(int(x))
        y = str(y) if y != int(y) else str(int(y))
        tname = type(self).__name__
        return '%s(%s, %s)' % (tname, x, y)

    def __str__(self):
        '''_x.__str__() <==> str(_x)'''

        return repr(self)

    def __len__(self):
        return 2

    def __iter__(self):
        yield self._x
        yield self._y

    def __getitem__(self, i):
        '''_x.__getitem__(i) <==> _x[i]'''

        if i == 0:
            return self._x
        elif i == 1:
            return self._y
        else:
            raise IndexError(i)

    def __hash__(self):
        return hash(self._x) ^ hash(self._y)

    # Operações aritiméticas ##################################################
    @C.locals(A='Vec2', B='double')
    def __mul__(self, other):
        '''_x.__mul__(y) <==> _x * y'''

        try:
            A = self
            B = other
        except TypeError:
            try:
                A = other
                B = self
            except TypeError:
                return other.__rmul__(self)

        return A._from_coords(A._x * B, A._y * B)

    def __rmul__(self, other):
        '''_x.__rmul__(y) <==> y * _x'''

        return self * other

    @C.locals(self='Vec2', other='double')
    def __div__(self, other):
        '''_x.__div__(y) <==> _x / y'''

        return self._from_coords(self._x / other, self._y / other)

    @C.locals(self='Vec2', other='double')
    def __truediv__(self, other):
        '''_x.__div__(y) <==> _x / y'''

        return self._from_coords(self._x / other, self._y / other)

    @C.locals(A='Vec2', B='Vec2', x='double', y='double')
    def __add__(self, other):
        '''_x.__add__(y) <==> _x + y'''

        try:
            A = self
            B = other
            return A._from_coords(A._x + B._x, A._y + B._y)
        except (TypeError, AttributeError):
            try:
                A = self
                x, y = other
            except TypeError:
                A = other
                x, y = self
            return A._from_coords(A._x + x, A._y + y)

    def __radd__(self, other):
        '''_x.__radd__(y) <==> y + _x'''

        return self + other

    @C.locals(A='Vec2', B='Vec2', x='double', y='double')
    def __sub__(self, other):
        '''_x.__sub__(y) <==> _x - y'''

        try:
            A = self
            B = other
            return A._from_coords(A._x - B._x, A._y - B._y)
        except (TypeError, AttributeError):
            try:
                A = self
                x, y = other
                return A._from_coords(A._x - x, A._y - y)
            except TypeError:
                B = other
                x, y = self
                return B._from_coords(x - B._x, y - B._y)

    def __rsub__(self, other):
        '''_x.__rsub__(y) <==> y - _x'''
        try:
            return self._from_coords(other._x - self._x, other._y - self._y)
        except AttributeError:
            x, y = other
            return self._from_coords(x - self._x, y - self._y)

    def __neg__(self):
        '''_x.__neg() <==> -_x'''

        return self._from_coords(-self._x, -self._y)

    def __nonzero__(self):
        if (self._x == 0) and (self._y == 0):
            return False
        else:
            return True

    def __abs__(self):
        return self.norm()

    @C.locals(method='int', x='double', y='double')
    def __richcmp__(self, other, method):
        if method == 2:    # igual (==)
            x, y = other
            return self._x == x and self._y == y
        elif method == 3:  # diferente (!=)
            x, y = other
            return self._x != x or self._y != y
        else:
            raise TypeError('invalid rich comparison: %s' % method)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y


###############################################################################
#                            Mutable Vector 2D
###############################################################################


class mVec2(Vec2):

    '''Como Vec2, mas com elementos mutáveis'''

    @C.locals(x='double', y='double', new='Vec2')
    def _from_coords(self, x, y):
        new = mVec2.__new__(mVec2, x, y)
        new._x = x
        new._y = y
        return new

    def __setitem__(self, i, value):
        if i == 0:
            self._x = value + 0.0
        elif i == 1:
            self._y = value + 0.0
        else:
            raise IndexError

    @C.locals(x='double', y='double', vec='Vec2')
    def __iadd__(self, other):
        '''_x.__iadd__(y) <==> _x += y'''

        try:
            vec = other
            self._x += vec._x
            self._y += vec._y
        except TypeError:
            x, y = other
            self._x += x
            self._y += y
        return self

    @C.locals(x='double', y='double', vec='Vec2')
    def __isub__(self, other):
        '''_x.__isub__(y) <==> _x -= y'''

        try:
            vec = other
            self._x -= vec._x
            self._y -= vec._y
        except TypeError:
            x, y = other
            self._x -= x
            self._y -= y
        return self

    @C.locals(other='double')
    def __imul__(self, other):
        '''_x.__imul__(y) <==> _x *= y'''

        self._x *= other
        self._y *= other
        return self

    @C.locals(other='double')
    def __idiv__(self, other):
        '''_x.__idiv__(y) <==> _x /= y'''

        self._x /= other
        self._y /= other
        return self

    @C.locals(other='double')
    def __itruediv__(self, other):
        '''_x.__idiv__(y) <==> _x /= y'''

        self._x /= other
        self._y /= other
        return self

    @C.locals(theta='double', x='double', y='double',
              dx='double', dy='double', cos_t='double', sin_t='double')
    def irotate(self, theta, axis=(0, 0)):
        '''Rotaciona o vetor *inplace*'''

        x, y = axis
        dx = self._x - x
        dy = self._y - y
        cos_t, sin_t = m.cos(theta), m.sin(theta)
        self._x = dx * cos_t - dy * sin_t + x
        self._y = dx * sin_t + dy * cos_t + y

    def inormalize(self):
        '''Normaliza o vetor *inplace*'''

        self /= self.norm()

    def update(self, other, y=None):
        '''Copia as coordenadas x, y do objeto other'''

        if y is None:
            x, y = other
        else:
            x = other
        self._x = x + 0.0
        self._y = y + 0.0

    def copy(self):
        '''Retorna uma cópia de si mesmo'''

        return self._from_coords(self._x, self._y)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, value):
        self._x = value + 0.0

    @y.setter
    def y(self, value):
        self._y = value + 0.0

    def __hash__(self):
        raise TypeError

###############################################################################
#               Código injetado para rodar no modo interpretado
###############################################################################

if not C.compiled:
    @pyinject(globals())
    class Vec2Inject:

        '''Implementa métodos que tem algum tipo de problema de performance
        ou de semântica diferente entre Cython e o Python interpretado'''

        def __init__(self, x_or_data, y=None):
            if y is None:
                x, y = x_or_data
            else:
                x = x_or_data
            self._x = x + 0.0
            self._y = y + 0.0

        @staticmethod
        def _from_coords(x, y):
            tt = Vec2
            new = tt.__new__(tt, x, y)
            new._x = x + 0.0
            new._y = y + 0.0
            return new

        def __mul__(self, other):
            '''_x.__mul__(y) <==> _x * y'''

            try:
                other = float(other)
            except TypeError:
                return other.__rmul__(self)
            return self._from_coords(self._x * other, self._y * other)

        def __eq__(self, other):
            x, y = other
            return self._x == x and self._y == y

    @pyinject(globals())
    class mVec2Inject:

        @staticmethod
        def _from_coords(x, y):
            tt = mVec2
            new = tt.__new__(tt, x, y)
            new._x = x + 0.0
            new._y = y + 0.0
            return new

    auto_public(Vec2)

if __name__ == '__main__' and not C.compiled:
    import doctest
    doctest.testmod()
