from collections import defaultdict

from FGAme.mathtools import Vec2, null2D
from FGAme.physics import flags
from FGAme.physics.broadphase import BroadPhase, BroadPhaseCBB, NarrowPhase
from FGAme.physics.signals import object_removed_signal, \
    gravity_changed_signal, damping_changed_signal, adamping_changed_signal, \
    friction_changed_signal, restitution_changed_signal


class Simulation:
    """
    Coordinate physical objects, compute forces, collisions, constrains and
    solve their time evolution.
    """

    # Physical properties and global forces
    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value):
        owns_prop = flags.owns_gravity
        old = self._gravity
        try:
            gravity = self._gravity = Vec2(*value)
        except TypeError:
            gravity = self._gravity = Vec2(0, -value)

        for obj in self._objects:
            if not obj.flags & owns_prop:
                obj._gravity = gravity
                gravity_changed_signal.trigger(self, old, self._gravity)

    @property
    def damping(self):
        return self._damping

    @damping.setter
    def damping(self, value):
        owns_prop = flags.owns_damping
        old = self._damping
        value = self._damping = float(value)

        for obj in self._objects:
            if not obj.flags & owns_prop:
                obj._damping = value
                damping_changed_signal.trigger(self, old, self._damping)

    @property
    def adamping(self):
        return self._adamping

    @adamping.setter
    def adamping(self, value):
        owns_prop = flags.owns_adamping
        old = self._adamping
        value = self._adamping = float(value)

        for obj in self._objects:
            if not obj.flags & owns_prop:
                obj._adamping = value
                adamping_changed_signal.trigger(self, old, self._adamping)

    @property
    def restitution(self):
        return self._restitution

    @restitution.setter
    def restitution(self, value):
        owns_prop = flags.owns_restitution
        old = self._restitution
        value = self._restitution = float(value)

        for obj in self._objects:
            if not obj.flags & owns_prop:
                obj._restitution = value
                restitution_changed_signal.trigger(self, old, self._restitution)

    @property
    def friction(self):
        return self._friction

    @friction.setter
    def friction(self, value):
        owns_prop = flags.owns_friction
        old = self._friction
        value = self._friction = float(value)

        for obj in self._objects:
            if not obj.flags & owns_prop:
                obj._friction = value
                friction_changed_signal.trigger(self, old, self._friction)

    def __init__(self,
                 gravity=None,
                 damping=0, adamping=0,
                 restitution=1, friction=0,
                 sleep_speed=3, sleep_angular_speed=0.05, max_speed=None,
                 bounds=None, broad_phase=None,
                 niter=5, beta=0.0,
                 collision_check=None):

        super(Simulation, self).__init__()

        # Objects and constraints
        self._objects = []
        self._constraints = []
        self._contacts = []
        self._active = []
        self._inactive = []

        # Solver parameters
        self.niter = niter
        self.beta = beta
        self.sleep_speed = sleep_speed
        self.sleep_angular_speed = sleep_angular_speed

        # Collision detection algorithms
        self.collision_check = collision_check or can_collide
        self.broad_phase = normalize_broad_phase(broad_phase, self)
        self.narrow_phase = NarrowPhase(simulation=self)

        # Global forces and physical parameters
        self._kinetic0 = None
        self._potential0 = None
        self._interaction0 = None
        self._gravity = null2D
        self._damping = self._adamping = self._friction = 0
        self._restitution = 1
        self.gravity = gravity or (0, 0)
        self.damping = damping
        self.adamping = adamping
        self.restitution = restitution
        self.friction = friction
        self.max_speed = max_speed

        # Bounds
        self.bounds = bounds
        self._out_of_bounds = set()

        # Simulation steps
        self.num_steps = 0
        self.time = 0

    def __iter__(self):
        return iter(self._objects)

    def __contains__(self, obj):
        return obj in self._objects

    # Objects and collisions
    def add(self, obj):
        """
        Adds new physical object to the simulation.
        """

        if obj not in self._objects:
            self._objects.append(obj)
            self._active.append(obj)
            obj.set_simulation(self)

    def remove(self, obj):
        """
        Remove object from simulation.

        Raises ValueError() of object is not present in the simulation.
        """

        try:
            idx = self._objects.index(obj)
        except IndexError:
            raise ValueError('object not present')
        else:
            del self._objects[idx]
            for L in self._active, self._inactive:
                try:
                    L.remove(obj)
                except ValueError:
                    pass
            object_removed_signal.trigger(self, obj)

        obj._simulation = None

    def discard(self, obj):
        """
        Discard object, if present.
        """

        try:
            self.remove(obj)
        except ValueError:
            pass

    # Simulation
    def update(self, dt):
        """
        Main iteration step.
        """

        # self.trigger_frame_enter()
        self._dt = dt = float(dt)
        if self._kinetic0 is None:
            self._init_energy0()

        # Generic loop
        self.accumulate_accelerations(dt)
        self.resolve_velocities(dt)
        self.resolve_constraints(dt)  # Collision is a constraint!
        self.resolve_positions(dt)

        # We alternate a few checks every two frames to conserve CPU.
        if self.num_steps % 2 == 0:
            self.find_out_of_bounds()
        elif self.num_steps % 2 == 1:
            self.enforce_max_speed()

        # Increase time and counter
        self.time += dt
        self.num_steps += 1

    def accumulate_accelerations(self, dt):
        """
        Update the acceleration state due to external forces and torques for all
        objects in the simulation.
        """

        IS_SLEEP = flags.is_sleeping
        t = self.time

        # Accumulate accelerations
        for obj in self._active:
            if obj.flags & IS_SLEEP:
                continue

            if obj._invmass:
                obj.init_accel()
                if obj.force is not None:
                    obj._acceleration += obj.force(t) * obj._invmass

            # elif obj.flags & ACCEL_STATIC:
            #    obj.init_accel()
            #    obj.apply_accel(obj._accel, dt)

            if obj._invinertia:
                obj.init_alpha()
                if obj.torque is not None:
                    obj._alpha += obj.torque(t) * obj._invinertia

                    # elif obj.flags & ALPHA_STATIC:
                    #    obj.init_alpha()
                    #    obj.apply_alpha(self._alpha, dt)

    def resolve_velocities(self, dt):
        """
        Update velocities from computed accelerations.
        """

        IS_SLEEP = flags.is_sleeping
        for obj in self._objects:
            if obj.flags & IS_SLEEP:
                continue

            if obj.invmass:
                obj.boost(obj._acceleration * dt)
            if obj.invinertia:
                obj.aboost(obj._alpha * dt)

            obj._e_vel = null2D
            obj._e_omega = 0.0

    def resolve_positions(self, dt):
        """
        Resolve positions and angles from the current velocities.
        """

        IS_SLEEP = flags.is_sleeping
        for obj in self._objects:
            if obj.flags & IS_SLEEP:
                continue
            obj.move((obj.vel + obj._e_vel) * dt)
            obj.rotate((obj.omega + obj._e_omega) * dt)

    def resolve_constraints(self, dt):
        """
        Resolve all constraints (including collisions) using sequential
        impulses.
        """

        broad_cols = self.broad_phase(self._objects)
        narrow_cols = self.narrow_phase(broad_cols)

        # Resolve collisions
        for col in narrow_cols:
            col.pre_collision(self)
            if col.active:
                col.resolve()

        # Baumgarte stabilization
        beta = self.beta
        for col in narrow_cols:
            if col.active:
                col.baumgarte(beta)

        # Post-collision signal
        for col in narrow_cols:
            if col.active:
                col.post_collision(self)

    def get_islands(self, contacts):
        """
        Return list of closed collision groups in the collision graph.
        """

        contacts = set(contacts)
        groups = defaultdict(list)
        while contacts:
            A, B = C = contacts.pop()
            gA = groups[A]
            gB = groups[B]
            if gA is not gB:
                gA.extend(gB)
                groups[B] = gA
            gA.append(C)
        return list(groups.values())

    # Physical parameters
    def energyK(self):
        """
        Total kinetic energy.
        """

        return sum(obj.energyK() for obj in self._objects
                   if (obj._invmass or obj._invinertia))

    def energyU(self):
        """
        Potential energy associated with single object contributions.
        """

        return sum(obj.energyU() for obj in self._objects if obj._invmass)

    def energy_interaction(self):
        """
        Potential energy due to interactions between objects.
        """

        return 0.0

    def energyT(self):
        """
        Total energy.
        """

        return self.energyU() + self.energyK() + self.energy_interaction()

    def energy_ratio(self):
        """
        Ratio between total energy now and in the beginning of simulation.

        In conservative systems this ratio should be one.
        """

        if self._kinetic0 is None:
            self._init_energy0()
            return 1.0
        sum_energies = self._kinetic0 + self._potential0 + self._interaction0
        return self.energyT() / sum_energies

    def _init_energy0(self):
        """
        Init _kinetic0 and friends.
        """

        self._kinetic0 = self.energyK()
        self._potential0 = self.energyU()
        self._interaction0 = self.energy_interaction()

    # Sporadic checks
    def enforce_max_speed(self):
        """
        Makes sure objects have a maximum velocity.
        """

        if self.max_speed is not None:
            vel = self.max_speed
            vel_sqr = self.max_speed ** 2

            for obj in self._objects:
                if obj._vel.norm_sqr() > vel_sqr:
                    obj._vel *= vel / obj._vel.norm()

    def find_out_of_bounds(self):
        """
        Triggers an 'out-of-margin' signal when object leaves the simulation.
        """

        if self.bounds is not None:
            xmin, xmax, ymin, ymax = self.bounds
            out = self._out_of_bounds

            for obj in self._objects:
                x, y = obj._pos
                is_out = True

                if x > xmax and obj.xmin > xmax:
                    direction = 0
                elif y > ymax and obj.ymin > ymax:
                    direction = 1
                elif x < xmin and obj.xmax < xmin:
                    direction = 2
                elif y < ymin and obj.ymax < ymin:
                    direction = 3
                else:
                    is_out = False

                if is_out and obj not in out:
                    out.add(obj)
                    obj.trigger_out_of_bounds(direction)
                else:
                    out.discard(obj)

    def burn(self, frames, dt=0.0):
        """
        Executes simulation for a given number of frames without updating time.
        """

        time = self.time
        for _ in range(frames):
            self.update(dt)
            self.time = time

    def remove_superpositions(self, num_iter=1):
        """
        Tries to remove superpositions between objects.

        Static objects are never affected.
        """

        self._dt = 0.0
        for _ in range(num_iter):
            self.broad_phase()
            self.fine_phase()

            for col in self._fine_collisions:
                col.adjust_overlap()


def normalize_broad_phase(broad_phase, simulation):
    if broad_phase is None:
        broad_phase = BroadPhaseCBB(simulation=simulation)
    elif isinstance(broad_phase, BroadPhase):
        if broad_phase.simulation not in [None, simulation]:
            raise ValueError('BroadPhase object has a world attatched')
        else:
            broad_phase.simulation = simulation
    elif isinstance(broad_phase, type) and issubclass(broad_phase, BroadPhase):
        broad_phase = broad_phase(simulation=simulation)
    else:
        raise TypeError('invalid broad phase object')
    return broad_phase


def can_collide(A, B):
    """
    Return True if A and B can collide.
    """

    # Check if A and B are kinematic
    if ((not A._invmass or A.flags & flags.is_sleeping) and
            (not B._invmass or B.flags & flags.is_sleeping)):
        return False

    # Check if both are in the same collision layer
    elif ((A._col_layer_mask != B._col_layer_mask)
          and not (A._col_layer_mask & B._col_layer_mask)):
        return False

    # Check if both are in the same collision group
    elif A._col_group_mask & B._col_group_mask:
        return False

    return True
