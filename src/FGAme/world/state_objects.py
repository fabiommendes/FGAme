import random

from FGAme import conf
from FGAme.mathtools import Vec2, pi, ux2D
from FGAme.utils import lazy


def _factory_pos_property(pos):
    """
    Factory of absolute position values.
    """
    a, b = pos

    def pos_prop(self):
        w, h = self._shape
        x0, y0 = self._origin
        return Vec2(x0 + a * w, y0 + b * h)

    pos_prop.terms = (a, b)

    return property(pos_prop)


def _factory_from_func(prop):
    """
    Factory of relative position values.
    """

    a, b = prop.fget.terms

    def from_pos(self, x, y):
        w, h = self._shape
        x0, y0 = self._origin
        return Vec2(x0 + a * w + x, y0 + b * h + y)

    return from_pos


def _speed_prop(name, scale, Vec):
    """
    Factory of velocity values.
    """

    def prop(self):
        return getattr(self, scale) * Vec

    prop.__name__ = name
    return property(prop)


class StateObject(object):
    """
    Base class for PosObject and VelObject.
    """

    @lazy
    def _globals(self):
        conf.init()
        self._globals = conf
        return self._globals

    @property
    def _shape(self):
        return self._globals.get_resolution()

    @property
    def _origin(self):
        return Vec2(0, 0)


class PosObject(StateObject):
    """
    Implements the global ``pos`` object in FGAme.
    """

    # Aligned
    middle, north, south, east, west = \
        map(_factory_pos_property,
            [(.5, .5), (.5, 1), (.5, 0), (1, .5), (0, .5)])

    # Relative displacements
    from_middle, from_north, from_south, from_east, from_west = \
        map(_factory_from_func, [middle, north, south, east, west])
    from_top, from_bottom, from_left, from_right = \
        map(_factory_from_func, [north, south, west, east])

    # Diagonals
    sw, se, ne, nw = \
        map(_factory_pos_property, [(0, 0), (1, 0), (1, 1), (0, 1)])
    south_west, sout_east, north_east, nort_west = sw, se, ne, nw

    # Diagonals (relative displacements)
    from_sw, from_se, from_ne, from_nw = \
        map(_factory_from_func, [sw, se, ne, nw])
    from_south_west, from_south_east, from_north_east, from_north_west = \
        from_sw, from_se, from_ne, from_nw

    def random(self, *args):
        """
        Return random position in the visible screen.

        Signature:
            ``pos.random(size)``: create objects within screen and inside a
                margin with the given number of pixels.
            ``pos.random(margin_x, margin_y)``: specify margin in x and y
                directions.
            ``pos.random(margin_left, margin_bottom, margin_right, margin_top)``:
                specify each margin separately
        """

        x0 = y0 = 0
        x1, y1 = self._shape
        if len(args) == 1:
            margin = args[0]
            x0 += margin
            x1 -= margin
            y0 += margin
            y1 -= margin
        elif len(args) == 2:
            dx, dy = args
            x0 += dx
            x1 -= dx
            y0 += dy
            y1 -= dy
        elif len(args) == 4:
            x0 += args[0]
            y0 += args[1]
            x1 -= args[2]
            y1 -= args[3]
        elif len(args) != 0:
            raise TypeError('must be called with 0, 1, 2, or 4 arguments')

        return Vec2(random.uniform(x0, x1), random.uniform(y0, y1)) + self._origin


class VelObject(StateObject):
    """
    Implements global ``vel`` object.
    """

    def __init__(self):
        self._fast = 600
        self._fair = 300
        self._slow = 150

    def set_speeds(self, slow, fair, fast):
        """
        Set the reference speeds for slow, fair and fast values.
        """

        if slow <= fair <= fast:
            self.set_slow(slow)
            self.set_fair(fair)
            self.set_fast(fast)

    def set_fast(self, value):
        """
        Defines the *fast* speed value.
        """

        self._fast = value

    def set_fair(self, value):
        """
        Defines the *fair* speed value.
        """

        self._fair = value

    def set_slow(self, value):
        """
        Defines the *slow* speed value.
        """

        self._slow = value

    @property
    def speed_fast(self):
        return self._fast

    @property
    def speed_slow(self):
        return self._slow

    @property
    def speed_fair(self):
        return self._fair

    def _random(self, scale, angle):
        return scale * ux2D.rotate(random.uniform(0, 2 * pi))

    def random(self, angle=None):
        """
        A random fair velocity.
        """

        return self._random(self._fair, angle)

    def random_fast(self, angle=None):
        """
        A random fast velocity.
        """

        return self._random(self._fast, angle)

    def random_slow(self, angle=None):
        """
        A random slow velocity.
        """

        return self._random(self._slow, angle)


_speeds = dict(
    up=Vec2(0, 1),
    down=Vec2(0, -1),
    right=Vec2(1, 0),
    left=Vec2(-1, 0),
    ne=Vec2(1, 1).normalize(),
    nw=Vec2(-1, 1).normalize(),
    se=Vec2(1, -1).normalize(),
    sw=Vec2(-1, -1).normalize(),
)


for name, Vec in _speeds.items():
    setattr(VelObject, name, _speed_prop(name, 'fair', Vec))
    setattr(VelObject, name, _speed_prop('%s_fast' % name, 'fast', Vec))
    setattr(VelObject, name, _speed_prop('%s_slow' % name, 'slow', Vec))
