from FGAme.tests.physics import test_particle as base
from FGAme.physics.bodies import Body
from smallshapes.tests import abstract as shape_tests
from FGAme.mathtools import vec
import pytest

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

    ## methods from physics/utils.py

    def test_center_mass(self):

        from FGAme.physics.utils import center_of_mass

        b1 = Body(pos=(0, 30), mass=1)
        b2 = Body(pos=(10, 0), mass=3)

        vector = vec(7.5,7.5)

        assert center_of_mass(b1, b2) == vector

    def test_mass(self):

        from FGAme.physics.utils import mass

        b1 = Body(pos=(0, 30), mass=1)
        b2 = Body(pos=(10, 0), mass=3)

        assert mass(b1,b2) == 4

    def test_inertia(self):

        from FGAme.physics.utils import inertia

        b1 = Body(mass=1, inertia=2)
        b2 = Body(pos=(1, 0), mass=3, inertia=1)

        assert inertia(b1, b2) == 3.75

    def test_momentumP(self):

        from FGAme.physics.utils import momentumP

        b1 = Body(pos=(2, 0), mass=1)
        b2 = Body(pos=(-1, 0), mass=2)

        vector = vec(0.0,0.0)

        assert momentumP(b1, b2) == vector

    def test_momentumL(self):

        from FGAme.physics.utils import momentumL

        b1 = Body(mass=1)
        b2 = Body(pos=(-1, 0), mass=2)

        with pytest.raises(Exception):
            momentumL(b1, b2)

    def test_energyK(self):

        from FGAme.physics.utils import energyK

        b1 = Body(pos=(2, 0), mass=1)
        b2 = Body(pos=(-1, 0), mass=2)

        assert energyK(b1,b2) == 0.0

    def test_linearK(self):

        from FGAme.physics.utils import linearK

        b1 = Body(pos=(2, 0), mass=1)
        b2 = Body(pos=(-1, 0), mass=2)

        assert linearK(b1,b2) == 0.0

    def test_angularK(self):

        from FGAme.physics.utils import angularK

        b1 = Body(pos=(2, 0), mass=1)
        b2 = Body(pos=(-1, 0), mass=2)

        assert angularK(b1,b2) == 0.0

    def test_energyU(self):

        from FGAme.physics.utils import energyU

        b1 = Body(pos=(2, 0), mass=1)
        b2 = Body(pos=(-1, 0), mass=2)

        assert energyU(b1,b2) == 0.0

    def test_energy(self):

        from FGAme.physics.utils import energy

        b1 = Body(pos=(2, 0), mass=1)
        b2 = Body(pos=(-1, 0), mass=2)

        assert energy(b1,b2) == 0.0

    def test_safe_div(self):

        from FGAme.physics.utils import safe_div

        assert safe_div(10,2) == 5
        assert safe_div(10,0) == float('inf')

    def test_normalize_flag_value(self):

        from FGAme.physics.utils import normalize_flag_value

        assert normalize_flag_value('has_external_alpha') != None
        assert normalize_flag_value(2) == 2

    def test_aslist(self):

        from FGAme.physics.utils import aslist

        assert aslist('hello') == 'hello'
        assert aslist(['hello', 'test']) ==  ['hello', 'test']

        with pytest.raises(Exception):
            aslist()