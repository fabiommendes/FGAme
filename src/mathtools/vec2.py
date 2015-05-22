# -*- coding: utf8 -*-

import cython as C
import mathtools as m
import math
from mathtools.base import auto_public
from mathtools.util import pyinject

__all__ = ['Vec2', 'VecSlot', 'null2D']


###############################################################################
#                              Vector 2D
###############################################################################
class Vec2(object):

    '''Representa um vetor bidimensional.

    Objetos do tipo `Vec2()` são imutáveis. Algumas implementações podem
    proteger explicitamente os atributos do vetor, enquanto outras não. É
    responsabilidade do usuário não tentar nenhum tipo de manipulação direta
    das coordenadas x e y do vetor.

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

    >>> v.norm(); abs(v)
    5.0
    5.0

    >>> v.normalize()
    Vec2(0.6, 0.8)
    '''
    if not C.compiled:
        __slots__ = ['x', 'y']
    else:
        __slots__ = []

    def __init__(self, x_or_data, y=None):
        if y is None:
            x, y = x_or_data
        else:
            x = x_or_data
        self.x = x
        self.y = y

    @classmethod
    def from_seq(cls, data):
        '''Inicializa vetor a partir de uma sequência com as coordenadas x e
        y'''

        if data.__class__ is Vec2:
            return data
        x, y = data
        return cls.from_coords(x, y)

    @staticmethod
    @C.locals(x='double', y='double', new='double')
    def from_coords(x, y):
        '''Inicializa vetor a partir das coordenadas'''

        # Um pouco mais rápido que chamar Vec2(x, y) diretamente.
        # Evita um pouco da lógica dentro do método __init__
        new = Vec2.__new__(Vec2, x, y)
        new.x = x
        new.y = y
        return new

    @C.locals(x='double', y='double', new='Vec2')
    def _from_coords(self, x, y):
        new = Vec2.__new__(Vec2, x, y)
        new.x = x
        new.y = y
        return new

    def as_tuple(self):
        '''Retorna a representação do vetor como uma tupla'''

        return (self.x, self.y)

    def is_null(self):
        '''
        Verifica se o vetor é nulo

        Exemplo
        --------
        >>> Vec2.is_null(Vec2(0,0))
        True
        '''

        if self == Vec2(0,0):
            return True
        else:
            return False

    def distance_to(self, v2):
        '''Retorna a distância entre dois vetores

        Exemplo
        --------

        >>> Vec2.distance_to(Vec2(0,5), Vec2(0,0))
        5.0
        '''

        distance = math.sqrt((v2.x - self.x) ** 2 + (v2.y - self.y) ** 2)

        return distance

    def angle(self, v2):
        '''Retorna o ângulo entre dois vetores em radianos

        Exemplo
        --------
        >>> Vec2.angle(Vec2(5,0),Vec2(0,5))
        pi/2
        '''
        return math.acos((self.dot(v2))/(self.norm()*v2.norm()))

    def almost_equals(self , v2):
        '''Verifica se o vetor é quase igual a outro

        Exemplo:
        ---------
        >>> Vec2.almost_equals(Vec2(3.00001 , 4.00001) , Vec2(3,4))
        True
        '''
        delta_angle = 1/1000
        delta_norm = 1/1000

        # Faz o teste primeiramente com o angulo entre os dois vetores
        if ( self.angle(v2) < delta_angle ):
            # Testa o tamanho dos vetores com base no delta
            if (self.norm() <= v2.norm() + delta_norm and self.norm() >= v2.norm() - delta_norm):
                return True
            else:
                return False 
        else:
            return False

    def norm(self): 
        '''Retorna o módulo (norma) do vetor'''

        return m.sqrt(self.x ** 2 + self.y ** 2)
    

    def norm_sqr(self):
        '''Retorna o módulo do vetor ao quadrado'''

        return self.x ** 2 + self.y ** 2

    def normalize(self):
        '''Retorna um vetor unitário'''

        norm = self.norm()
        return (self._from_coords(self.x / norm, self.y / norm)
                if norm else self._from_coords(0, 0))

    @C.locals(theta='double', x='double', y='double',
              dx='double', dy='double', cos_t='double', sin_t='double')
    def rotate(self, theta, axis=(0, 0)):
        '''Retorna um vetor rotacionado por um ângulo theta'''

        x, y = axis
        dx = self.x - x
        dy = self.y - y
        cos_t, sin_t = m.cos(theta), m.sin(theta)
        return self._from_coords(
            dx * cos_t - dy * sin_t + x,
            dx * sin_t + dy * cos_t + y)

    @C.locals(x='double')
    def flip_x(self, x=0.0):
        '''Retorna uma cópia com a coordenada x espelhada em torno do ponto
        dado'''

        return self._from_coords(x - self.x, self.y)

    @C.locals(y='double')
    def flip_y(self, y=0.0):
        '''Retorna uma cópia com a coordenada x espelhada em torno do ponto
        dado'''

        return self._from_coords(self.x, y - self.y)

    @C.locals(height='int')
    def screen_coords(self, height=600):
        '''Converte o vetor para um sistema de coordenadas onde o eixo y aponta
        para baixo a partir do topo da tela. É necessário especificar a altura
        da tela para realizar a conversão. Retorna uma tupla com os valores
        truncados.'''

        return m.trunc(self.x), height - m.trunc(self.y)

    def trunc(self):
        '''Retorna uma tupla com os valores das coordenadas x e y truncados'''

        return m.trunc(self.x), m.trunc(self.y)

    @C.locals(vec='Vec2', x='double', y='double')
    def dot(self, other):
        '''Retorna o resultado do produto escalar com outro vetor

        Exemplo
        -------

        >>> Vec2(1, 0).dot(Vec2(0, 1))
        0.0
        '''

        try:
            vec = other
            return vec.x * self.x + vec.y * self.y
        except (TypeError, AttributeError):
            x, y = other
            return self.x * x + self.y * y

    @C.locals(vec='Vec2', x='double', y='double')
    def cross(self, other):
        '''Retorna o resultado da componente z do produto vetorial com outro
        vetor

        Exemplo
        -------

        >>> Vec2(1, 0).cross(Vec2(0, 1))
        1.0
        '''

        try:
            vec = other
            return self.x * vec.y - self.y * vec.x
        except (TypeError, AttributeError):
            x, y = other
            return self.x * y - self.y * x

    # Métodos mágicos #########################################################
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

    def __hash__(self):
        return hash(self.x) ^ hash(self.y)

    # Operações aritiméticas ##################################################
    @C.locals(A='Vec2', B='double')
    def __mul__(self, other):
        '''x.__mul__(y) <==> x * y'''

        try:
            A = self
            B = other
        except TypeError:
            try:
                A = other
                B = self
            except TypeError:
                return other.__rmul__(self)

        return A._from_coords(A.x * B, A.y * B)

    def __rmul__(self, other):
        '''x.__rmul__(y) <==> y * x'''

        return self * other

    @C.locals(self='Vec2', other='double')
    def __div__(self, other):
        '''x.__div__(y) <==> x / y'''

        return self._from_coords(self.x / other, self.y / other)

    @C.locals(self='Vec2', other='double')
    def __truediv__(self, other):
        '''x.__div__(y) <==> x / y'''

        return self._from_coords(self.x / other, self.y / other)

    @C.locals(A='Vec2', B='Vec2', x='double', y='double')
    def __add__(self, other):
        '''x.__add__(y) <==> x + y'''

        try:
            A = self
            B = other
            return A._from_coords(A.x + B.x, A.y + B.y)
        except (TypeError, AttributeError):
            try:
                A = self
                x, y = other
            except TypeError:
                A = other
                x, y = self
            return A._from_coords(A.x + x, A.y + y)

    def __radd__(self, other):
        '''x.__radd__(y) <==> y + x'''

        return self + other

    @C.locals(A='Vec2', B='Vec2', x='double', y='double')
    def __sub__(self, other):
        '''x.__sub__(y) <==> x - y'''

        try:
            A = self
            B = other
            return A._from_coords(A.x - B.x, A.y - B.y)
        except (TypeError, AttributeError):
            try:
                A = self
                x, y = other
                return A._from_coords(A.x - x, A.y - y)
            except TypeError:
                B = other
                x, y = self
                return B._from_coords(x - B.x, y - B.y)

    def __rsub__(self, other):
        '''x.__rsub__(y) <==> y - x'''
        try:
            return self._from_coords(other.x - self.x, other.y - self.y)
        except AttributeError:
            x, y = other
            return self._from_coords(x - self.x, y - self.y)

    def __neg__(self):
        '''x.__neg() <==> -x'''

        return self._from_coords(-self.x, -self.y)

    def __nonzero__(self):
        if (self.x == 0) and (self.y == 0):
            return False
        else:
            return True

    def __abs__(self):
        return self.norm()

    @C.locals(method='int', x='double', y='double')
    def __richcmp__(self, other, method):
        if method == 2:    # igual (==)
            x, y = other
            return self.x == x and self.y == y
        elif method == 3:  # diferente (!=)
            x, y = other
            return self.x != x or self.y != y
        else:
            raise TypeError('invalid rich comparison: %s' % method)

    # Ganchos para implementações mutáveis ####################################
    def _setx(self, x):
        self.x = x

    def _sety(self, y):
        self.y = y

    def _setxy(self, x, y):
        self.x = x
        self.y = y

    def _setitem(self, i, value):
        if i == 0:
            self.x = value + 0.0
        elif i == 1:
            self.y = value + 0.0
        else:
            raise IndexError

    @C.locals(x='double', y='double', vec='Vec2')
    def _iadd(self, other):
        '''x.__iadd__(y) <==> x += y'''

        try:
            vec = other
            self.x += vec.x
            self.y += vec.y
        except TypeError:
            x, y = other
            self.x += x
            self.y += y
        return self

    @C.locals(x='double', y='double', vec='Vec2')
    def _isub(self, other):
        '''x.__isub__(y) <==> x -= y'''

        try:
            vec = other
            self.x -= vec.x
            self.y -= vec.y
        except TypeError:
            x, y = other
            self.x -= x
            self.y -= y
        return self

    @C.locals(other='double')
    def _imul(self, other):
        '''x.__imul__(y) <==> x *= y'''

        self.x *= other
        self.y *= other
        return self

    @C.locals(other='double')
    def _idiv(self, other):
        '''x.__idiv__(y) <==> x /= y'''

        self.x /= other
        self.y /= other
        return self

    @C.locals(other='double')
    def _itruediv(self, other):
        '''x.__idiv__(y) <==> x /= y'''

        self.x /= other
        self.y /= other
        return self

    @C.locals(theta='double', x='double', y='double',
              dx='double', dy='double', cos_t='double', sin_t='double')
    def _irotate(self, theta, axis=(0, 0)):
        '''Rotaciona o vetor *inplace*'''

        x, y = axis
        dx = self.x - x
        dy = self.y - y
        cos_t, sin_t = m.cos(theta), m.sin(theta)
        self.x = dx * cos_t - dy * sin_t + x
        self.y = dx * sin_t + dy * cos_t + y

    def _inormalize(self):
        '''Normaliza o vetor *inplace*'''

        self /= self.norm()

    def _update(self, other, y=None):
        '''Copia as coordenadas x, y do objeto other'''

        if y is None:
            x, y = other
        else:
            x = other
        self.x = x + 0.0
        self.y = y + 0.0

    def _copy(self):
        '''Retorna uma cópia de si mesmo'''

        return self._from_coords(self.x, self.y)

    __dict__ = {}

