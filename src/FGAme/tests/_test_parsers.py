from FGAme.extra.parsers import *
import unittest

#
# Examples
#
declaration1 = '''
<brick@AABB>:
    shape: (100, 100)
    color: random

bricks:
    brick: brick
        pos: (0, 0)
'''


#
# Test cases
#
class TestDeclarationParser(unittest.TestCase):
    def objects(self, source):
        world = set()
        populate(world, source)
        return sorted(world)
    
    def _test_declaration_with_template(self):
        aabb, = self.objects(declaration1)
        self.assertEqual(aabb.pos, (0, 0))
        self.assertEqual(aabb.shape, (100, 100))
