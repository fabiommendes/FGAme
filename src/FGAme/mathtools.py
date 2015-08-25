#-*- coding: utf8 -*-
'''
Importa as funções matemáticas do módulo mathutils.
'''

from math import *
from smallvectors import *
import smallvectors as linalg
from smallshapes import *
import smallshapes as shapes

#
# Apelidos para tipos vetoriais
#
Point2 = Point[2, float]
Point3 = Point[3, float]
Point4 = Point[4, float]
Vec2 = Vec[2, float]
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


def vec(*args):
    '''Converte o argumento em um vetor de compontentes do tipo float'''

    if len(args) == 1:
        return vec(*args[0])
    elif len(args) == 2:
        return Vec2.from_flat(args)
    elif len(args) == 3:
        return Vec3.from_flat(args)
    elif len(args) == 4:
        return Vec4.from_flat(args)
    else:
        return Vec.from_flat(args, dtype=float)


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
