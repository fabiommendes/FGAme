from contextlib import contextmanager

import smallshapes.segment
from FGAme.draw import colorproperty, Color
from FGAme.mathtools import Vec2, asvector, shapes
from FGAme.utils import delegate_to, accept_vec_args, caching_proxy_factory

__all__ = ['Screen', 'Canvas', 'camera']
black = Color('black')
white = Color('white')


class Screen(object):
    """
    Abstract class that coordinates visualization. Must be overridden in each
    backend.
    """

    __instance = None
    is_canvas = False
    background = colorproperty('background')
    draw_circle = delegate_to('camera')
    draw_aabb = delegate_to('camera')
    draw_poly = delegate_to('camera')
    draw_segment = delegate_to('camera')
    draw_path = delegate_to('camera')
    draw_ray = delegate_to('camera')
    draw_line = delegate_to('camera')
    draw_image = delegate_to('camera')

    @property
    def shape(self):
        return self.width, self.height

    def __new__(cls, *args, **kwds):
        if cls.__instance is not None:
            raise TypeError('cannot create two instances of singleton object')
        return object.__new__(cls)

    def __init__(self, shape=(800, 600), pos=(0, 0), zoom=1, background=None):
        self.width, self.height = shape
        self.pos = Vec2(*pos)
        self.zoom = zoom
        self.background = background
        self.camera = Camera(self)
        self.visible = False

    def init(self):
        """
        Initialize game screen.
        """

    def show(self):
        """
        Show initialized game window.
        """

        self.visible = True

    def draw(self, obj):
        obj.draw(self.camera)


class Camera:
    """
    A camera defines a point of view for rendering objects on the screen.

    Cameras can zoom, pan and rotate the output image in relation with the
    world coordinates.
    """

    def __init__(self, canvas, displacement=(0, 0), scale=1, rotation=0):
        if scale != 1 or rotation != 0:
            raise ValueError('rotations and rescaling are not supported')

        self.displacement = asvector(displacement)
        self.canvas = canvas
        self._passthru = True

    @accept_vec_args
    def pan(self, vec):
        """
        Pan camera by the given displacement.
        """

        self.displacement -= vec
        self._passthru = self.displacement == (0, 0)

    def panleft(self, px):
        """
        Pan camera to the left by the given amount (in pixels).
        """

        self.pan(-px, 0)

    def panright(self, px):
        """
        Pan camera to the right by the given amount (in pixels).
        """

        self.pan(px, 0)

    def panup(self, px):
        """
        Pan camera upwards by the given amount (in pixels).
        """

        self.pan(0, px)

    def pandown(self, px):
        """
        Pan camera downards right by the given amount (in pixels).
        """

        self.pan(0, -px)

    @property
    def shape(self):
        return self.width, self.height

    @property
    def width(self):
        return self.canvas.width

    @property
    def height(self):
        return self.canvas.height

    @property
    def xmin(self):
        return -self.displacement.x

    @property
    def xmax(self):
        return -self.displacement.x + self.width

    def draw_circle(self, circle, fillcolor=None, linecolor=None, linewidth=1):
        """
        Draw a circle on screen.
        """

        if not self._passthru:
            circle = circle.move(self.displacement)

        if fillcolor is not None:
            self.canvas.raw_circle_solid(circle, fillcolor)
        if linecolor is not None and linewidth:
            self.canvas.raw_circle_border(circle, linewidth, linecolor)

    def draw_aabb(self, aabb, fillcolor=None, linecolor=None, linewidth=1):
        """
        Draw an axis aligned rectangle on screen.
        """

        if not self._passthru:
            aabb = aabb.move(self.displacement)

        if fillcolor is not None:
            self.canvas.raw_aabb_solid(aabb, fillcolor)
        if linecolor is not None and linewidth:
            self.canvas.raw_aabb_border(aabb, linewidth, linecolor)

    def draw_poly(self, poly, fillcolor=None, linecolor=None, linewidth=1):
        """
        Draw a polygon on screen.
        """

        if not self._passthru:
            poly = poly.move(self.displacement)

        if fillcolor is not None:
            self.canvas.raw_poly_solid(poly, fillcolor)
        if linecolor is not None and linewidth:
            self.canvas.raw_poly_border(poly, linewidth, linecolor)

    def draw_segment(self, segment, linecolor=black, linewidth=1):
        """
        Draw a line segment on screen.
        """

        if not self._passthru:
            segment = segment.move(self.displacement)

        if linecolor is not None and linewidth:
            self.canvas.raw_segment(segment, linewidth, linecolor)

    def draw_ray(self, ray, linecolor=black, linewidth=1):
        """
        Draw a ray (semi-line) on screen.
        """

        raise NotImplementedError

    def draw_line(self, line, linecolor=black, linewidth=1):
        """
        Draw an infinite line on screen.
        """

        raise NotImplementedError

    def draw_path(self, path, linecolor=black, linewidth=1):
        """
        Draw an (possibly open) path on screen.
        """

        if not self._passthru:
            path = path.move(self.displacement)

        points = iter(path)
        pt0 = next(points)
        for pt1 in points:
            self.canvas.raw_segment(smallshapes.segment.Segment(pt0, pt1), linewidth,
                                    linecolor)
            pt0 = pt1

    def draw_image(self, image):
        """
        Draw an image/sprite on screen.
        """

        if not self._passthru:
            image = image.move(self.displacement)
        self.canvas.raw_image(image)

    def draw(self, obj):
        """
        Draw any Drawable instance.
        """

        obj.draw(self)


