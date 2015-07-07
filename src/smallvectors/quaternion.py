# -*- coding: utf8 -*-
'''
Quaternion algebra and rotations
'''

from smallvectors import Vec3, normalize
import math as m


class Quaternion(object):

    '''A quaternion class'''

    def __init__(self, *args):
        if len(args) == 1:
            return self.__init__(*args)
        elif len(args) == 2:
            s, vec = args
        else:
            s, x, y, z = args
            vec = Vec3(x, y, z)
        super(Quaternion, self).__init__(s, vec)

    @classmethod
    def from_rotation(cls, theta, axis):
        '''Create a rotation quaternion from angle and rotation axis'''

        return Quaternion(m.cos(theta / 2), m.sin(theta / 2) * normalize(axis))

    #
    # Special operations
    #
    def conjugate(self):
        '''Return the conjugate quaternion'''

        return Quaternion(self.scalar, -self.vector)

    def inv(self):
        '''Return the inverse quaternion'''

        return Quaternion(self.scalar, -self.vector) / self.norm_sqr()

    #
    # Geoemtric operations
    #
    def norm(self):
        '''Absolute value of quaternion'''

        return m.sqrt(self.scalar ** 2 + self.vector.norm_sqr())

    def norm_sqr(self):
        '''Squared absolute value'''

        return self.scalar ** 2 + self.vector.norm_sqr()

    def normalize(self):
        '''Return the normalized quaternion'''

        Z = self.norm_sqr()
        if abs(Z - 1.0) < 1e-6:
            return self
        else:
            return self / m.sqrt(Z)

    #
    # Conversion functions
    #
    def to_matrix(self):
        '''Convert quaternion to the equivalent rotation matrix'''

        from mathtools import Mat3

        s, (x, y, z) = self.normalize()

        xx = 2 * x * x
        yy = 2 * y * y
        zz = 2 * z * z
        xy = 2 * x * y
        yz = 2 * y * z
        zx = 2 * z * x
        sx = 2 * s * x
        sy = 2 * s * y
        sz = 2 * s * z
        DD = 1 - xx - yy - zz

        return Mat3([[DD + xx, xy - sz, zx + sy],
                     [xy + sz, DD + yy, yz - sx],
                     [zx - sy, yz + sx, DD + zz]])

    def to_rotation(self):
        '''Return a tuple of (theta, axis) equivalent to the quaternion
        rotation'''

        q = self.normalize()
        return (m.acos(q.scalar), q.vector.normalize())

    #
    # Magic methods
    #
    def __abs__(self):
        return self.norm()

    def __iter__(self):
        yield self.scalar
        yield self.vector

    def __getitem__(self, idx):
        if idx == 0:
            return self.scalar
        elif idx == 1:
            return self.vector.x
        elif idx == 2:
            return self.vector.y
        elif idx == 3:
            return self.vector.z
        else:
            raise IndexError(idx)

    def __mul__(self, other):
        if isinstance(other, Quaternion):
            s1, v1 = self
            s2, v2 = other
            scalar = s1 * s2 - v1.dot(v2)
            vector = s1 * v2 + s2 * v1 + s1.cross(s2)
            return Quaternion(scalar, vector)
        else:
            return Quaternion(self.scalar * other, self.vector * other)

    def __add__(self, other):
        s = self.scalar + other.scalar
        v = self.vector + other.vector
        return Quaternion(s, v)

    def __sub__(self, other):
        s = self.scalar - other.scalar
        v = self.vector - other.vector
        return Quaternion(s, v)
