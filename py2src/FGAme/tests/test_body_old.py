# -*- coding: utf8 -*-
import unittest
from FGAme.physics.bodies import Body, Circle, AABB, Poly, RegularPoly, Rectangle

def assert_simeq(L1, L2, delta=None, places=7):
    L1 = list(L1)
    L2 = list(L2)
    if len(L1) != len(L2):
        raise AssertionError('different length: %r != %r' % (L1, L2))
    
    for i, (x, y) in enumerate(zip(L1, L2)):
        if (round(x - y, places) if delta is None else abs(x - y) < delta): 
            raise AssertionError('%s-th position: %r != %r' % (i, x, y))
        
        
class BodyTestCase(unittest.TestCase):
    def test_body_flags(self):
        body = Body(mass=1)
        self.assertEqual(body.owns_gravity, False)
        body.owns_gravity = True
        self.assertEqual(body.owns_gravity, True)


class BodyTestBase(unittest.TestCase):
    '''Test case base para todos os objetos físicos da FGAme'''
    
    args = ()
    kwds = {'mass': 1}
    cls = Body
            
    def new(self):
        return self.cls(*self.args, **self.kwds)    

    def test_bb_move(self):
        obj = self.new()
        bb = obj.bb
        obj.move(10, 10)
        assert_simeq(bb.displaced(10, 10).flat, obj.bb.flat)
    
    def test_cbb_move(self):
        obj = self.new()
        bb = obj.cbb
        obj.move(10, 10)
        self.assertEqual(bb.displaced(10, 10), obj.cbb)
        
    def test_aabb_move(self):
        obj = self.new()
        bb = obj.aabb
        obj.move(10, 10)
        #FIXME: self.assertEqual(bb.displaced(10, 10), obj.aabb)

class CircleTest(BodyTestBase):
    args = (5,)
    kwds = {}
    cls = Circle

class AABBTest(BodyTestBase):
    kwds = {'shape': (10, 10)}
    cls = AABB

class RectangleTest(BodyTestBase):
    kwds = {'shape': (10, 10)}
    cls = Rectangle
    
class RegularPolyTest(BodyTestBase):
    args = (3,)    
    kwds = {'length': 10}
    cls = RegularPoly

class PolyTest(BodyTestBase):
    args = ([(0, 0), (10, 0), (0, 10)],)
    cls = Poly


def test_poly_creation():
    assert Poly([(0, 0), (10, 0), (0, 10)])


if __name__ == '__main__':
    from pytest import main
    main('test_body.py -v')