from FGAme.mathtools import null2D, shapes, shadow_x, shadow_y, uy2D, ux2D, Vec2
from FGAme.physics.bodies import Body, AABB
from FGAme.physics.collision import get_collision, Collision


class Circle(Body):
    """
    Object with a circular bounding box.

    Examples:
        Circle instances are initialized by passing a radius and any optional
        Body parameters.

        >>> c1 = Circle(10, pos=(10, 0))     # radius 10 and center at (10, 10)
        >>> c2 = Circle(10, density=2)       # radius 10 in the origin
        >>> c2.area()
        314.1592653589793
    """

    __slots__ = ()

    @property
    def radius(self):
        return self.cbb_radius

    def rescale(self, scale, update_physics=False):
        self.cbb_radius *= scale
        super(Circle, self).rescale(scale, update_physics)

    @property
    def bb(self):
        return self.cbb

    @property
    def xmin(self):
        return self._pos.x - self.cbb_radius

    @property
    def xmax(self):
        return self._pos.x + self.cbb_radius

    @property
    def ymin(self):
        return self._pos.y - self.cbb_radius

    @property
    def ymax(self):
        return self._pos.y + self.cbb_radius

    def __init__(self, radius, pos=(0, 0), vel=(0, 0), **kwds):
        radius = float(radius)
        super(Circle, self).__init__(
            pos, vel,
            base_shape=shapes.Circle(radius, null2D),
            cbb_radius=radius,
            **kwds
        )

    def __repr__(self):
        tname = type(self).__name__
        vel = ', '.join('%.1f' % x for x in self._vel)
        pos = ', '.join('%.1f' % x for x in self._pos)
        return '%s(pos=(%s), vel=(%s), radius=%.1f)' % (
            tname, pos, vel, self.radius)


@get_collision.overload([Circle, Circle])
def collision_circle(A, B, collision_class=Collision):
    """
    Circle-to-circle collision.
    """

    rA = A.radius
    rB = B.radius
    normal = B.pos - A.pos
    distance = normal.norm()

    if distance < rA + rB:
        normal /= distance
        delta = rA + rB - distance
        pos = A.pos + (rA - delta / 2) * normal
        col = collision_class(A, B, pos=pos, normal=normal, delta=delta)
        return col
    else:
        return None


@get_collision.overload([Circle, AABB])
def circle_aabb(A, B, collision_class=Collision):
    cx, cx_, cy, cy_ = A.rect_coords
    ax, ax_, ay, ay_ = B.rect_coords
    dx = min(cx_, ax_) - max(cx, ax)
    dy = min(cy_, ay_) - max(cy, ay)
    if dy < 0 or dx < 0:
        return None

    x, y = pos = A.pos
    if dx < dy:
        # Circle is right at the bottom/top of AABB
        if ay <= y <= ay_:
            left = x < ax
            pos = Vec2(ax if left else ax_, y)
            normal = Vec2(1 if left else -1, 0)
            delta = dx / 2
            return collision_class(A, B, pos=pos, normal=normal, delta=delta)
    else:
        # Circle is right at the bottom/top of AABB
        if ax <= x <= ax_:
            bottom = y < ay
            pos = Vec2(x, ay if bottom else ay_)
            normal = Vec2(0, 1 if bottom else -1)
            delta = dy / 2
            return collision_class(A, B, pos=pos, normal=normal, delta=delta)

    # If we reached this point, the circle encountered the AABB at a vertex.
    # We must find the vertex that is closest to the center and define the
    # normal vector using it.
    vertex = min(B.vertices, key=lambda v: abs(v - pos))
    normal = (vertex - pos).normalize()
    delta = A.radius - (pos - vertex).norm()
    return collision_class(A, B, pos=vertex, normal=normal, delta=delta)


@get_collision.overload([AABB, Circle])
def aabb_circle(A, B, collision_class=Collision):
    col = circle_aabb(B, A, collision_class=collision_class)
    if col is not None:
        return col.swap()