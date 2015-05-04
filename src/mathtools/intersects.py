# -*- coding: utf8 -*-

'''
Encontra os pontos de intersecção entre dois objetos.
'''

from FGAme.util import multifunction, DispatchError
from mathtools import Vec2


class IntersectError(ValueError):
    pass


@multifunction(None, None)
def intersection(A, B, tol=1e-6):
    '''Retorna uma lista com todos os pontos de interseção entre os objetos
    A e B'''

    try:
        reverse_f = intersection.getfunction(type(B), type(A))

        def r_intersection(A, B):
            return reverse_f(B, A)

        intersection[type(B), type(A)] = r_intersection
        return r_intersection(A, B)

    except DispatchError:
        tA = type(A).__name__
        tB = type(B).__name__
        raise ValueError('don\'t know how to intercept %s and %s' % (tA, tB))


@multifunction((Vec2, tuple), (Vec2, tuple))
def intersection_vector_vector(u, v, tol=1e-6):

    if (u - v).norm() < tol:
        return [(u + v) / 2]
    else:
        return []

if __name__ == '__main__':
    import doctest
    doctest.testmod()