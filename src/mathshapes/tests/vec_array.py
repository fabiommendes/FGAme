# -*- coding: utf8 -*-

from FGAme.mathutils import Vec2, mVec2, pi
from FGAme.util import lazy
from nose.tools import raises, assert_almost_equal, assert_almost_equals
import nose
from unittest import TestCase


class Immutable(object):
    vecarray = None
    array = None

    @lazy
    def A(self):
        return self.vector(1, 2)

    @lazy
    def B(self):
        return self.vector(2, 1)

    # Construtores ############################################################
    def test_init_pos(self):
        assert self.vector(1, 2) == self.vector(1.0, 2.0) == (1, 2)

    def test_init_seq(self):
        assert self.vector(1, 2) == self.vector((1, 2))

    # Comparação com tuplas ###################################################
    def test_tuple_compare(self):
        assert self.vector(1, 2) == (1, 2)
        assert (1, 2) == self.vector(1, 2)

    # Operações matemáticas ###################################################
    def test_add(self):
        v1 = self.vector(1, 2)
        v2 = self.vector(2, 1)
        assert v1 + v2 == self.vector(3, 3)
        assert v1 + (2, 1) == self.vector(3, 3)
        assert (2, 1) + v1 == self.vector(3, 3)

    def test_sub(self):
        v1 = self.vector(1, 2)
        v2 = self.vector(2, 1)
        assert v1 - v2 == self.vector(-1, 1)
        assert v1 - (2, 1) == self.vector(-1, 1)
        assert (1, 2) - v2 == self.vector(-1, 1)

    def test_mul(self):
        v = self.vector(1, 2)
        assert v * 2 == (2, 4)
        assert 2 * v == (2, 4)

    def test_linear(self):
        v1 = self.vector(1, 2)
        v2 = self.vector(2, 1)
        assert v1 + 2 * v2 == (5, 4)

    def test_div(self):
        v = self.vector(2, 4)
        assert v / 2 == (1, 2)

    def test_neg(self):
        v = self.vector(1, 2)
        assert -v == (-1, -2)

    # Operações matemáticas inválidas #########################################
    @raises(TypeError)
    def test_add_scalar(self):
        self.vector(1, 2) + 1

    @raises(TypeError)
    def test_sub_scalar(self):
        self.vector(1, 2) - 1

    @raises(TypeError)
    def test_mul_tuple(self):
        self.vector(1, 2) * (1, 2)

    @raises(TypeError)
    def test_mul_vec(self):
        self.vector(1, 2) * self.vector(1, 2)

    @raises(TypeError)
    def test_div_vec_vec(self):
        self.vector(1, 2) / self.vector(1, 2)

    @raises(TypeError)
    def test_div_num_vec(self):
        1 / self.vector(1, 2)

    # Propriedades de vetores e operações geométricas #########################
    def test_vector_norm(self):
        v = self.vector(3, 4)
        assert_almost_equal(v.norm(), 5)
        assert_almost_equal(v.norm_sqr(), 25)

    def test_rotated(self):
        v = self.vector(1, 2)
        v_rot = v.rotate(pi / 2)
        v_res = self.vector(-2, 1)
        assert_almost_equal((v_rot - v_res).norm(), 0)
        assert_almost_equal((v_rot.rotate(pi / 2) + v).norm(), 0)
        assert_almost_equal(v.norm(), v.rotate(pi / 2).norm())

    def test_normalized(self):
        v = self.vector(1, 2)
        n = v.normalize()

        assert_almost_equal(v.normalize().norm(), 1)
        assert_almost_equals(n.x * v.x + n.y * v.y, v.norm())

    # Interface Python ########################################################
    def test_as_tuple(self):
        v = self.vector(1, 2)
        t = v.as_tuple()
        assert isinstance(t, tuple)
        assert t == (1, 2)

    def test_getitem(self):
        v = self.vector(1, 2)
        assert v[0] == 1, v[1] == 2

    @raises(IndexError)
    def test_overflow(self):
        v = self.vector(1, 2)
        v[2]

    def test_iter(self):
        v = self.vector(1, 2)
        assert list(v) == [1, 2]

    def test_len(self):
        v = self.vector(1, 2)
        assert len(v) == 2


class Mutable(Immutable):
    # Modificação de coordenadas ##############################################

    def test_set_coords(self):
        v = self.vector(1, 2)
        v.x = 2
        assert v == (2, 2)

    def test_setitem(self):
        v = self.vector(1, 2)
        v[0] = 2
        assert v == (2, 2)

    def test_update(self):
        v = self.vector(1, 2)
        v.update(2, 1)
        assert v == (2, 1)
        v.update((1, 2))
        assert v == (1, 2)

    # Operações matemáticas inplace ###########################################
    def test_iadd(self):
        v = self.vector(1, 2)
        v += (1, 2)
        assert v == (2, 4)

    def test_imul(self):
        v = self.vector(1, 2)
        v *= 2
        assert v == (2, 4)

    def test_idiv(self):
        v = self.vector(1, 2)
        v /= 0.5
        assert v == (2, 4)

###############################################################################
#                                TestCases
###############################################################################


class CVectorTest(Immutable, TestCase):
    from FGAme.mathutils.cvector import Vec2 as vector


class CVectorMTest(Mutable, TestCase):
    from FGAme.mathutils.cvector import mVec2 as vector


class PyVectorTest(Immutable, TestCase):
    from FGAme.mathutils.vector import Vec2 as vector


class PyVectorMTest(Mutable, TestCase):
    from FGAme.mathutils.vector import mVec2 as vector


if __name__ == '__main__':
    nose.runmodule('__main__')
