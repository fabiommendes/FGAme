from FGAme.mathtools import Vec2, sin, pi, shapes, shadow_y, \
    shadow_x
from FGAme.physics.bodies import Body, AABB, Circle
from FGAme.physics.collision import get_collision, Collision, DEFAULT_DIRECTIONS
from smallshapes import aabb_coords
from smallshapes import area, clip, center_of_mass, ROG_sqr
from smallvectors import dot, Rotation2d


class Poly(Body):
    """
    N-sided polygon.
    """

    __slots__ = ('_vertices', 'num_sides', '_normals_idxs', 'num_normals')

    @property
    def bb(self):
        return shapes.Poly(self.vertices)

    @property
    def vertices(self):
        pos = self._pos
        return [v + pos for v in self._rvertices]

    @property
    def _rvertices(self):
        if self._theta == self._cache_theta:
            return self._cache_rvertices_last
        else:
            r = Rotation2d(self._theta)
            vert = [r * v for v in self._vertices]
            xmin = min(v.x for v in vert)
            xmax = max(v.x for v in vert)
            ymin = min(v.y for v in vert)
            ymax = max(v.y for v in vert)
            bbox = (xmin, xmax, ymin, ymax)

            self._cache_rvertices_last = vert
            self._cache_theta = self._theta
            self._cache_rbbox_last = bbox

            return vert

    @property
    def _rbbox(self):
        if self._theta == self._cache_theta:
            return self._cache_rbbox_last
        else:
            self._rvertices
            return self._cache_rbbox_last

    @property
    def xmin(self):
        return self._pos.x + self._rbbox[0]

    @property
    def xmax(self):
        return self._pos.x + self._rbbox[1]

    @property
    def ymin(self):
        return self._pos.y + self._rbbox[2]

    @property
    def ymax(self):
        return self._pos.y + + self._rbbox[3]

    @property
    def shape_bb(self):
        return shapes.Poly(self.vertices)

    def __init__(self,
                 vertices,
                 pos=None, vel=(0, 0), theta=0.0, omega=0.0,
                 mass=None, density=None, inertia=None, **kwargs):

        if isinstance(vertices, int):
            raise ValueError('must pass a list of vertices. '
                             'Use RegularPoly to define a polygon by the '
                             'number of vertices')
        vertices = [Vec2(*pt) for pt in vertices]
        pos_cm = center_of_mass(vertices)
        vertices = [v - pos_cm for v in vertices]
        self._vertices = vertices

        # Cache vertices
        self._cache_theta = None
        self._cache_rvertices_last = None
        self._cache_rbbox_last = None
        super(Poly, self).__init__(pos_cm, vel, theta, omega,
                                   mass=mass, density=density, inertia=inertia,
                                   cbb_radius=max(v.norm() for v in vertices),
                                   **kwargs)

        self.num_sides = len(vertices)
        self._normals_idxs = self.get_li_indexes()
        self.num_normals = len(self._normals_idxs or self.vertices)

        # Slightly faster when all normals are linear dependent: if
        # self._normals_idx = None, all normals are recomputed at each frame.
        if self.num_normals == self.num_sides:
            self._normals_idxs = None

        # Move to specified position, if pos is given.
        if pos is not None:
            self._pos = Vec2(*pos)

    def scale(self, scale, update_physics=False):
        self._vertices = [scale * v for v in self._vertices]

    def area(self):
        return area(self._vertices)

    def ROG_sqr(self):
        return ROG_sqr(self._vertices)

    def get_li_indexes(self):
        """
        Return indexes of all linearly independent normals.
        """

        normals = [self.get_normal(i).normalize()
                   for i in range(self.num_sides)]
        LI = []
        LI_idx = []
        for idx, n in enumerate(normals):
            for n_other in LI:
                # Null cross product ==> linear dependency
                if abs(n.cross(n_other)) < 1e-3:
                    break
            else:
                # For do not ending implies linear independence
                LI.append(n)
                LI_idx.append(idx)
        return LI_idx

    def get_side(self, i):
        """
        Return a vector with the same direction as the ith side.

        Each segment goes from point i to i + 1.
        """

        points = self.vertices
        return points[(i + 1) % self.num_sides] - points[i]

    def get_normal(self, i):
        """
        Normal unity vector to the ith side.

        Each segment goes from point i to i + 1.
        """

        points = self.vertices
        x, y = points[(i + 1) % self.num_sides] - points[i]
        return Vec2(y, -x).normalize()

    def get_normals(self):
        """
        List of linearly independent normals.
        """

        if self._normals_idxs is None:
            N = self.num_sides
            points = self.vertices
            segmentos = (points[(i + 1) % N] - points[i] for i in range(N))
            return [Vec2(y, -x).normalize() for (x, y) in segmentos]
        else:
            return [self.get_normal(i) for i in self._normals_idxs]

    def is_internal_point(self, pt):
        """
        True, if point is inside polygon.
        """

        n = self.get_normal
        P = self.vertices
        return all((pt - P[i]).dot(n(i)) <= 0 for i in range(self.num_sides))


