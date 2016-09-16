from FGAme.tests.physics import test_particle as base
from FGAme.physics.bodies import Body
from smallshapes.tests import abstract as shape_tests


class TestBody(base.TestParticle, shape_tests.TestSolid):
    base_cls = Body

    def test_aabb_limits_aliases(self, obj):
        assert obj.xmin == obj.left
        assert obj.xmax == obj.right
        assert obj.ymin == obj.bottom
        assert obj.ymax == obj.top

    def test_aabb_coords_setters(self, obj):
        pos = obj.pos
        obj.xmin += 10
        assert obj.x == obj.pos.x