class Canvas(Screen):
    """
    Screen handlers that implement the "painting" metaphor to rendering.

    Each object on the screen is thus "painted" at each frame.
    """
    is_canvas = True

    def __init__(self, shape=(800, 600), pos=(0, 0), zoom=1, background=None):
        super(Canvas, self).__init__(shape, pos, zoom, background)
        self._drawing_funcs = {}

    def show(self):
        super(Canvas, self).show()
        self.clear_background('white')
        self.flip()

    def flip(self):
        """
        Pushes the rendering buffer to the computer screen.
        """

        raise NotImplementedError

    @contextmanager
    def autoflip(self, clear=False):
        """
        Context manager that automatically flips the screen when the ``with``
        block finishes.

        If `clear=True`, it clears the screen before entering the ``with``
        block.
        """

        if clear:
            self.clear_background(self.background or Color('white'))

        try:
            yield None
        finally:
            self.flip()

    # These functions draw primitive objects without handling translation, scale
    # and rotation transformations. The primitive operations must be overridden
    # in each backend. Users should not use the "raw" versions of the drawing
    # functions
    def raw_pixel(self, pos, color=black):
        raise NotImplementedError

    def raw_segment(self, segment, width=1.0, color=black):
        raise NotImplementedError

    def raw_line(self, line, width=1.0, color=black):
        raise NotImplementedError

    def raw_ray(self, line, width=1.0, color=black):
        raise NotImplementedError

    def raw_circle_solid(self, circle, color=black):
        raise NotImplementedError

    def raw_circle_border(self, circle, width=1.0, color=black):
        raise NotImplementedError

    def raw_aabb_solid(self, aabb, color=black):
        raise NotImplementedError

    def raw_aabb_border(self, aabb, width=1.0, color=black):
        poly = shapes.Poly(aabb.vertices)
        self.raw_poly_border(poly, width=width, color=color)

    def raw_poly_solid(self, poly, color=black):
        raise NotImplementedError

    def raw_poly_border(self, poly, width=1.0, color=black):
        raise NotImplementedError

    def raw_texture(self, texture, start_pos=(0, 0)):
        raise NotImplementedError

    def raw_image(self, image):
        self.raw_texture(image.texture, image.pos_sw)

    def clear_background(self, color):
        raise NotImplementedError


@caching_proxy_factory
def camera():
    """
    Global camera object.
    """

    from FGAme import conf
    return conf.get_screen().camera
