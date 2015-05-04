# -*- coding: utf8 -*-
import cython
from mathtools import Mat2, Vec2


def sign(x):
    '''Retorna -1 para um numero negativo e 1 para um número positivo'''

    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0


def shadow_x(A, B):
    '''Retorna o tamanho da sombra comum entre os objetos A e B no eixo x.
    Caso não haja superposição, retorna um valor negativo que corresponde ao
    tamanho do buraco'''

    return min(A.xmax, B.xmax) - max(A.xmin, B.xmin)


def shadow_y(A, B):
    '''Retorna o tamanho da sombra comum entre os objetos A e B no eixo y.
    Caso não haja superposição, retorna um valor negativo que corresponde ao
    tamanho do buraco'''

    return min(A.ymax, B.ymax) - max(A.ymin, B.ymin)


def asvector(v):
    '''Retorna o objeto como uma instância da classe Vetor'''

    if isinstance(v, Vec2):
        return v
    else:
        return Vec2.from_seq(v)


@cython.locals(A='Vec2', B='mVec2')
def dot(v1, v2):
    '''Calcula o produto escalar entre dois vetores

    Exemplo
    -------

    >>> dot((1, 2), (3, 4))
    11

    >>> dot(Vec2(1, 2), Vec2(3, 4))
    11.0
    '''

    try:
        A = v1
        B = v2
        return A._x * B._x + A._y * B._y
    except (AttributeError, TypeError):
        return sum(x * y for (x, y) in zip(v1, v2))


@cython.locals(A='Vec2', B='mVec2',
               x1='double', x2='double', y1='double', y2='double')
def cross(v1, v2):
    '''Retorna a compontente z do produto vetorial de dois vetores
    bidimensionais'''

    try:
        A = v1
        B = v2
        x1 = A._x
        y1 = A._y
        x2 = B._x
        y2 = B._x
    except (AttributeError, TypeError):
        x1, y1 = v1
        x2, y2 = v2
    return x1 * y2 - x2 * y1


def asmatrix(m):
    '''Retorna o objeto como uma instância da classe Vetor'''

    if isinstance(m, Mat2):
        return m
    else:
        return Mat2(m)


def diag(a, b):
    '''Retorna uma matrix com os valores de a e b na diagonal principal'''

    return Mat2([[a, 0], [0, b]])

if __name__ == '__main__':
    import doctest
    doctest.testmod()