class RegularPoly(Poly):
    """
    Regular polygon with ``N`` sides with given ``length``.
    """

    __slots__ = ('length',)

    def __init__(self, N, length,
                 pos=(0, 0), vel=(0, 0), theta=0.0, omega=0.0,
                 **kwargs):
        self.length = float(length)
        vertices = self._vertices(int(N), pos)
        super(RegularPoly, self).__init__(vertices, None, vel, theta, omega,
                                          **kwargs)

    def _vertices(self, N, pos):
        length = self.length
        alpha = pi / N
        theta = 2 * alpha
        b = length / (2 * sin(alpha))
        P0 = Vec2(b, 0)
        pos = Vec2(*pos)
        return [(P0.rotate(n * theta)) + pos for n in range(N)]


class Rectangle(Poly):
    """
    A rotational version of an AABB.

    Example:
        >>> r = Rectangle(shape=(200, 100))
        >>> r.rotate(pi/4)
        >>> r.rect_coords                                   # doctest: +ELLIPSIS
        (-106.066..., 106.066..., -106.066..., 106.066...)
    """

    __slots__ = ()

    def __init__(self, xmin=None, xmax=None, ymin=None, ymax=None,
                 pos=None, vel=(0, 0), theta=0.0, omega=0.0,
                 rect=None, shape=None, **kwargs):
        xmin, xmax, ymin, ymax = aabb_coords(xmin, ymin, xmax, ymax,
                                             rect=rect, shape=shape, pos=pos)

        super(Rectangle, self).__init__(
            [(xmax, ymin), (xmax, ymax), (xmin, ymax), (xmin, ymin)],
            None, vel, theta, omega, **kwargs)


@get_collision.overload([Poly, Poly])
def collision_poly(A, B, directions=None, collision_class=Collision):
    """
    Collision detection using SAT.
    """

    # List of directions from normals
    if directions is None:
        if A.num_normals + B.num_normals < 9:
            directions = A.get_normals() + B.get_normals()
        else:
            directions = DEFAULT_DIRECTIONS

    # Test overlap in all considered directions and picks the smaller
    # penetration
    min_overlap = float('inf')
    norm = None
    for u in directions:
        A_coords = [dot(pt, u) for pt in A.vertices]
        B_coords = [dot(pt, u) for pt in B.vertices]
        Amax, Amin = max(A_coords), min(A_coords)
        Bmax, Bmin = max(B_coords), min(B_coords)
        minmax, maxmin = min(Amax, Bmax), max(Amin, Bmin)
        overlap = minmax - maxmin
        if overlap < 0:
            return None
        elif overlap < min_overlap:
            min_overlap = overlap
            norm = u

    # Finds the correct direction for the normal
    if dot(A.pos, norm) > dot(B.pos, norm):
        norm = -norm

    # Computes the clipped polygon: collision happens at its center point.
    try:
        clipped = clip(A.vertices, B.vertices)
        col_pt = center_of_mass(clipped)
    except ValueError:
        return None

    if area(clipped) == 0:
        return None

    return collision_class(A, B, pos=col_pt, normal=norm, delta=min_overlap)


@get_collision.overload([AABB, Poly])
def aabb_poly(A, B, collision_class=Collision):
    if shadow_x(A, B) < 0 or shadow_y(A, B) < 0:
        return None

    A_poly = Rectangle(A.rect_coords)
    col = collision_poly(A_poly, B)
    if col is not None:
        return collision_class(A, B, pos=col.pos, normal=col.normal,
                               delta=col.delta)
    else:
        return None


@get_collision.overload([Circle, Poly])
def circle_poly(A, B, collision_class=Collision):
    if shadow_x(A, B) < 0 or shadow_y(A, B) < 0:
        return None

    # Searches for the nearest point to B
    vertices = B.vertices
    center = A.pos
    normals = [(i, v - center, v) for i, v in enumerate(vertices)]
    idx, _, pos = min(normals, key=lambda x: x[1].norm())

    # The smaller distance to the center can be vertex-center or side-center.
    # We need to detect this.
    separation = (pos - center).norm()

    # Verify each face
    P0 = pos
    N = len(vertices)
    for idx in [(idx - 1) % N, (idx + 1) % N]:
        P = vertices[idx]
        v = center - P
        u = P0 - P
        L = u.norm()
        distance = abs(v.cross(u) / L)

        # Verify if closest point is inside segment
        if distance < separation and u.dot(v) < L ** 2:
            pos = P + (u.dot(v) / L ** 2) * u
            separation = distance

    # Verify if there is collision in the direction of smaller separation
    delta = A.radius - separation
    normal = (pos - center).normalize()

    if delta > 0:
        return collision_class(A, B, pos=pos, normal=normal, delta=delta)
    else:
        return None


@get_collision.overload([Poly, Circle])
def poly_circle(A, B, collision_class=Collision):
    return circle_poly(B, A, collision_class=Collision)


@get_collision.overload([Poly, AABB])
def poly_aabb(A, B, collision_class=Collision):
    return aabb_poly(B, A, collision_class=Collision)
