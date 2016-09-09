import copy

import smallshapes as shapes
import smallshapes.core.locatable
from FGAme.mathtools import null2D, asvector, Vec2
from FGAme.physics import flags
from FGAme.physics.bodies.utils import flag_property, accept_vec_args, \
    vec_property
from FGAme.physics.forces import ForceProperty
from FGAme.physics.utils import normalize_flag_value
from FGAme.utils import popattr


class Particle(smallshapes.core.locatable.mLocatable):
    """
    Basic particle physics simulation.

    A particle has position, velocity and mass, but do not have any angular
    dynamics.
    """

    __slots__ = [
        '_invmass', '_pos', '_vel', '_acceleration',
        '_restitution', '_damping', '_friction', '_gravity',
        '_col_layer_mask', '_col_group_mask',
        'flags',
        '__dict__',
    ]

    # pre_collision = signal('pre-collision', num_args=1)
    # post_collision = signal('post-collision', num_args=1)
    # frame_enter = signal('frame-enter')
    # out_of_bounds = signal('out-of-margin', num_args=1)
    has_physics = True
    DEFAULT_FLAGS = 0 | flags.dirty_shape | flags.dirty_aabb

    def __init__(self,
                 pos=null2D, vel=null2D, mass=1.0,
                 gravity=None, damping=None, adamping=None,
                 restitution=None, friction=None,
                 simulation=None,
                 col_layer=0, col_group=0,
                 flags=DEFAULT_FLAGS):

        self._simulation = simulation

        # Object flags
        self.flags = flags

        # State variables
        self._pos = asvector(pos)
        self._vel = asvector(vel)
        self._acceleration = null2D
        self._invmass = 1 / mass

        # Control object-local physical parameters
        self._gravity = null2D
        self._damping = 0.0
        self._friction = 0.0
        self._restitution = 1.0
        if damping is not None:
            self.damping = damping
        if gravity is not None:
            self.gravity = gravity
        if restitution is not None:
            self.restitution = restitution
        if friction is not None:
            self.friction = friction

        # Collision filters
        self.collisions = []
        if col_layer:
            if isinstance(col_layer, int):
                self._col_layer_mask = 1 << col_layer
            else:
                mask = 0
                for n in col_layer:
                    mask |= 1 << n
                self._col_layer_mask = mask
        else:
            self._col_layer_mask = 0

        if col_group:
            if isinstance(col_group, int):
                self._col_group_mask = 1 << (col_group - 1)
            else:
                mask = 0
                for n in col_group:
                    mask |= 1 << (n - 1)
                self._col_group_mask = mask
        else:
            self._col_group_mask = 0

        # World
        if simulation is not None:
            self._simulation.add(self)

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)

    def __repr__(self):
        tname = type(self).__name__
        pos = ', '.join('%.1f' % x for x in self._pos)
        vel = ', '.join('%.1f' % x for x in self._vel)
        return '%s(pos=(%s), vel=(%s))' % (tname, pos, vel)

    def get_flag(self, flag):
        """
        Returns the value of the given flag.

        The flag argument can be a string or a constant in FGAme.physics.flags.
        """

        return bool(self.flags | normalize_flag_value(flag))

    def set_flag(self, flag, value):
        """
        Set the true/
        assert 'trigger_frame_enter' in methods
        assert 'trigger_out_ofalse value of a given flag.

        The flag argument can be a string or a constant in FGAme.physics.flags.
        """

        if value:
            self.flags |= normalize_flag_value(flag)
        else:
            self.flags &= ~normalize_flag_value(flag)

    def toggle_flag(self, flag):
        """
        Inverts the boolean value of the given flag.

        The flag argument can be a string or a constant in FGAme.physics.flags.
        """

        flag = normalize_flag_value(flag)
        value = not (self.flags & flag)
        if value:
            self.flags |= flag
        else:
            self.flags &= ~flag

    owns_gravity = flag_property(flags.owns_gravity)
    owns_damping = flag_property(flags.owns_damping)
    owns_adamping = flag_property(flags.owns_adamping)
    owns_restitution = flag_property(flags.owns_restitution)
    owns_friction = flag_property(flags.owns_friction)
    can_rotate = flag_property(flags.can_rotate)

    # Mass properties
    @property
    def invmass(self):
        return self._invmass

    @property
    def invinertia(self):
        return self._invinertia

    @property
    def mass(self):
        try:
            return 1.0 / self._invmass
        except ZeroDivisionError:
            return float('inf')

    @mass.setter
    def mass(self, value):
        self._invmass = 1.0 / value

    # Global forces
    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value):
        try:
            self._gravity = Vec2(*value)
        except TypeError:
            self._gravity = Vec2(0, -value)
        self.owns_gravity = True

    @property
    def damping(self):
        return self._damping

    @damping.setter
    def damping(self, value):
        self._damping = float(value)
        self.owns_damping = True

    @property
    def restitution(self):
        return self._restitution

    @restitution.setter
    def restitution(self, value):
        self._restitution = float(value)
        self.owns_restitution = True

    @property
    def friction(self):
        return self._friction

    @friction.setter
    def friction(self, value):
        self._friction = float(value)
        self.owns_friction = True

    # Interaction with physics simulation.
    @property
    def simulation(self):
        if self._simulation is None:
            raise ValueError('object is not linked with any simulation')
        else:
            return self._simulation

    def destroy(self):
        """
        Destroy object.
        """

        if self._simulation is not None:
            self.simulation.remove(self)

    def copy(self):
        """
        Return a copy of object.
        """

        try:
            simulation, self._simulation = self._simulation, None
            cp = copy.copy(self)
        finally:
            self._simulation = simulation
        return cp

    # Physical properties
    force = ForceProperty()

    def linearK(self):
        """
        Kinetic energy of linear movement.
        """

        if self._invmass:
            return self._vel.norm_sqr() / (2 * self._invmass)
        else:
            return 0.0

    def energyK(self):
        """
        Total kinetic energy: sum of linearK and angularK.
        """

        return self.linearK()

    def energyU(self):
        """
        Potential energy associated with gravity and other external forces.
        """

        return -self.gravity.dot(self._pos) / self._invmass

    def energy(self):
        """
        Total energy: sum of energyU and energyK.
        """

        return self.energyK() + self.energyU()

    def momentumP(self):
        """
        Linear momentum.
        """

        try:
            return self._vel / self._invmass
        except ZeroDivisionError:
            return Vec2(float('inf'), float('inf'))

    # Position and movement
    @property
    def pos(self):
        return self._pos

    @property
    def x(self):
        return self._pos.x

    @x.setter
    def x(self, value):
        self.move_to()

    @property
    def y(self):
        return self._pos.y

    @property
    def vx(self):
        return self._vel.x

    @vx.setter
    def vx(self, value):
        self._vel = Vec2(value, self._vel.y)

    @property
    def vy(self):
        return self._vel.y

    @vy.setter
    def vy(self, value):
        self._vel = Vec2(self._vel.x, value)

    def move_vec(self, vec):
        self._pos += vec
        self.flags |= flags.dirty_aabb
        return self

    def move_to_vec(self, vec):
        self._pos = asvector(vec)
        self.flags |= flags.dirty_aabb
        return self

    def imove_vec(self, vec):
        """
        Alias to .move_vec().

        Exists for consistency with the mLocatable API.
        """

        self.move_vec(vec)

    def imove_to_vec(self, vec):
        """
        Alias to .move_to_vec().

        Exists for consistency with the mLocatable API.
        """

        self.move_to_vec(vec)

    @accept_vec_args
    def boost(self, vec):
        """
        Shifts the linear velocity.
        """

        self.boost_vec(vec)

    def boost_vec(self, vec):
        """
        Like .boost(), but accepts only vec arguments.
        """

        self._vel += vec

    # Forces and acceleration
    def init_accel(self):
        """
        Initialize the accumulated acceleration vector in the beginning of a
        frame.
        """

        if self._damping:
            a = self._vel
            a *= -self._damping
            if self.gravity is not None:
                a += self._gravity
        elif self._gravity is not None:
            a = self._gravity
        else:
            a = null2D
        self._acceleration = a

    def apply_force(self, force, dt, method=None):
        """
        Apply a linear force during interval dt.

        This has no effect on kinematic objects.
        """

        self.apply_accel(asvector(force) * self._invmass, dt, method)

    def apply_accel(self, a, dt, method=None):
        """
        Apply linear acceleration during interval dt.
        """

        a = asvector(a)

        if method is None or method == 'euler-semi-implicit':
            self.boost(a * dt)
            self.move(self._vel * dt + a * (0.5 * dt * dt))
        elif method == 'verlet':
            raise NotImplementedError
        elif method == 'euler':
            self.move(self._vel * dt + a * (0.5 * dt * dt))
            self.boost(a * dt)
        else:
            raise ValueError('invalid method: %r' % method)

    def apply_impulse(self, vec):
        """
        Apply a linear impulse to object.
        """

        self.boost(vec * self._invmass)

    def update(self, dt, method=None):
        """
        Update physics during interval dt.
        """

        self.apply_accel(null2D, dt, method=method)

    # Dynamic vs. kinematic vs. static objects
    def is_dynamic(self, what=None):
        """
        Dynamic objects respond to forces.

        They must have a well defined (finite) mass or moment of inertia.

        Args:
            what:
                Specify which kind of dynamics one is interested in: 'linear',
                'angular', 'both' or 'any' (default).
        """

        if what is None or what == 'any':
            return self.is_dynamic_linear() or self.is_dynamic_angular()
        elif what == 'both':
            return self.is_dynamic_linear() and self.is_dynamic_angular()
        elif what == 'linear':
            return self.is_dynamic_linear()
        elif what == 'angular':
            return self.is_dynamic_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def is_dynamic_linear(self):
        """
        Return True if object is dynamic in linear variables.
        """

        return bool(self._invmass)

    def is_dynamic_angular(self):
        """
        Return True if object is dynamic in angular variables.
        """

        return bool(self._invinertia)

    def make_dynamic(self, what=None, restore_speed=True):
        """
        Restores mass, inertia, velocity stored after calling
        `obj.make_static()` or `obj.make_kinematic()`.

        Args:
            what:
                Same meaning as in :func:`Particle.is_dynamic`
            restore_speed:
                If True (default) restore previous speed when object is standing
                still.
        """

        if what is None or what == 'both':
            self.make_dynamic_linear(restore_speed)
            self.make_dynamic_angular(restore_speed)
        elif what == 'linear':
            self.make_dynamic_linear(restore_speed)
        elif what == 'angular':
            self.make_dynamic_angular(restore_speed)
        else:
            raise ValueError('unknown mode: %r' % what)

    def make_dynamic_linear(self, restore_speed=True):
        """
        Restores linear dynamic parameters.
        """

        if not self.is_dynamic_linear():
            self._invmass = 1.0 / (self.area() * self._density)

            if restore_speed and self._vel.is_null():
                self._vel = popattr(self, '_old_vel', null2D)

    def make_dynamic_angular(self, restore_speed=True):
        """
        Restores angular dynamic parameters.
        """

        if not self.is_dynamic_angular():
            self._inertia = 1.0 / (self._density * self.ROG_sqr())

            if restore_speed and self._omega == 0:
                self._omega = popattr(self, '_old_omega', 0.0)

    # Kinematic
    def is_kinematic(self, what=None):
        """
        A kinematic object has infinite mass but can move on screen.

        Kinematic objects suffer accelerations from global forces such as
        gravity, damping and friction.

        Args:
            what:
                Specify which kind of dynamics one is interested in: 'linear',
                'angular', 'both' (default) or 'any'.
        """

        if what is None or what == 'both':
            return not (self.is_dynamic_linear() or self.is_dynamic_angular())
        elif what == 'any':
            return (not self.is_dynamic_linear() or
                    not self.is_dynamic_angular())
        elif what == 'linear':
            return not self.is_dynamic_linear()
        elif what == 'angular':
            return not self.is_dynamic_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def is_kinematic_linear(self):
        return not self.is_dynamic_linear()

    def is_kinematic_angular(self):
        return not self.is_dynamic_angular()

    def make_kinematic(self, what=None):
        if what is None or what == 'both':
            self.make_kinematic_linear()
            self.make_kinematic_angular()
        elif what == 'linear':
            self.make_kinematic_linear()
        elif what == 'angular':
            self.make_kinematic_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def make_kinematic_linear(self):
        self._invmass = 0.0

    def make_kinematic_angular(self):
        self._invinertia = 0.0

    # Static
    def is_static(self, what=None):
        """
        Static objects do not move.
        """

        if what is None or what == 'both':
            return self.is_static_linear() and self.is_static_angular()
        elif what == 'any':
            return self.is_static_linear() or self.is_static_angular()
        elif what == 'linear':
            return self.is_static_linear()
        elif what == 'angular':
            return self.is_static_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def is_static_linear(self):
        return self.is_kinematic_linear() and self._vel == null2D

    def is_static_angular(self):
        return self.is_kinematic_angular() and self._omega == 0

    def make_static(self, what=None):
        if what is None or what == 'both':
            self.make_static_linear()
            self.make_static_angular()
        elif what == 'linear':
            self.make_static_linear()
        elif what == 'angular':
            self.make_static_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def make_static_linear(self):
        self.make_kinematic_linear()
        self._old_vel = self._vel
        self._vel = null2D

    def make_static_angular(self):
        self.make_kinematic_angular()
        self._old_omega = self._omega
        self._omega = 0.0

    def _raise_cannot_rotate_error(self):
        raise ValueError('Cannot change angular variables with disabled '
                         '`can_rotate` flag')


Particle.pos = vec_property(Particle._pos)
Particle.vel = vec_property(Particle._vel)
