from FGAme.mathtools import sqrt, shapes, Vec2
from FGAme.physics.bodies.body import LinearRigidBody
from FGAme.physics.collision import get_collision, Collision


class AABB(LinearRigidBody):
    """
    Axis Aligned Bounding Box: represents an irrotational rectangle.

    Usage:
        AABBs can be initialized in many different ways.

        Perhaps the most common way is to give the coordinates xmin, xmax, ymin,
        ymax of the bounding box::

        >>> A = AABB(-50, 50, -100, 100)

        We can also provide the shape and center position::

        >>> B = AABB(shape=(100, 200))
        >>> B.rect_coords # (xmin, xmax, ymin, ymax)
        (-50.0, 50.0, -100.0, 100.0)

        A second option is to define the rect tuple, i.e., (xmin, ymin, width,
        height), with the coordinates of the bottom-left point together with the
        shape::

        >>> C = AABB(rect=(-50, 50, 100, 200))
        >>> C.rect_coords
        (-50.0, 50.0, -100.0, 100.0)

        In all cases, the mass is computed automatically from the area assuming
        a density of 1.0. Rotational inertia is infinite since the object does
        not have any rotational dynamics::

        >>> A.mass, A.inertia  # 20.000 == 200 x 100
        (20000.0, inf)

    """

    __slots__ = ()

    @property
    def aabb(self):
        return self.bb

    @property
    def xmin(self):
        return self._pos.x - self._delta_x

    @property
    def xmax(self):
        return self._pos.x + self._delta_x

    @property
    def ymin(self):
        return self._pos.y - self._delta_y

    @property
    def ymax(self):
        return self._pos.y + self._delta_y

    @property
    def vertices(self):
        return self.bb.vertices

    def __init__(self, xmin=None, xmax=None, ymin=None, ymax=None,
                 pos=None, vel=(0, 0), shape=None, rect=None, **kwds):
        xmin, xmax, ymin, ymax = shapes.aabb_coords(
            xmin, xmax, ymin, ymax,
            rect=rect, shape=shape, pos=pos
        )

        pos = (xmin + xmax) / 2., (ymin + ymax) / 2.
        self._delta_x = dx = (xmax - xmin) / 2
        self._delta_y = dy = (ymax - ymin) / 2
        aabb = shapes.AABB(-dx, dx, -dy, dy)
        super(AABB, self).__init__(pos, vel,
                                   base_shape=aabb,
                                   cbb_radius=sqrt(dx ** 2 + dy ** 2), **kwds)

    def __repr__(self):
        tname = type(self).__name__
        if not self._invmass:
            tname += '*'
        vel = ', '.join('%.1f' % x for x in self._vel)
        data = ', '.join('%.1f' % x for x in self.rect_coords)
        return '%s(%s, vel=(%s))' % (tname, data, vel)

    def area(self):
        return 4 * self._delta_x * self._delta_y

    def ROG_sqr(self):
        a = self._delta_x
        b = self._delta_y
        return (a ** 2 + b ** 2) / 3


@get_collision.overload([AABB, AABB])
def collision_aabb(A, B):
    # Detects collision using bounding box shadows.
    x0, x1 = max(A.xmin, B.xmin), min(A.xmax, B.xmax)
    y0, y1 = max(A.ymin, B.ymin), min(A.ymax, B.ymax)
    dx = x1 - x0
    dy = y1 - y0
    if x1 < x0 or y1 < y0:
        return None

    # Chose collision center as the center point in the intersection
    pos = Vec2((x1 + x0) / 2, (y1 + y0) / 2)

    # Normal is the direction with smallest penetration
    if dy < dx:
        delta = dy
        normal = Vec2(0, (1 if A.pos.y < B.pos.y else -1))
    else:
        delta = dx
        normal = Vec2((1 if A.pos.x < B.pos.x else -1), 0)

    return Collision(A, B, pos=pos, normal=normal, delta=delta)
