from FGAme import draw
import unittest


class TestAABB(unittest.TestCase):
    def test_aabb_moves(self):
        aabb = draw.AABB(pos=(0, 0), shape=(1, 2))
        aabb.pos = (1, 1)
        self.assertEqual(aabb.pos, (1, 1))


if __name__ == "__main__":
    unittest.main()