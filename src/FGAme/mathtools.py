#-*- coding: utf8 -*-
'''
Importa as funções matemáticas do módulo mathutils.
'''

from math import *
from smallvectors import *
import smallvectors as linalg
from smallshapes import *
import smallshapes as shapes
from generic import set_promotion_rule, set_conversion

#
# Apelidos para tipos vetoriais
#
Point2 = Point[2, float]
Point3 = Point[3, float]
Point4 = Point[4, float]


class FGAmeVec(object):
    '''A FGAme vector object'''

    def __repr__(self):
        data = ['%.1f' % x for x in self]
        if all(x.endswith('.0') for x in data):
            data = [x[:-2] for x in data]
        return 'Vec(%s)' % (', '.join(data))

    def __radd__(self, other):
        return type(self)(*(y + x for (x, y) in zip(self, other)))

    def __rsub__(self, other):
        return type(self)(*(y - x for (x, y) in zip(self, other)))

    def __rmul__(self, other):
        return type(self)(*(x * other for x in self))

    def __mul__(self, other):
        return type(self)(*(x * other for x in self))

    def __rtruediv__(self, other):
        return type(self)(*(x / other for x in self))


class Vec2(FGAmeVec, Vec[2, float]):
    '''Vetor bidimensional'''


@set_conversion(list, Vec2)
@set_conversion(tuple, Vec2)
def _tuple2vec2(u):
    x, y = u
    return Vec2(x, y)


set_promotion_rule(Vec2, tuple, Vec2)
set_promotion_rule(Vec2, list, Vec2)


@add.overload([Vec2, tuple])
@add.overload([Vec2, list])
@add.overload([tuple, Vec2])
@add.overload([list, Vec2])
def add(u, v):
    x, y = u
    a, b = v
    return Vec2(x + a, y + b)


@sub.overload([Vec2, tuple])
@sub.overload([Vec2, list])
@sub.overload([tuple, Vec2])
@sub.overload([list, Vec2])
def sub(u, v):
    x, y = u
    a, b = v
    return Vec2(x - a, y - b)


Vec3 = Vec[3, float]
Vec4 = Vec[4, float]
Direction2 = Direction[2, float]
Direction3 = Direction[3, float]
Direction4 = Direction[4, float]

#
# Direções unitárias e vetores nulos
#
ux2D = Direction2(1, 0)
uy2D = Direction2(0, 1)
ux3D = Direction3(1, 0, 0)
uy3D = Direction3(0, 1, 0)
uz3D = Direction3(0, 0, 1)
ux4D = Direction4(1, 0, 0, 0)
uy4D = Direction4(0, 1, 0, 0)
uz4D = Direction4(0, 0, 1, 0)
uw4D = Direction4(0, 0, 0, 1)
null2D = Vec2(0, 0)
null3D = Vec3(0, 0, 0)
null4D = Vec4(0, 0, 0, 0)

#
# Criação de vetores e pontos
#


def Vec(*args):
    '''Converte o argumento em um vetor de compontentes do tipo float'''

    if len(args) == 1:
        return Vec(*args[0])
    elif len(args) == 2:
        return Vec2.from_flat(args)
    elif len(args) == 3:
        return Vec3.from_flat(args)
    elif len(args) == 4:
        return Vec4.from_flat(args)
    else:
        return Vec.from_flat(args, dtype=float)


def asvector(u):
    if isinstance(u, (Vec2, Vec3, Vec4)):
        return u
    else:
        return Vec(*u)


def point(*args):
    '''Converte o argumento em um ponto de compontentes do tipo float'''

    if len(args) == 1:
        return point(*args[0])
    elif len(args) == 2:
        return Point2.from_flat(args)
    elif len(args) == 3:
        return Point3.from_flat(args)
    elif len(args) == 4:
        return Point4.from_flat(args)
    else:
        return Point.from_flat(args, dtype=float)


def direction(*args):
    '''Converte o argumento em um vetor direção unitária de compontentes do
    tipo float'''

    if len(args) == 1:
        return point(*args[0])
    elif len(args) == 2:
        return Direction2.from_flat(args)
    elif len(args) == 3:
        return Direction3.from_flat(args)
    elif len(args) == 4:
        return Direction4.from_flat(args)
    else:
        return Direction.from_flat(args, dtype=float)


#
# 2D projection functions
#
def shadow_x(A, B):
    '''Overlap between shapes A and B in the x direction'''

    return min(A.xmax, B.xmax) - max(A.xmin, B.xmin)


def shadow_y(A, B):
    '''Retorna o tamanho da sombra comum entre os objetos A e B no eixo y.
    Caso não haja superposição, retorna um valor negativo que corresponde ao
    tamanho do buraco'''

    return min(A.ymax, B.ymax) - max(A.ymin, B.ymin)


if __name__ == '__main__':
    print(Vec(1, 2) + (1, 2))
    print((1, 2) + Vec(1, 2))
    print(2 * Vec(1, 2))
    print(Vec(1, 2) * 2)
    print(asvector((1, 2)))
