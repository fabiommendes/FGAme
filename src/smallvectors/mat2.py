# -*- coding: utf8 -*-

import math as m
from mathtools.base import auto_public
from mathtools.util import pyinject
from smallvectors.vec2 import Vec2

__all__ = ['Mat2', 'RotMat2', 'mMat2']
number = (float, int)


###############################################################################
#                            Matriz 2 x 2
###############################################################################
class Mat2(object):

    '''Implementa uma matriz bidimensional e operações básicas de álgebra
    linear

    Example
    -------

    Criamos uma matriz a partir de uma lista de listas

    >>> M = Mat2([[1, 2],
    ...             [3, 4]])

    Podemos também utilizar classes especializadas, como por exemplo
    a `RotMat2`, que cria uma matriz de rotação

    >>> R = RotMat2(3.1415); R
    |-1  -0|
    | 0  -1|

    Os objetos da classe Mat2 implementam as operações algébricas básicas

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

    >>> (M * M.inv()).eigval()
    (1.0, 1.0)
    '''

    __slots__ = ['_a', '_b', '_c', '_d']

    def __init__(self, obj):
        c1, c2 = obj
        a, b = c1
        c, d = c2
        self._a = a + 0.0
        self._b = b + 0.0
        self._c = c + 0.0
        self._d = d + 0.0

    @classmethod
    def _from_lists_(cls, M):
        '''Inicia a matriz a partir de uma lista de linhas. Corresponde ao
        método de inicialização padrão, mas pode ser invocado por subclasses
        caso a assinatura do construtor padrão seja diferente'''

        new = object.__new__(cls)
        Mat2.__init__(new, M)
        return new

    @classmethod
    def from_flat(cls, data):
        '''Constroi matriz a partir de dados linearizados'''

        return cls.from_flat(data, restype=cls)

    @classmethod
    def _from_flat(cls, data, restype=None):
        it = iter(data)
        new = object.__new__(restype or cls)
        new._a = next(it) + 0.0
        new._b = next(it) + 0.0
        new._c = next(it) + 0.0
        new._d = next(it) + 0.0
        return new

    # Métodos de apresentação da informação na matriz #########################

    def aslist(self):
        '''Retorna a matrix como uma lista de listas'''

        a, b, c, d = self.flat()
        return [[a, b], [c, d]]

    def flat(self):
        '''Itera sobre todos elementos da matriz, primeiro os elementos da
        primeira linha e depois da segunda'''

        yield self._a
        yield self._b
        yield self._c
        yield self._d

    def colvecs(self):
        '''Retorna uma lista com os vetores coluna da matriz.'''

        return [Vec2(self._a, self._c), Vec2(self._b, self._d)]

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

        >>> M = Mat2([[1,2], [3,4]])
        >>> vals, vecs = M.eig()

        Agora extraimos os auto-vetores coluna

        >>> v1, v2 = vecs.colvecs()

        Finalmente, multiplicamos M por v1: o resultado deve ser igual que
        multiplicar o autovetor pelo autovalor correspondente

        >>> M * v1, vals[0] * v1
        (Vec2(2.2, 4.9), Vec2(2.2, 4.9))
        '''

        v1, v2 = self.eigvec()
        a, c = v1
        b, d = v2
        return (self.eigval(), self._from_lists_([[a, b], [c, d]]))

    def eigval(self):
        '''Retorna uma tupla com os autovalores da matriz'''

        a, b, c, d = self.flat()
        l1 = (d + a + m.sqrt(d * d - 2 * a * d + a * a + 4 * c * b)) / 2
        l2 = (d + a - m.sqrt(d * d - 2 * a * d + a * a + 4 * c * b)) / 2
        return (l1, l2)

    def eigvec(self, transpose=False):
        '''Retorna uma lista com os autovetores normalizados da matriz.

        A ordem dos autovetores corresponde àquela retornada pelo método
        `M.eigval()`'''

        a, b = self._a, self._b
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
    def transpose(self):
        '''Retorna a transposta da matriz'''

        a, b, c, d = self.flat()
        M = [[a, c],
             [b, d]]
        return self._from_lists_(M)

    def rotate(self, theta):
        '''Retorna uma matriz rotacionada por um ângulo theta'''

        R = RotMat2(theta)
        return R * self * R.transpose()

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

        if isinstance(other, Mat2):
            u, v = other.colvecs()
            U, V = self.rowvecs()
            M = [[U.dot(u), U.dot(v)],
                 [V.dot(u), V.dot(v)]]
            return self._from_lists_(M)

        elif isinstance(other, number):
            return self._from_flat(x * other for x in self.flat())

        else:
            x, y = other
            return Vec2(self._a * x + self._b * y,
                        self._c * x + self._d * y)

    def __rmul__(self, other):
        '''x.__rmul__(y) <==> y * x'''

        if isinstance(other, number):
            return self._from_flat(x * other for x in self.flat())
        else:
            x, y = other
            return Vec2(self._a * x + self._c * y,
                        self._b * x + self._d * y)

    def __div__(self, other):
        '''x.__div__(y) <==> x / y'''

        return self._from_flat(x / other for x in self.flat())

    def __truediv__(self, other):
        '''x.__div__(y) <==> x / y'''

        return self._from_flat(x / other for x in self.flat())

    def __floordiv__(self, other):
        return self._from_flat(x // other for x in self.flat())

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


###############################################################################
#                            Matriz de rotação
###############################################################################
class RotMat2(Mat2):

    '''Cria uma matriz de rotação que realiza a rotação pelo ângulo theta
    especificado'''

    __slots__ = ['_theta', '_transposed']

    def __init__(self, theta):
        self._theta = float(theta)
        self._transposed = None

        C = m.cos(theta)
        S = m.sin(theta)
        M = [[C, -S], [S, C]]
        super(RotMat2, self).__init__(M)

    def rotate(self, theta):
        return RotMat2(self.theta + theta)

    def transpose(self):
        if self._transposed is None:
            self._transposed = super(RotMat2, self).transpose()
        return self._transposed

    def inv(self):
        return self.transpose()

    @property
    def theta(self):
        return self.theta


###############################################################################
#                            Matriz mutável
###############################################################################
class mMat2(Mat2):

    '''Versão mutável de Mat2'''

    __slots__ = ['_data']

    def __init__(self, data):
        super(mMat2, self).__init__(data)
        self._data = list(data)

    def __setattr__(self, idx, value):
        i, j = idx
        self._data[i][j] = value

    def irotate(self, theta):
        '''Rotaciona a matriz *inplace*'''

        R = RotMat2(theta)
        self._data = (R * self * R.transpose())._data

    def itranspose(self):
        '''Transpõe a matriz *inplace*'''

        self[1, 0], self[0, 1] = self[0, 1], self[1, 0]

###############################################################################
#               Código injetado para rodar no modo interpretado
###############################################################################

if __name__ == '__main__' and not C.compiled:
    import doctest
    doctest.testmod()
