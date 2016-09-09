from math import *
import smallshapes as shapes
from smallvectors import *

# Vector type aliases
Vec2 = Vec[2, float]
Vec3 = Vec[3, float]
Vec4 = Vec[4, float]
Vec = Vec2
Direction2 = Direction[2, float]
Direction3 = Direction[3, float]
Direction4 = Direction[4, float]
Direction = Direction2

# Unitary directions and null vectors
ux = ux2D = Direction2(1, 0)
uy = uy2D = Direction2(0, 1)
ux3D = Direction3(1, 0, 0)
uy3D = Direction3(0, 1, 0)
uz3D = Direction3(0, 0, 1)
ux4D = Direction4(1, 0, 0, 0)
uy4D = Direction4(0, 1, 0, 0)
uz4D = Direction4(0, 0, 1, 0)
uw4D = Direction4(0, 0, 0, 1)
nullvec = null2D = Vec2(0, 0)
null3D = Vec3(0, 0, 0)
null4D = Vec4(0, 0, 0, 0)


def vec(*args):
    """
    Creates a vector of 2, 3 or 4 dimensions
    """

    N = len(args)
    if N == 2:
        return Vec2(args[0], args[1])
    elif N == 3:
        return Vec3(args[0], args[1], args[2])
    elif N == 2:
        return Vec4(args[0], args[1], args[2], args[3])
    else:
        raise ValueError('invalid number of components: %s' % N)


def asvector(u):
    """
    Return argument as vector.
    """

    if isinstance(u, (Vec2, Vec3, Vec4)):
        return u
    else:
        return vec(*u)


def direction(*args):
    """
    Creates an unitary direction vector in the given coordinates.
    """

    N = len(args)
    if N == 2:
        return Direction2(args[0], args[1])
    elif N == 3:
        return Direction3(args[0], args[1], args[2])
    elif N == 2:
        return Direction4(args[0], args[1], args[2], args[3])
    else:
        raise ValueError('invalid number of components: %s' % N)


def asdirection(u):
    """
    Return object as a direction.
    """

    if isinstance(u, (Direction2, Direction3, Direction4)):
        return u
    else:
        return direction(*u)


def shadow_x(A, B):
    """
    Overlap between shapes A and B in the x direction.
    """

    return min(A.xmax, B.xmax) - max(A.xmin, B.xmin)


def shadow_y(A, B):
    """
    Overlap between shapes A and B in the y direction.
    """

    return min(A.ymax, B.ymax) - max(A.ymin, B.ymin)
