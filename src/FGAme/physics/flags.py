from itertools import count


class PhysicsFlags:
    N = count()

    # Dynamic state
    is_active = 1 << next(N)
    is_dynamic = 1 << next(N)
    is_kinematic = 1 << next(N)
    is_static = 1 << next(N)
    is_shape = 1 << next(N)
    is_sensor = 1 << next(N)
    is_sleeping = 1 << next(N)
    can_sleep = 1 << next(N)
    can_rotate = 1 << next(N)

    # External forces
    owns_gravity = 1 << next(N)
    owns_damping = 1 << next(N)
    owns_adamping = 1 << next(N)
    owns_restitution = 1 << next(N)
    owns_friction = 1 << next(N)

    # Contacts and joints
    has_joints = 1 << next(N)
    has_contacts = 1 << next(N)
    has_external_force = 1 << next(N)
    has_external_accel = 1 << next(N)
    has_external_torque = 1 << next(N)
    has_external_alpha = 1 << next(N)

    # Temporary state
    dirty_shape = 1 << next(N)
    dirty_aabb = 1 << next(N)

    # Visualization
    has_visualization = 1 << next(N)
    has_simple_visualization = 1 << next(N)
    has_solid_color = 1 << next(N)
    has_line_color = 1 << next(N)

    num_bits = next(N)
    full = (1 << num_bits) - 1
    del N

    # Derived flags
    dirty_any = dirty_shape | dirty_aabb
    not_dirty = full ^ dirty_any


flags = PhysicsFlags()
