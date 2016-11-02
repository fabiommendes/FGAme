import functools

from FGAme import objects, conf


def auto_add(func):
    """
    Creates object with func() and add it to the world.
    """

    @functools.wraps(func)
    def auto_add_decorated(self, *args, **kwargs):
        obj = func(self, *args, **kwargs)
        self._world.add(obj)
        return obj

    return auto_add_decorated


class ObjectFactory:
    """
    Methods create special objects in the world.
    """

    def __init__(self, world):
        self._world = world

    def __add(self, obj):
        self._world._add(obj)

    def __call__(self, *args, **kwargs):
        return self._world._add(*args, **kwargs)

    # Object creators
    @auto_add
    def aabb(self, *args, **kwargs):
        """
        Create a new AABB.
        """

        return objects.AABB(*args, **kwargs)

    @auto_add
    def circle(self, *args, **kwargs):
        """
        Create a new circle.
        """

        return objects.Circle(*args, **kwargs)

    @auto_add
    def poly(self, *args, **kwargs):
        """
        Create a new polygon.
        """

        return objects.Poly(*args, **kwargs)

    @auto_add
    def regular_poly(self, *args, **kwargs):
        """
        Create a new regular polygon.
        """

        return objects.RegularPoly(*args, **kwargs)

    @auto_add
    def triangle(self, *args, **kwargs):
        """
        Create a new triangle.
        """

        return objects.Triangle(*args, **kwargs)

    @auto_add
    def rectangle(self, *args, **kwargs):
        """
        Create a new rectangle.
        """

        return objects.Rectangle(*args, **kwargs)

    # Special objects
    def aabb_margin(self, *args, width=500, **kwargs):
        """
        Creates four AABBs that encloses the visible area.

        It accepts a few different signatures:

        aabb_margin(width):
            Creates a margin around screen with the given width in pixels.
            Width can be positive or negative (for a margin outside the visible
            area of the screen.
        aabb_margin(width_x, width_y):
            Set different widths in the x and y directions.
        aabb_margin(width_left, width_bottom, width_right, width_top):
            Set width in each direction to a different value.
        """

        W, H = conf.get_resolution()
        N = len(args)
        if N == 0:
            dx = dy = dx_ = dy_ = 0
        elif N == 1:
            dx = dy = dx_ = dy_ = args[0]
        elif N == 2:
            dx, dy = args
            dx_, dy_ = dx, dy
        elif N == 4:
            dx, dy, dx_, dy_ = args
        else:
            raise ValueError('width can have 1, 2 or 4 values')

        xmin, xmax = dx, W - dx_
        ymin, ymax = dy, H - dy_
        maker = objects.AABB
        width = width
        up = maker((xmin - width, xmax + width, ymax, ymax + width), **kwargs)
        down = maker((xmin - width, xmax + width, ymin - width, ymin), **kwargs)
        left = maker((xmin - width, xmin, ymin, ymax), **kwargs)
        right = maker((xmax, xmax + width, ymin, ymax), **kwargs)

        for box in [up, down, left, right]:
            box.make_static()

        self.__add([up, down, left, right])
        return left, right, up, down

    def margin(self, *args, **kwargs):
        """
        Alias to *aabb_margin.**

        In the future this will be implemented using infinite lines.
        """

        return self.aabb_margin(*args, **kwargs)
