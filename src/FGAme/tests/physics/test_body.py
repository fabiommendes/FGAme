from FGAme.tests.physics import test_particle as base
from FGAme.physics.bodies import Body
from smallshapes.tests import abstract as shape_tests


class TestBody(base.TestParticle, shape_tests.TestSolid):
    base_cls = Body