null2D = Vec2(0, 0)

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
            self.x = x + 0.0
            self.y = y + 0.0

        @staticmethod
        def _from_coords(x, y):
            tt = Vec2
            new = tt.__new__(tt, x, y)
            new.x = x + 0.0
            new.y = y + 0.0
            return new

        def __mul__(self, other):
            '''x.__mul__(y) <==> x * y'''

            try:
                other = float(other)
            except TypeError:
                return other.__rmul__(self)
            return self._from_coords(self.x * other, self.y * other)

        def __eq__(self, other):
            x, y = other
            return self.x == x and self.y == y

    auto_public(Vec2)

###############################################################################
#                         Propriedades vetoriais
###############################################################################


class VecSlot(object):
    if C.compiled:
        __slots__ = []
    else:
        __slots__ = ['getter', 'setter']

    def __init__(self, slot):
        self.setter = slot.__set__
        self.getter = slot.__get__

    def __get__(self, obj, tt):
        return self.getter(obj, tt)

    def __set__(self, obj, value):
        if not isinstance(value, Vec2):
            value = Vec2.from_seq(value)
        self.setter(obj, value)

    def update_class(self, tt=None, *args):
        '''Update all enumerated slots/descriptors in class to be VecSlots'''

        if tt is None:
            def decorator(tt):
                self.update_class(tt, *args)
                return tt
            return decorator

        for sname in args:
            slot = getattr(tt, sname)
            setattr(tt, sname, VecSlot(slot))


if __name__ == '__main__' and not C.compiled:
    import doctest
    doctest.testmod()
