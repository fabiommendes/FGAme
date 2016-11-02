from FGAme.mathtools import Vec2, asvector, null2D, shapes, Vec
from FGAme.physics import flags
from FGAme.physics.bodies import Particle
from FGAme.physics.utils import safe_div, INF
from smallshapes import Solid
from smallshapes.utils import accept_vec_args

__all__ = ['Body', 'LinearRigidBody']
NOT_IMPLEMENTED = NotImplementedError('must be implemented at child classes')
INERTIA_SCALE = 1


def _do_nothing(*args, **kwds):
    """
    A handle that does nothing
    """


def _raises_method(exception=NOT_IMPLEMENTED):
    """
    Return a method that raises the given exception.
    """

    def method(self, *args, **kwds):
        raise exception

    return method


class Body(Solid, Particle):
    """
    A rigid body element.
    """

    __slots__ = (
        '_invinertia',
        'cbb_radius', '_shape', 'base_shape',
        '_theta', '_omega', '_alpha',
    )
    _e_vel = Vec(0, 0)
    _e_omega = 0

    # Angular state
    @property
    def omega(self):
        """
        Angular velocity (rad/sec).
        """

        return self._omega

    @omega.setter
    def omega(self, value):
        if self.flags & flags.can_rotate:
            self._omega = value + 0.0
        elif value:
            self._raise_cannot_rotate_error()

    @property
    def theta(self):
        """
        Rotation angle (rad)
        """

        return self._theta

    @theta.setter
    def theta(self, value):
        if self.flags & flags.can_rotate:
            self._theta = value + 0.0
        elif value:
            self._raise_cannot_rotate_error()

    # Forces and torques
    @property
    def adamping(self):
        return self._adamping

    @adamping.setter
    def adamping(self, value):
        self._adamping = float(value)
        self.owns_adamping = True

    # Inertia
    def _mass_setter(self, value):
        value = float(value)

        if value <= 0:
            raise ValueError('mass cannot be null or negative')
        elif value != INF:
            self._density = value / self.area()
            if self._invinertia:
                inertia = value * self.ROG_sqr()
                self._invinertia = 1.0 / inertia
            self._invmass = 1.0 / value
        else:
            self._invmass = 0.0
            self._invinertia = 0.0

    @property
    def inertia(self):
        try:
            return 1.0 / self._invinertia
        except ZeroDivisionError:
            return INF

    @inertia.setter
    def inertia(self, value):
        value = float(value)

        if self.can_rotate:
            if value <= 0:
                raise ValueError('inertia cannot be null or negative')
            elif value != INF:
                self._invinertia = 1.0 / value
            else:
                self._invinertia = 0.0
        else:
            self._raise_cannot_rotate_error()

    @property
    def density(self):
        return self._density

    @density.setter
    def density(self, value):
        rho = float(value)
        self._density = rho
        if self._invmass:
            self._invmass = 1.0 / (self.area() * rho)
        if self._invinertia:
            self._invinertia = 1.0 / (self.area() * rho * self.ROG_sqr())

    # Geometric properties
    @property
    def cbb(self):
        return shapes.Circle(self.cbb_radius, self.pos)

    @property
    def aabb(self):
        if self.flags & flags.dirty_aabb:
            self._aabb = self.bb.aabb
            self.flags &= flags.not_dirty_aabb
        return self._aabb

    @property
    def bb(self):
        """
        Bounding box around object.

        Can be of any primitive shape such as AABB, Circle, Poly, etc.
        """

        shape = self.base_shape.move(self.pos)
        if self._theta:
            shape = shape.rotate(self._theta)
        return shape

    xmin = property(lambda self: self.bb.xmin)
    xmax = property(lambda self: self.bb.xmax)
    ymin = property(lambda self: self.bb.ymin)
    ymax = property(lambda self: self.bb.ymax)

    @property
    def left(self):
        return self.xmin

    @left.setter
    def left(self, value):
        self.move(value - self.xmin, 0)

    @property
    def right(self):
        return self.xmax

    @right.setter
    def right(self, value):
        self.move(value - self.xmax, 0)

    @property
    def top(self):
        return self.ymax

    @top.setter
    def top(self, value):
        self.move(0, value - self.ymax)

    @property
    def bottom(self):
        return self.ymin

    @bottom.setter
    def bottom(self, value):
        self.move(0, value - self.ymin)

    @property
    def heading(self):
        try:
            return self.vel.normalize()
        except ZeroDivisionError:
            return self.orientation()

    @heading.setter
    def heading(self, value):
        vel = self.vel
        speed = vel.norm()
        heading = asvector(value).normalize()
        self.vel = heading * speed

    DEFAULT_FLAGS = 0 | flags.can_rotate | flags.dirty_shape | flags.dirty_aabb

    def __init__(self,
                 pos=null2D, vel=null2D,
                 theta=0.0, omega=0.0,
                 adamping=None,
                 density=None, mass=None, inertia=None,
                 base_shape=shapes.Circle(1),
                 cbb_radius=1.0,
                 flags=DEFAULT_FLAGS, **kwargs):

        super().__init__(pos, vel, flags=flags, **kwargs)

        # State variables
        self._theta = float(theta)
        self._omega = float(omega)
        self._alpha = 0.0

        # Collision and shapes
        self.base_shape = base_shape
        self.cbb_radius = cbb_radius
        self._shape = None

        # Makes mass, inertial and density consistent
        if density is not None:
            density = float(density)
            if mass is None:
                mass = density * self.area()
            else:
                mass = float(mass)
            if inertia is None:
                inertia = density * \
                          self.area() * self.ROG_sqr() / INERTIA_SCALE
            else:
                inertia = float(inertia)
        elif mass is not None:
            mass = float(mass)
            try:
                density = mass / self.area()
            except ZeroDivisionError:
                density = float('inf')
            if inertia is None:
                inertia = mass * self.ROG_sqr() / INERTIA_SCALE
            else:
                inertia = float(inertia)
        else:
            density = 1.0
            area = self.area()
            if area:
                mass = density * self.area()
                if inertia is None:
                    inertia = density * \
                              self.area() * self.ROG_sqr() / INERTIA_SCALE
                else:
                    inertia = float(inertia)
            else:
                mass = 1.0
                density = float('inf')
                inertia = 0.0

        self._invmass = safe_div(1.0, mass)
        self._invinertia = safe_div(1.0, inertia)
        self._density = float(density)

    def area(self):
        """
        Object surface area.
        """

        try:
            return self.base_shape.area()
        except AttributeError:
            return 0.0

    def ROG_sqr(self):
        """
        Radius of gyration.
        """

        try:
            return self.base_shape.ROG_sqr()
        except AttributeError:
            return float('inf')

    def ROG(self):
        """
        Radius of gyration.

        ROG is defined from the object's inertia:

        $inertia = mass * ROG^2$

        Subclasses must override ROG_sqr instead of this method.
        """

        return self._sqrt(self.ROG_sqr())

    # Physical properties
    def angularK(self):
        """
        Kinetic energy of angular movement.
        """

        if self._invinertia:
            return self._omega ** 2 / (2 * self._invinertia)
        else:
            return 0.0

    def energyK(self):
        """
        Total kinetic energy: sum of linearK and angularK.
        """

        return self.linearK() + self.angularK()

    def momentumL(self, *args):
        """
        Angular momentum.

        Angular momentum depends on a reference point. By default, we use the
        object's center of mass. One can pass any coordinate to specify the
        reference.

        Example:

            Consider the object

            >>> b1 = Body(pos=(0, 1), vel=(1, 0), mass=2)

            Its center of mass angualar momentum is zero since it has no angular
            velocity

            >>> b1.momentumL()
            0.0

            However, linear movement creates an angular moment around origin or
            other reference points

            >>> b1.momentumL(0, 0)
            -2.0
            >>> b1.momentumL(0, 2)
            2.0
        """

        if not args:
            momentumL = None
        else:
            if len(args) == 1:
                vec = args[0]
            else:
                vec = Vec2(*args)
            delta_pos = self.pos - vec
            momentumL = delta_pos.cross(self.momentumP())

        if self._invinertia:
            return momentumL + self.omega * self.inertia
        else:
            return momentumL

    def apply_force_at(self, force, pos, dt, method=None):
        """
        Apply force at the given point in space, by computing the resulting
        torques.
        """

        self.apply_force_at_relative(force, pos - self.pos, dt, method)

    def apply_force_at_relative(self, force, pos, dt, method=None):
        """
        Like .apply_force_at(), but treats pos as a relative to the center of
        mass.
        """

        self.apply_force(force, dt, method)

        if self.invinertia:
            self.apply_torque(pos.cross(force), dt, method)

    def apply_impulse_at(self, J, pos):
        """
        Apply linear and the corresponding angular impulses by applying an
        impulsive force at the given position.
        """

        self.apply_impulse_at_relative(J, pos - self.pos)

    def apply_impulse_at_relative(self, J, pos):
        """
        Like .apply_impulse_at(), but consider pos to be relative to the center
        of mass.
        """

        self.apply_impulse(J)
        if self.invinertia:
            self.apply_aimpulse(asvector(pos).cross(J))

    def rotate(self, theta):
        """
        Rotates object by an angle theta (rad).
        """

        self._theta += theta
        if theta != 0.0:
            self.flags |= flags.dirty_any

    def aboost(self, delta):
        """
        Shifts angular velocity.
        """

        self._omega += delta

    @accept_vec_args
    def vpoint(self, pos):
        """
        Return the linear velocity of a point at **absolute** position pos rigidly
        attached to the body.
        """

        return self.vpoint_relative(pos - self._pos)

    @accept_vec_args
    def vpoint_relative(self, pos):
        """
        Return the linear velocity of a point at position pos **relative** to
        the  center of mass.
        """

        if self._omega:
            return self._vel + pos.perp() * self._omega
        else:
            return self._vel

    def orientation(self, theta=0.0):
        """
        Return an unitary vector in the direction the object is oriented.

        If the rotation is zero, the orientation vector is Vec2(1, 0). Rotation
        is applied accordingly.
        """

        theta += self._theta
        return Vec2(self._cos(theta), self._sin(theta))

    def torque(self, t):
        """
        An external torque, analogous to the .force(t) method.
        """

        return 0.0

    def init_alpha(self):
        """
        Initialize the accumulated angular acceleration in the beginning of the
        frame.
        """

        self._alpha = - self._adamping * self._omega

    def apply_torque(self, torque, dt, method=None):
        """
        Apply some torque during the interval dt.

        This method has no effect in kinematic objects.
        """

        self.apply_alpha(torque * self._invinertia, dt)

    def apply_alpha(self, alpha, dt):
        """
        Apply angular acceleration alpha during interval dt.
        """

        if alpha is None:
            alpha = self._alpha
        self.aboost(alpha * dt)
        self.rotate(self._omega * dt + alpha * dt ** 2 / 2.)

    def apply_aimpulse(self, angular_delta):
        """
        Apply angular impulse to object.
        """

        self.aboost(angular_delta * self._invinertia)


class LinearRigidBody(Body):
    """
    A rigid body with infinite inertia.

    This is the subclass of all rigid bodies that do not support rotations.
    """

    __slots__ = ()
    DEFAULT_FLAGS = Body.DEFAULT_FLAGS & (flags.full ^ flags.can_rotate)

    @property
    def theta(self):
        return 0.0

    @theta.setter
    def theta(self, value):
        if value != 0.0:
            name = type(self).__name__
            raise ValueError('cannot set theta != 0 for %s' % name)

    _theta = theta

    @property
    def inertia(self):
        return INF

    @inertia.setter
    def inertia(self, value):
        if float(value) != INF:
            raise ValueError('LinearObjects have infinite inertia, '
                             'got %r' % value)

    def __init__(self, pos=(0, 0), vel=(0, 0),
                 mass=None, density=None, **kwargs):
        super(LinearRigidBody, self).__init__(
            pos, vel, 0.0, 0.0,
            mass=mass, density=density,
            inertia='inf',
            flags=self.DEFAULT_FLAGS, **kwargs
        )
