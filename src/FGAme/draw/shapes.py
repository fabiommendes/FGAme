import smallshapes.core.shape
import smallshapes.core.solid
from FGAme.draw import Color
from FGAme.draw.base import Drawable
from FGAme.mathtools import shapes

black = Color('black')
white = Color('white')


class Shape(smallshapes.core.shape.mShape, Drawable):
    """
    Base class for all objects that define an open curve.
    """

    __slots__ = ()
    _slots = ('_linewidth', '_linecolor') + Drawable._slots

    @property
    def linecolor(self):
        return self._linecolor

    @linecolor.setter
    def linecolor(self, value):
        self._linecolor = Color(value)

    @property
    def linewidth(self):
        return self._linewidth

    @linewidth.setter
    def linewidth(self, value):
        self._linewidth = float(value)

    color = linecolor

    def __init__(self,
                 linewidth=1,
                 linecolor=None,
                 color=black,
                 visible=True):
        linecolor = color if linecolor is None else linecolor
        self._linewidth = float(linewidth)
        self._linecolor = Color(linecolor)
        super().__init__(visible=visible)

    def draw(self, canvas):
        try:
            if self._canvas_obj is not canvas:
                raise AttributeError
        except AttributeError:
            self._prepare_canvas(canvas)

        self._prepare_canvas(canvas)
        lc = self.linecolor
        lw = self.linewidth
        return self._canvas_func(self, lc, lw)


class Solid(smallshapes.core.solid.mSolid, Shape):
    """
    Base class for all geometric objects.

    It adds
    """

    __slots__ = ()
    _slots = ('_fillcolor',) + Shape._slots

    @property
    def fillcolor(self):
        return self._fillcolor

    @fillcolor.setter
    def fillcolor(self, value):
        self._fillcolor = Color(value)

    color = fillcolor

    def __init__(self,
                 linewidth=1,
                 linecolor=None,
                 color=black,
                 fillcolor=None,
                 visible=True):
        super().__init__(linewidth, linecolor, color, visible)
        if fillcolor is None:
            fillcolor = color
        self._fillcolor = Color(fillcolor)

    def draw(self, canvas):
        try:
            if self._canvas_obj is not canvas:
                raise AttributeError
        except AttributeError:
            self._prepare_canvas(canvas)

        color = self.fillcolor
        lc = self.linecolor
        lw = self.linewidth
        return self._canvas_func(self, color, lc, lw)


class Segment(shapes.mSegment, Shape):
    """
    Line segment with definite *start* and *end* points.
    """

    __slots__ = Shape._slots

    def __init__(self, start, end,
                 linewidth=1,
                 linecolor=None,
                 color=black,
                 visible=True):
        shapes.mSegment.__init__(self, start, end)
        Shape.__init__(self, linewidth, linecolor, color, visible)

# class Ray(Curve, shapes.mRay):
#     """
#     A semi-finite line segment that begins in an specific *start* point.
#     """
#
#     def __init__(self, *args, **kwds):
#         raise RuntimeError('lines are not supported, perhaps you mean Segment?')
#
#
# class Line(Curve, shapes.mLine):
#     """
#     Infinite line
#     """
#
#     def __init__(self, *args, **kwds):
#         raise RuntimeError('lines are not supported, perhaps you mean Segment?')


class Path(shapes.mPath, Shape):
    """
    Path made of a sequence of points.
    """

    __slots__ = Shape._slots


class Circle(shapes.mCircle, Solid):
    """
    Circle of given *radius* and *center* point.
    """

    __slots__ = Solid._slots

    def __init__(self, radius, pos,
                 linewidth=1,
                 linecolor=None,
                 color=black,
                 fillcolor=None,
                 visible=True):
        shapes.mCircle.__init__(self, radius, pos)
        Solid.__init__(self, linewidth, linecolor, color, fillcolor, visible)


class AABB(shapes.mAABB, Solid):
    """
    Axis aligned bounding box.
    """

    __slots__ = Solid._slots

    def __init__(self, *args,
                 linewidth=1,
                 linecolor=None,
                 color=black,
                 fillcolor=None,
                 visible=True,
                 **kwargs):
        shapes.mAABB.__init__(self, *args, **kwargs)
        Solid.__init__(self, linewidth, linecolor, color, fillcolor, visible)


class Circuit(shapes.mCircuit, Shape):
    """
    A closed path without a well defined or contiguous interior.
    """

    __slots__ = Solid._slots


class PolyBase(Solid):
    """
    Base class for drawable polygons.
    """

    __slots__ = ()


class Poly(shapes.mPoly, PolyBase):
    """
    A polygon.
    """

    __slots__ = Solid._slots

    def __init__(self, data,
                 linewidth=1,
                 linecolor=None,
                 color=black,
                 fillcolor=None,
                 visible=True,
                 **kwargs):
        shapes.mPoly.__init__(self, data, **kwargs)
        PolyBase.__init__(self, linewidth, linecolor, color, fillcolor, visible)

class RegularPoly(shapes.mRegularPoly, PolyBase):
    """
    Regular polygon.
    """

    __slots__ = Solid._slots


class Rectangle(shapes.mRectangle, PolyBase):
    """
    A Poly subclass specialized in rectangles.

    Alternatively, can be initialized as an AABB and possibly setting a rotation
    angle `theta`."""

    __slots__ = Solid._slots


class Triangle(shapes.mTriangle, PolyBase):
    """
    Specializes Poly to represent triangles.
    """

    __slots__ = Solid._slots
