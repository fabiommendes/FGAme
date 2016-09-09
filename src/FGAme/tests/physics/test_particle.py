import pytest
from smallshapes.tests import abstract as base
from smallvectors import simeq
from smallshapes.tests.abstract import DisableMutabilityTests
from FGAme.physics.bodies import Particle
from FGAme.mathtools import Vec2


class DisabledSmallshapesTests(DisableMutabilityTests):
    """
    Disable tests in the smallshapes test suite
    """

    test_displacement_creates_a_new_object = \
        test_vec_displacement_creates_a_new_object =\
        test_displaced = None
    test_object_has_no_dict = None


class TestParticle(DisabledSmallshapesTests, base.TestLocatable):
    base_cls = Particle
    base_args = ()
    base_shape_args = ()

    @pytest.fixture
    def shape_args(self):
        return self.base_shape_args

    @pytest.fixture
    def vel(self):
        return Vec2(1, 0)

    @pytest.fixture
    def moving(self, vel):
        return self.base_cls(*self.base_args, vel=vel)

    # Consistency
    def test_default_object_is_on_origin(self, obj):
        assert simeq(obj.pos, (0, 0))

    # Dynamic variables
    def test_standing_object_do_not_change_position(self, obj):
        obj.update(1)
        assert obj.pos == (0, 0)

    def test_force_changes_object_position_and_velocity(self, obj):
        obj.apply_force((1, 0), 1)
        assert obj.x > 0
        assert obj.y == 0
        assert obj.vx > 0
        assert obj.vy == 0

    def test_scalar_state_accessors(self, obj):
        obj.move_to(1, 2)
        obj.boost(3, 4)
        assert obj.x == 1
        assert obj.y == 2
        assert obj.vx == 3
        assert obj.vy == 4

    def test_move_functions_signature(self, obj):
        for args in [[Vec2(1, 2)], [(1, 2)], (1, 2)]:
            obj.move(*args)
            obj.imove(*args)
            obj.boost(*args)
            obj.move_to(*args)

    # Energy
    def test_kinetic_energy_of_moving_obj_is_positive(self, moving):
        assert moving.energyK() > 0

    def test_total_energy_is_kinetic_energy_for_free_object(self, obj):
        assert obj.energyK() == obj.energy()
