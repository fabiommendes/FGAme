#-*- coding: utf8 -*-
from FGAme.mathutils import Vector, VectorM, pi
import nose

#===============================================================================
# Operações matemáticas básicas
#===============================================================================
def test_vector_add():
    v1 = Vector(1, 2)
    v2 = Vector(2, 3)
    assert v1 + v2 == Vector(3, 5)
    assert tuple(v1 + v2) == (3, 5)
    assert v2 - v1 == Vector(1, 1)
    
def test_vector_tuple_add():
    v = Vector(1, 2)
    assert v + (1, 2) == Vector(2, 4)
    assert (1, 2) + v == Vector(2, 4)
    assert v - (1, 2) == Vector(0, 0)
    assert (1, 2) - v == Vector(0, 0)
    
def test_vector_algeb():
    v1 = Vector(1, 2)
    v2 = Vector(2, 3)
    v3 = Vector(4, 5)
    assert 2 * v1 == Vector(2, 4)
    assert v1 * 2 == Vector(2, 4)
    assert v1 + 2 * v2 - 3 * v3 == Vector(-7, -7)

def test_vector_norm():
    v = Vector(1, 2)
    u = v.normalized()
    r = v.rotated(pi/3)
    assert abs(u.norm() - 1) < 1e-6, u.norm()
    assert abs(v.norm() - r.norm()) < 1e-6, (v.norm(), r.norm())

def test_vector_rotation():
    v = Vector(1, 0)
    assert (v.rotated(pi/2) - Vector(0, 1)).norm() < 1e-6, v
    
#===============================================================================
# Interface Python    
#===============================================================================
def test_vector_iter():
    v = Vector(1, 2)
    it = iter(v)
    assert next(it) == 1
    assert next(it) == 2
    nose.tools.assert_raises(StopIteration, lambda: next(it))

def test_vector_getitem():
    v = Vector(1, 2)
    assert v[0] == 1, v[1] == 2
