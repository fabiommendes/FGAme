from FGAme.physics import bodies, get_collision
from FGAme.tests.physics import test_body
from smallshapes.tests import test_aabb
from smallshapes.tests import test_circle


class TestCircle(test_body.TestBody, test_circle.TestCircle):
    base_cls = bodies.Circle
    base_args = (10, (0, 0))
    base_shape_args = (10,)

    def test_circle_collision(self, cls):
        c1 = cls(10, (0, 0))
        c2 = cls(10, (10, 10))
        c3 = cls(10, (20, 20))
        assert get_collision(c1, c2) is not None
        assert get_collision(c2, c3) is not None
        assert get_collision(c1, c3) is None


class TestAABB(test_body.TestBody, test_aabb.TestAABB):
    base_cls = bodies.AABB
    base_args = (-50, 50, -100, 100)
    base_shape_args = base_args

    def test_aabb_collision(self, cls):
        a = cls(0, 10, 0, 10)
        b = cls(5, 15, 5, 15)
        c = cls(11, 15, 11, 16)
        assert get_collision(a, b) is not None
        assert get_collision(b, c) is not None
        assert get_collision(a, c) is None
