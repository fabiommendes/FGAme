# -*- coding: utf8 -*-
'''
Importa as funções matemáticas do módulo mathutils.
'''

from math import *
from smallvectors import *
import smallvectors as linalg
from smallshapes import *
import smallshapes as shapes
from generic import set_promotion_rule, set_conversion
from generic.op import add, sub, mul, truediv


#
# Apelidos para tipos vetoriais
#
class FGAmeVec(object):
    '''A FGAme vector object'''

    def __repr__(self):
        data = ['%.1f' % x for x in self]
        if all(x.endswith('.0') for x in data):
            data = [x[:-2] for x in data]
        return 'Vec(%s)' % (', '.join(data))

class Vec2(FGAmeVec, Vec[2, float]):
    '''Vetor bidimensional'''
   
class Vec3(FGAmeVec, Vec[3, float]):
    '''Vetor bidimensional'''
    
class Vec4(FGAmeVec, Vec[4, float]):
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
        x, y = args
        return Vec2(x + 0.0, y + 0.0)
    elif len(args) == 3:
        x, y, z = args
        return Vec3(x + 0.0, y + 0.0, z + 0.0)
    elif len(args) == 4:
        x, y, z, w = args
        return Vec4(x + 0.0, y + 0.0, z + 0.0, w + 0.0)
    else:
        raise TypeError


def asvector(u):
    '''Retorna o argumento como vetor'''
    if isinstance(u, (Vec2, Vec3, Vec4)):
        return u
    else:
        return Vec(*u)


def direction(*args):
    '''Converte o argumento em um vetor direção unitária de compontentes do
    tipo float'''

    if len(args) == 1:
        return Direction(*args[0])
    elif len(args) == 2:
        return Direction2.fromflat(args)
    elif len(args) == 3:
        return Direction3.fromflat(args)
    elif len(args) == 4:
        return Direction4.fromflat(args)
    else:
        return Direction.fromflat(args, dtype=float)


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
