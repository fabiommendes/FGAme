# -*- coding: utf8 -*-

from mathtools import Vec2, dot
from math import sqrt, sin, cos

SQRT_2 = sqrt(2)
number = (float, int)

__all__ = ['Matrix', 'RotMatrix', 'asmatrix']


class Matrix(object):

    '''Implementa uma matriz bidimensional e operações básicas de álgebra
    linear

    Example
    -------

    Criamos uma matriz a partir de uma lista de listas

    >>> M = Matrix([[1, 2],
    ...             [3, 4]])

    Podemos também utilizar classes especializadas, como por exemplo
    a `RotMatrix`, que cria uma matriz de rotação

    >>> R = RotMatrix(3.1415); R
    |-1  -0|
    | 0  -1|

    Os objetos da classe Matrix implementam as operações algébricas básicas

    >>> M + 2 * R
    |-1  2|
    | 3  2|

    As multiplicações são como definidas em ágebra linear

    >>> M * M
    | 7  10|
    |15  22|

    Onde multiplicação por vetores também é aceita

    >>> v = Vec2(2, 3)
    >>> M * v
    Vec2(8, 18)

    Note que não existem classes especializadas para vetores linha ou coluna.
    Deste modo, sempre assumimos o formato que permite realizar a
    multiplicação.

    >>> v * M   # agora v é tratado como um vetor linha
    Vec2(11, 16)

    Além disto, temos operações como cálculo da inversa, autovalores,
    determinante, etc

    >>> M.inv() * M
    |1  0|
    |0  1|

    >>> diag(1, 1).eigval()
    (1.0, 1.0)
    '''

    __slots__ = ['_data']
    _restype = None  # late binding ==> _restype == Matrix

    def __init__(self, obj):
        c1, c2 = obj
        a, b = c1
        c, d = c2
        self._data = (float(a), float(b), float(c), float(d))

    @classmethod
    def _from_lists_(cls, M):
        '''Inicia a matriz a partir de uma lista de linhas. Corresponde ao
        método de inicialização padrão, mas pode ser invocado por subclasses
        caso a assinatura do construtor padrão seja diferente'''

        new = object.__new__(cls._restype)
        Matrix.__init__(new, M)
        return new

    @classmethod
    def from_flat(cls, data):
        '''Constroi matriz a partir de dados linearizados'''

        return cls.from_flat(data, restype=cls)

    @classmethod
    def _from_flat(cls, data, restype=None):
        new = object.__new__(restype or cls._restype)
        new._data = tuple(data)
        if len(new._data) != 4:
            raise ValueError('must have 4 components')
        return new

    # Métodos de apresentação da informação na matriz #########################

    def aslist(self):
        '''Retorna a matrix como uma lista de listas'''

        a, b, c, d = self.flat()
        return [[a, b], [c, d]]

    def flat(self):
        '''Itera sobre todos elementos da matriz, primeiro os elementos da
        primeira linha e depois da segunda'''

        return iter(self._data)

    def colvecs(self):
        '''Retorna uma lista com os vetores coluna da matriz.'''

        a, b, c, d = self._data
        return [Vec2(a, c), Vec2(b, d)]

    def rowvecs(self):
        '''Retorna uma lista com os vetores linha. Este método existe por
        simetria a `M.colvecs()`. Mesma coisa que list(M).'''

        a, b, c, d = self.flat()
        return [Vec2(a, b), Vec2(c, d)]

    # Métodos para cálculo de propriedades lineares da matriz #################
    def det(self):
        '''Retorna o determinante da matriz'''

        a, b, c, d = self.flat()
        return a * d - b * c

    def trace(self):
        '''Retorna o traço da matriz'''

        return self[0, 0] + self[1, 1]

    def diag(self):
        '''Retorna uma lista com os valores na diagonal principal da matriz'''

        return [self[0, 0], self[1, 1]]

    def eig(self):
        '''Retorna uma tupla com a lista de autovalores e a matriz dos
        autovetores

        Example
        -------

        Criamos uma matriz e aplicamos eig()

        >>> M = Matrix([[1,2], [3,4]])
        >>> vals, vecs = M.eig()

        Agora extraimos os auto-vetores coluna

        >>> v1, v2 = vecs.colvecs()

        Finalmente, multiplicamos M por v1: o resultado deve ser igual que
        multiplicar o autovetor pelo autovalor correspondente

        >>> M * v1, vals[0] * v1                           # doctest: +ELLIPSIS
        (Vec2(2.23..., 4.88...), Vec2(2.23..., 4.88...))
        '''

        v1, v2 = self.eigvec()
        a, c = v1
        b, d = v2
        return (self.eigval(), self._from_lists_([[a, b], [c, d]]))

    def eigval(self):
        '''Retorna uma tupla com os autovalores da matriz'''

        a, b, c, d = self.flat()
        l1 = (d + a + sqrt(d * d - 2 * a * d + a * a + 4 * c * b)) / 2
        l2 = (d + a - sqrt(d * d - 2 * a * d + a * a + 4 * c * b)) / 2
        return (l1, l2)

    def eigvec(self, transpose=False):
        '''Retorna uma lista com os autovetores normalizados da matriz.

        A ordem dos autovetores corresponde àquela retornada pelo método
        `M.eigval()`'''

        a, b = self._data[0:2]
        l1, l2 = self.eigval()
        try:
            v1 = Vec2(b / (l1 - a), 1)
        except ZeroDivisionError:
            v1 = Vec2(1, 0)
        try:
            v2 = Vec2(b / (l2 - a), 1)
        except ZeroDivisionError:
            v2 = Vec2(1, 0)

        return v1.normalize(), v2.normalize()

    # Métodos que retornam versões transformadas ##############################
    def transposed(self):
        '''Retorna a transposta da matriz'''

        a, b, c, d = self.flat()
        M = [[a, c],
             [b, d]]
        return self._from_lists_(M)

    def rotate(self, theta):
        '''Retorna uma matriz rotacionada por um ângulo theta'''

        R = RotMatrix(theta)
        return R * self * R.transposed()

    def inv(self):
        '''Retorna a inversa da matriz'''

        det = self.det()
        a, b, c, d = self.flat()
        M = [[d / det, -b / det],
             [-c / det, a / det]]
        return self._from_lists_(M)

    # Sobrescrita de operadores ###############################################
    def _fmt_number(self, x):
        '''Função auxiliar para __repr__: formata número para impressão'''

        return ('%.3f' % x).rstrip('0').rstrip('.')

    def __repr__(self):
        '''x.__repr__() <==> repr(x)'''

        l1, l2 = self.rowvecs()
        a, b = l1
        c, d = l2
        a, b, c, d = map(self._fmt_number, [a, b, c, d])
        n = max(len(a), len(c))
        m = max(len(b), len(d))
        l1 = '|%s  %s|' % (a.rjust(n), b.rjust(m))
        l2 = '|%s  %s|' % (c.rjust(n), d.rjust(m))
        return '%s\n%s' % (l1, l2)

    def __str__(self):
        '''x.__str__() <==> str(x)'''
        return repr(self)

    def __len__(self):
        return 2

    def __iter__(self):
        it = self.flat()
        yield Vec2(next(it), next(it))
        yield Vec2(next(it), next(it))

    def __getitem__(self, idx):
        '''x.__getitem__(i) <==> x[i]'''

        if isinstance(idx, tuple):
            i, j = idx
            return self._data[i][j]

        elif isinstance(idx, int):
            return Vec2(*self._data[idx])

    # Operações matemáticas ###################################################
    def __mul__(self, other):
        '''x.__mul__(y) <==> x * y'''

        if isinstance(other, Matrix):
            u, v = other.colvecs()
            U, V = self.rowvecs()
            M = [[dot(U, u), dot(U, v)],
                 [dot(V, u), dot(V, v)]]
            return self._from_lists_(M)

        elif isinstance(other, (Vec2, tuple, list)):
            u, v = self.rowvecs()
            return Vec2(dot(u, other), dot(v, other))

        elif isinstance(other, number):
            return self._from_flat(x * other for x in self.flat())

        else:
            u, v = self.rowvecs()
            return Vec2(dot(u, other), dot(v, other))

    def __rmul__(self, other):
        '''x.__rmul__(y) <==> y * x'''

        if isinstance(other, number):
            return self._from_flat(x * other for x in self.flat())
        else:
            u, v = self.colvecs()
            return Vec2(dot(u, other), dot(v, other))

    def __div__(self, other):
        '''x.__div__(y) <==> x / y'''

        return self._from_flat(x / other for x in self.flat())

    def __floordiv__(self, other):
        return self._from_flat(x // other for x in self.flat())

    __truediv__ = __div__  # Python 2

    def __add__(self, other):
        '''x.__add__(y) <==> x + y'''

        return self._from_flat(x + y for (x, y) in
                               zip(self.flat(), other.flat()))

    def __radd__(self, other):
        '''x.__radd__(y) <==> y + x'''

        return self + other

    def __sub__(self, other):
        '''x.__sub__(y) <==> x - y'''

        return self._from_flat(x - y for (x, y) in
                               zip(self.flat(), other.flat()))

    def __rsub__(self, other):
        '''x.__rsub__(y) <==> y - x'''

        return self._from_flat(y - x for (x, y) in
                               zip(self.flat(), other.flat()))

    def __neg__(self):
        '''x.__neg() <==> -x'''

        return self._from_flat(-x for x in self.flat())

    def __nonzero__(self):
        return any(self.flat())

Matrix._restype = Matrix


class RotMatrix(Matrix):

    '''Cria uma matriz de rotação que realiza a rotação pelo ângulo theta
    especificado'''

    __slots__ = ['_theta', '_transposed']

    def __init__(self, theta):
        self._theta = float(theta)
        self._transposed = None

        C = cos(theta)
        S = sin(theta)
        M = [[C, -S], [S, C]]
        super(RotMatrix, self).__init__(M)

    def rotate(self, theta):
        return RotMatrix(self.theta + theta)

    def transposed(self):
        if self._transposed is None:
            self._transposed = super(RotMatrix, self).transposed()
        return self._transposed

    def inv(self):
        return self.transposed()

    @property
    def theta(self):
        return self.theta


class mMatrix(Matrix):

    '''Versão mutável de Matrix'''

    __slots__ = ['_data']

    def __init__(self, data):
        super(mMatrix, self).__init__(data)
        self._data = list(data)

    def __setattr__(self, idx, value):
        i, j = idx
        self._data[i][j] = value

    def irotate(self, theta):
        '''Rotaciona a matriz *inplace*'''

        R = RotMatrix(theta)
        self._data = (R * self * R.transposed())._data

    def transpose(self):
        '''Transpõe a matriz *inplace*'''

        self[1, 0], self[0, 1] = self[0, 1], self[1, 0]


def asmatrix(m):
    '''Retorna o objeto como uma instância da classe Vetor'''

    if isinstance(m, Matrix):
        return m
    else:
        return Matrix(m)


def diag(a, b):
    '''Retorna uma matrix com os valores de a e b na diagonal principal'''

    return Matrix([[a, 0], [0, b]])


if __name__ == '__main__':
    import doctest
    doctest.testmod()
