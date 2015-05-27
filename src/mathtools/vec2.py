# -*- coding: utf8 -*-

import cython as C
import mathtools as m
import decimal
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

    def almost_equals(self , other, delta_angle = 1/1000 , delta_norm = 1/1000):
        '''Verifica se o vetor é quase igual a outro

        Exemplo:
        ---------
        >>> v = Vec2(3,4)
        >>> other = Vec2(3.00001, 4.00001)
        >>> v.almost_equals(other)
        True
        '''

        # Faz o teste primeiramente com o angulo entre os dois vetores
        if ( self.angle(other) < delta_angle ):
            # Testa o tamanho dos vetores com base no delta
            if (self.norm() <= other.norm() + delta_norm and self.norm() >= other.norm() - delta_norm):
                return True
            else:
                return False 
        else:
            return False


    def distance_to(self, other):
        '''Retorna a distância entre dois vetores

        Exemplo
        --------
        >>> v = Vec2(0,5)
        >>> other = Vec2(0,0)
        >>> v.distance_to(other)
        5.0
        '''

        distance = m.sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

        return distance

    def angle(self, other):
        '''Retorna o ângulo entre dois vetores em radianos

        Exemplo
        --------
        >>> v = Vec2(5,0)
        >>> other = Vec2(0,5)
        >>> v.angle(other)
        1.5707963267948966
        '''
        return m.acos((self.dot(other))/(self.norm()*other.norm()))

    def is_null(self):
        '''Verifica se o vetor é nulo

        Exemplo
        --------
        >>> v = Vec2(0,0)
        >>> v.is_null()
        True
        '''

        if self == Vec2(0,0):
            return True
        else:
            return False

    def polar(self):
        '''Retorna o vetor com suas coordenadas polares em forma de tupla

        Exemplo
        --------
        >>> v = Vec2(1,0)
        >>> v.polar()
        (1.0, 0.0)
        '''
        radius = self.norm()
        x_unit = Vec2(1,0)
        angle = self.angle(x_unit)

        polar = (radius, angle)

        return polar

    def reflect(self, other):
        '''Retorna o vetor refletido por outro vetor

        Exemplo
        --------
        >>> v = Vec2(3,4)
        >>> other = Vec2(1,0)
        >>> v.reflect(other)
        Vec2(3, -4)
        ''' 
        # confere se algum dos vetores é nulo
        if ( other.is_null() or self.is_null() ):

            return self
        else:

            angle = self.angle(other)

            if ( other.x < 0 ):
                reflect = self.rotate(2*angle)
            else:
                reflect = self.rotate(-2*angle)

            reflect.x = round(reflect.x,4)
            reflect.y = round(reflect.y,4)

            return reflect

    def lerp(self, other , range_lerp):
        '''Retorna um vetor com tamanho máximo baseado no vetor resultante da
        diferença entre dois vetores, sendo que o range_lerp assume valores
        entre 0 e 1.

        Exemplo
        --------
        >>> v = Vec2(1,0)
        >>> v1 = Vec2(0,1)
        >>> v.lerp(v1, 0)
        Vec2(1, 0)
        '''

        if range_lerp > 1 or range_lerp < 0:

            lerp = self
        else:
            subtraction_vectors = other - self

            lerp = subtraction_vectors * range_lerp + self

        return lerp

    def perpendicular(self , inverse = False):
        '''Retorna um vetor 2d perpendicular a ele, sendo que a convenção do
        parametro inverse é o sentido anti-horário

        Exemplo
        --------
        >>> v = Vec2(1,0)
        >>> v.perpendicular(True)
        Vec2(0, -1)
        '''

        if ( inverse == False ):
            perpendicular = self.rotate(m.pi/2)

        else:
            perpendicular = self.rotate(-m.pi/2)

        perpendicular.x = round(perpendicular.x, 7)
        perpendicular.y = round(perpendicular.y, 7)

        return perpendicular

    def project(self, other):
        '''Retorna um vetor que é a projeção do mesmo na direção do segundo vetor

        Exemplo
        --------
        >>> v = Vec2(3,4)
        >>> other = Vec2(1,0)
        >>> v.project(other)
        Vec2(3, 0)
        '''

        dot = self.dot(other)
        module_square = other.norm_sqr()

        return dot*other/module_square

    def clamp(self, minimum, maximum):
        '''Retorna um vetor na mesma direção com o módulo baseado entre os valores
        minimo e máximo.Se for menor que o máximo, retorna um vetor com módulo igual ao 
        mínimo , se for maior que o máximo, retorna um vetor com módulo igual ao
        máximo.

        Exemplo
        --------
        >>> v = Vec2(3,4)
        >>> v.clamp(7,9)
        Vec2(4.2, 5.6)
        '''

        if self.norm() < maximum:
            distance_min_max = minimum/self.norm()
        else:
            distance_min_max = maximum/self.norm()
        
        self = self * distance_min_max
        self.x = round(self.x, 8)
        self.y = round(self.y, 8)

        return self

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
