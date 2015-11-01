from FGAme.physics.bodies import Body, Circle, AABB, Poly, RegularPoly, Rectangle
from FGAme.tests.base import unittest


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
        self.assertEqual(bb.displaced(10, 10), obj.bb)
    
    def test_cbb_move(self):
        obj = self.new()
        bb = obj.cbb
        obj.move(10, 10)
        self.assertEqual(bb.displaced(10, 10), obj.cbb)
        
    def test_aabb_move(self):
        obj = self.new()
        bb = obj.aabb
        obj.move(10, 10)
        self.assertEqual(bb.displaced(10, 10), obj.aabb)


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
    args = ([(0, 0), (10, 0), (0, 10)],)
    kwds = {'length': 10}
    cls = RegularPoly

class PolyTest(BodyTestBase):
    args = (3,)
    kwds = {'length': 10}
    cls = Poly



if __name__ == '__main__':
    unittest.main()