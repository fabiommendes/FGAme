from FGAme import draw
from FGAme.tests.draw import abstract as base
from smallshapes.tests import test_circle, test_segment, test_aabb


class TestSegment(base.TestShape, test_segment.TestSegment):
    base_cls = draw.Segment


class TestCircle(base.TestSolid, test_circle.TestCircle):
    base_cls = draw.Circle
    base_args = (10, (0, 0))

    def test_circle_radius_and_pos_are_defined(self, obj):
        assert obj.radius == 10
        assert obj.pos == (0, 0)


class TestAABB(base.TestSolid, test_aabb.TestAABB):
    base_cls = draw.AABB
