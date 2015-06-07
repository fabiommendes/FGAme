# -*- coding: utf8 -*-

import cython as C
import mathtools as m
import decimal
from mathtools.base import auto_public
from mathtools.util import pyinject
from mathtools.vec2 import Vec2

__all__ = ['Vec3', 'VecSlot', 'nullvec3']


###############################################################################
#                              Vector 3D
###############################################################################
class Vec3(object):

    '''Representa um vetor tridimensional.

    Objetos do tipo `Vec3()` são imutáveis. Algumas implementações podem
    proteger explicitamente os atributos do vetor, enquanto outras não. É
    responsabilidade do usuário não tentar nenhum tipo de manipulação direta
    das coordenadas x, y e z do vetor.

    Exemplo
    -------

    Criamos um vetor chamando a classe com as componentes como argumento.

    >>> v = Vec3(2, 3, 4); print(v)
    Vec3(2, 3, 4)

    Os métodos de listas funcionam para objetos do tipo Vec3:

    >>> v[0], v[1], v[2], len(v)
    (2.0, 3.0, 4.0, 3)

    Objetos do tipo Vec3 também aceitam operações matemáticas

    >>> v + 2 * v
    Vec3(6, 9, 12)

    Além de algumas funções de conveniência para calcular o módulo,
    vetor unitário, etc.
    >>> v.norm()
    5.385164807134504

    >>> v.normalize()
    Vec3(0.371390676354, 0.557086014531, 0.742781352708)

    '''

    if not C.compiled:
        __slots__ = ['x', 'y', 'z']
    else:
        __slots__ = []

    def __init__(self, x_or_data, y=None, z=None):
        if y is None:
            x, y, z = x_or_data
        else:
            x = x_or_data
        self.x = x + 0.0
        self.y = y + 0.0
        self.z = z + 0.0

    @classmethod
    def from_seq(cls, data):
        '''Inicializa vetor a partir de uma sequência com as coordenadas x e
        y'''

        if data.__class__ is Vec3:
            return data
        x, y, z = data
        return cls.from_coords(x, y, z)

    @staticmethod
    @C.locals(x='double', y='double', z='double', new='double')
    def from_coords(x, y, z):
        '''Inicializa vetor a partir das coordenadas'''

        # Um pouco mais rápido que chamar Vec3(x, y, z) diretamente.
        # Evita um pouco da lógica dentro do método __init__
        new = Vec3.__new__(Vec3, x, y, z)
        new.x = x
        new.y = y
        new.z = z
        return new

    @C.locals(x='double', y='double', z='double', new='Vec3')
    def _from_coords(self, x, y, z):
        new = Vec3.__new__(Vec3, x, y, z)
        new.x = x
        new.y = y
        new.z = z
        return new

    def as_tuple(self):
        '''Retorna a representação do vetor como uma tupla'''

        return (self.x, self.y, self.z)

    def almost_equals(self , other, delta = 0.0001):
        '''Verifica se o vetor é quase igual a outro

        Exemplo:
        ---------
        >>> v1 = Vec3(2,3,4)
        >>> v2 = Vec3(2.1, 2.9, 4.12)
        >>> other = Vec3(2.0000001, 3.0000001, 4.000001)
        >>> v1.almost_equals(other)
        True
        >>> v2.almost_equals(other)
        False
        '''

        # Faz o teste primeiramente com o angulo entre os dois vetores
        if abs(self.x - other.x) <= delta and abs(self.y - other.y) <= delta and abs(self.z - other.z) <= delta:
            return True
        else:
            return False

    def distance_to(self, other):
        '''Retorna a distância entre dois vetores

        Exemplo
        --------
        >>> v = Vec3(0, 0, 5)
        >>> other = Vec3(0, 0, 4)
        >>> v.distance_to(other)
        1.0
        '''

        distance = m.sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2 + (other.z - self.z) ** 2)

        return distance

    def angle(self, other):
        '''Retorna o ângulo entre dois vetores em radianos

        Exemplo
        --------
        >>> v = Vec3(5, 0, 0)
        >>> other = Vec3(0, 5, 0)
        >>> v.angle(other)
        1.5707963267948966
        '''
        return m.acos((self.dot(other))/(self.norm()*other.norm()))

    def is_null(self):
        '''Verifica se o vetor é nulo

        Exemplo
        --------
        >>> v = Vec3(0,0,0)
        >>> v.is_null()
        True
        '''

        if self == Vec3(0,0,0):
            return True
        else:
            return False

    def cylindrical_coords(self):
        '''Retorna as coordenadas cilindricas desse vetor como uma tupla

        Exemplo
        --------
        >>> v = Vec3(2,3,4)
        >>> v.cylindrical_coords()
        (3.605551275463989, 0.982793723247329, 4.0)
        '''
        radius = m.sqrt(self.x**2 + self.y**2)
        angle = m.atan(self.y/self.x)
        height = self.z

        return (radius, angle, height)

    def spherical_cords(self):
        '''Retorna as coordenadas esféricas desse vetor como uma tupla

        Exemplo
        --------
        >>> v = Vec3(2,3,4)
        >>> v.spherical_cords()
        (5.385164807134504, 0.7335813236400831, 0.982793723247329)
        '''
        radius = self.norm()
        theta = m.acos(self.z / radius)
        phi = m.atan(self.y/ self.x)

        sph = (radius, theta, phi)

        return sph

    def reflect(self, other):
        '''Retorna o vetor refletido por outro vetor
        Exemplo
        --------
        >>> v = Vec3(1,2,3)
        >>> other = Vec3(1,0,0)
        >>> v.reflect(other)
        Vec3(1, -2, -3)
        '''

        reflection = 2 * (self.dot(other)) * other - self
        return reflection

    def lerp(self, other , range_lerp):
        '''Retorna um vetor com tamanho máximo baseado no vetor resultante da
        diferença entre dois vetores, sendo que o range_lerp assume valores
        entre 0 e 1.

        Exemplo
        --------
        >>> v = Vec3(1,0,0)
        >>> v1 = Vec3(0,1,0)
        >>> v.lerp(v1, 0)
        Vec3(1, 0, 0)
        '''

        if range_lerp > 1 or range_lerp < 0:

            lerp = self
        else:
            subtraction_vectors = other - self

            lerp = subtraction_vectors * range_lerp + self

        return lerp

    def project(self, other):
        '''Retorna um vetor que é a projeção do mesmo na direção do segundo vetor

        Exemplo
        --------
        >>> v = Vec3(3, 5, 6)
        >>> other = Vec3(10, 0, 0)
        >>> v.project(other)
        Vec3(3, 0, 0)
        '''

        return (self.dot(other) / other.norm_sqr()) * other

    def clamp(self, minimum, maximum):
        '''Retorna um vetor na mesma direção com o módulo baseado entre os valores
        minimo e máximo.Se for menor que o máximo, retorna um vetor com módulo igual ao
        mínimo , se for maior que o máximo, retorna um vetor com módulo igual ao
        máximo.

        Exemplo
        --------
        >>> v = Vec3(2, 4, 5)
        >>> v.clamp(8, 10)
        Vec3(2.38513918, 4.77027835, 5.96284794)
        '''

        if self.norm() < maximum:
            distance_min_max = minimum/self.norm()
        else:
            distance_min_max = maximum/self.norm()

        self = self * distance_min_max
        self.x = round(self.x, 8)
        self.y = round(self.y, 8)
        self.z = round(self.z, 8)

        return self

    def norm(self):
        '''Retorna o módulo (norma) do vetor'''

        return m.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)


    def norm_sqr(self):
        '''Retorna o módulo do vetor ao quadrado'''

        return self.x ** 2 + self.y ** 2 + self.z ** 2

    def normalize(self):
        '''Retorna um vetor unitário'''

        norm = self.norm()
        return (self._from_coords(self.x / norm, self.y / norm, self.z / norm)
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

        return self._from_coords(x - self.x, self.y, self.z)

    @C.locals(y='double')
    def flip_y(self, y=0.0):
        '''Retorna uma cópia com a coordenada y espelhada em torno do ponto
        dado'''

        return self._from_coords(self.x, y - self.y, self.z)

    @C.locals(z='double')
    def flip_z(self, z=0.0):
        '''Retorna uma cópia com a coordenada z espelhada em torno do ponto
        dado'''

        return self._from_coords(self.x, self.y, z - self.z)

    @C.locals(height='int')
    def screen_coords(self, height=600):
        '''Converte o vetor para um sistema de coordenadas onde o eixo y aponta
        para baixo a partir do topo da tela. É necessário especificar a altura
        da tela para realizar a conversão. Retorna uma tupla com os valores
        truncados.'''

        return m.trunc(self.x), height - m.trunc(self.y)

    def trunc(self):
        '''Retorna uma tupla com os valores das coordenadas x, y e z truncados'''

        return m.trunc(self.x), m.trunc(self.y), m.trunc(self.z)

    @C.locals(vec='Vec3', x='double', y='double', z = 'double')
    def dot(self, other):
        '''Retorna o resultado do produto escalar com outro vetor

        Exemplo
        -------
        >>> Vec3(1, 2, 3).dot(Vec3(6, 7, 8))
        44.0
        '''

        try:
            vec = other
            return vec.x * self.x + vec.y * self.y + vec.z * self.z
        except (TypeError, AttributeError):
            x, y, z = other
            return self.x * x + self.y * y + self.z * z

    @C.locals(vec='Vec3', x='double', y='double', z='double', a='double', b='double', c='double')
    def cross(self, other):
        '''Retorna o produto vetorial de dois vetores 3D como um terceiro vetor

        Exemplo
        -------

        >>> Vec3(1, 2, 3).cross(Vec3(-1, 1, 2))
        Vec3(1, -5, 3)
        '''

        try:
            vec = other
            a = (self.y * vec.z) - (self.z * vec.y);
            b = -(self.x * vec.z) + (self.z * vec.x);
            c = (self.x * vec.y) - (self.y * vec.x);
            return Vec3(a, b, c)
        except (TypeError, AttributeError):
            x, y, z = other
            a = (self.y * z) - (self.z * y);
            b = -(self.x * z) + (self.z * x);
            c = (self.x * y) - (self.y * x);
            return Vec3(a, b, c)

    def null(self):
        '''Retorna o vetor nulo'''

        return nullvec3

    # Métodos mágicos #########################################################
    def __repr__(self):
        '''x.__repr__() <==> repr(x)'''

        x, y, z = self
        x = str(x) if x != int(x) else str(int(x))
        y = str(y) if y != int(y) else str(int(y))
        z = str(z) if z != int(z) else str(int(z))
        tname = type(self).__name__
        return '%s(%s, %s, %s)' % (tname, x, y, z)

    def __str__(self):
        '''x.__str__() <==> str(x)'''

        return repr(self)

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

    def __hash__(self):
        return hash(self.x) ^ hash(self.y) ^ hash(self.z)

    # Operações aritiméticas ##################################################
    @C.locals(A='Vec3', B='double')
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

        return A._from_coords(A.x * B, A.y * B, A.z * B)

    def __rmul__(self, other):
        '''x.__rmul__(y) <==> y * x'''

        return self * other

    @C.locals(self='Vec3', other='double')
    def __div__(self, other):
        '''x.__div__(y) <==> x / y'''

        return self._from_coords(self.x / other, self.y / other, self.z / other)

    @C.locals(self='Vec3', other='double')
    def __truediv__(self, other):
        '''x.__div__(y) <==> x / y'''

        return self._from_coords(self.x / other, self.y / other, self.z / other)

    @C.locals(A='Vec3', B='Vec3', x='double', y='double', z='double')
    def __add__(self, other):
        '''x.__add__(y) <==> x + y'''

        try:
            A = self
            B = other
            return A._from_coords(A.x + B.x, A.y + B.y, A.z + B.z)
        except (TypeError, AttributeError):
            try:
                A = self
                x, y, z = other
            except TypeError:
                A = other
                x, y, z = self
            return A._from_coords(A.x + x, A.y + y, A.z + z)

    def __radd__(self, other):
        '''x.__radd__(y) <==> y + x'''

        return self + other

    @C.locals(A='Vec3', B='Vec3', x='double', y='double', z='double')
    def __sub__(self, other):
        '''x.__sub__(y) <==> x - y'''

        try:
            A = self
            B = other
            return A._from_coords(A.x - B.x, A.y - B.y, A.z - B.z)
        except (TypeError, AttributeError):
            try:
                A = self
                x, y = other
                return A._from_coords(A.x - x, A.y - y, A.z - z)
            except TypeError:
                B = other
                x, y = self
                return B._from_coords(x - B.x, y - B.y, z - B.z)

    def __rsub__(self, other):
        '''x.__rsub__(y) <==> y - x'''
        try:
            return self._from_coords(other.x - self.x, other.y - self.y, other.z - self.z)
        except AttributeError:
            x, y, z = other
            return self._from_coords(x - self.x, y - self.y, z - self.z)

    def __neg__(self):
        '''x.__neg() <==> -x'''

        return self._from_coords(-self.x, -self.y, -self.z)

    def __nonzero__(self):
        if (self.x == 0) and (self.y == 0) and (self.z == 0):
            return False
        else:
            return True

    def __abs__(self):
        return self.norm()

    @C.locals(method='int', x='double', y='double', z='double')
    def __richcmp__(self, other, method):
        if method == 2:    # igual (==)
            x, y, z = other
            return self.x == x and self.y == y and self.z == z
        elif method == 3:  # diferente (!=)
            x, y, z = other
            return self.x != x or self.y != y or self.z!= z
        else:
            raise TypeError('invalid rich comparison: %s' % method)

    # Ganchos para implementações mutáveis ####################################
    def _setx(self, x):
        self.x = x

    def _sety(self, y):
        self.y = y

    def _setz(self, z):
        self.z = z

    def _setxyz(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def _setitem(self, i, value):
        if i == 0:
            self.x = value + 0.0
        elif i == 1:
            self.y = value + 0.0
        elif i == 2:
            self.z = value + 0.0
        else:
            raise IndexError

    @C.locals(x='double', y='double', z='double', vec='Vec3')
    def _iadd(self, other):
        '''x.__iadd__(y) <==> x += y'''

        try:
            vec = other
            self.x += vec.x
            self.y += vec.y
            self.z += vec.z
        except TypeError:
            x, y, z = other
            self.x += x
            self.y += y
            self.z += z
        return self

    @C.locals(x='double', y='double', z='double', vec='Vec3')
    def _isub(self, other):
        '''x.__isub__(y) <==> x -= y'''

        try:
            vec = other
            self.x -= vec.x
            self.y -= vec.y
            self.z -= vec.z
        except TypeError:
            x, y, z = other
            self.x -= x
            self.y -= y
            self.z -= z
        return self

    @C.locals(other='double')
    def _imul(self, other):
        '''x.__imul__(y) <==> x *= y'''

        self.x *= other
        self.y *= other
        self.z *= other
        return self

    @C.locals(other='double')
    def _idiv(self, other):
        '''x.__idiv__(y) <==> x /= y'''

        self.x /= other
        self.y /= other
        self.z /= other
        return self

    @C.locals(other='double')
    def _itruediv(self, other):
        '''x.__idiv__(y) <==> x /= y'''

        self.x /= other
        self.y /= other
        self.z /= other
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

    def _update(self, other, y=None, z=None):
        '''Copia as coordenadas x, y do objeto other'''

        if y is None:
            x, y, z = other
        else:
            x = other
        self.x = x + 0.0
        self.y = y + 0.0
        self.z = z + 0.0

    def _copy(self):
        '''Retorna uma cópia de si mesmo'''

        return self._from_coords(self.x, self.y, self.z)

    __dict__ = {}

nullvec3 = Vec3(0, 0, 0)

###############################################################################
#               Código injetado para rodar no modo interpretado
###############################################################################

if not C.compiled:
    @pyinject(globals())
    class Vec3Inject:

        '''Implementa métodos que tem algum tipo de problema de performance
        ou de semântica diferente entre Cython e o Python interpretado'''

        def __init__(self, x_or_data, y=None, z = None):
            if y is None:
                x, y, z = x_or_data
            else:
                x = x_or_data
            self.x = x + 0.0
            self.y = y + 0.0
            self.z = z + 0.0

        @staticmethod
        def _from_coords(x, y, z):
            tt = Vec3
            new = tt.__new__(tt, x, y, z)
            new.x = x + 0.0
            new.y = y + 0.0
            new.z = z + 0.0
            return new

        def __mul__(self, other):
            '''x.__mul__(y) <==> x * y'''

            try:
                other = float(other)
            except TypeError:
                return other.__rmul__(self)
            return self._from_coords(self.x * other, self.y * other, self.z * other)

        def __eq__(self, other):
            x, y, z = other
            return self.x == x and self.y == y and self.z == z

    auto_public(Vec3)

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
        if not isinstance(value, Vec3):
            value = Vec3.from_seq(value)
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
