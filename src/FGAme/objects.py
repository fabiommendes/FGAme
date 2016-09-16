"""
Re-define os objetos do módulo FGAme.physics e adiciona propriades extras de
renderização
"""

from FGAme import conf
from FGAme import draw
from FGAme import physics
from FGAme.draw import Color, colorproperty, Image
from FGAme.mathtools import asvector
from FGAme.utils import lazy

__all__ = [
    'AABB', 'Circle',  'Poly', 'RegularPoly', 'Rectangle',
]
black = Color('black')


class Body(physics.Body):
    def __init__(self, *args, **kwargs):
        # Visualization parameters
        image = {
            'image': kwargs.pop('image', None)
        }
        for k in list(kwargs):
            if k.startswith('image_'):
                image[k] = kwargs.pop(k)
        self.color = kwargs.pop('color', black)
        self.linecolor = kwargs.pop('linecolor', None)
        self.linewidth = kwargs.pop('linewidth', 1)
        self.visible = kwargs.pop('visible', True)

        self.world = kwargs.pop('world', None)

        # Init physics object and visualization
        super().__init__(*args, **kwargs)
        self.__init_image(**image)

        # Set world
        if self.world is not None:
            self.world.add(self)

    def __init_image(self, image, image_offset=(0, 0), image_reference=None,
                     **kwargs):
        self._image = None
        self._drawshape = None

        if image is not None:
            # Get all image parameters
            img_kwargs = {}
            for k, v in kwargs.items():
                if k.startswith('image_'):
                    img_kwargs[k[6:]] = v

            if isinstance(image, str):
                image = Image(image, self.pos, **img_kwargs)
            else:
                raise NotImplementedError
            self._image = image

            offset = asvector(image_offset)
            if image_reference in ['pos_ne', 'pos_nw', 'pos_se', 'pos_sw',
                                   'pos_left', 'pos_right', 'pos_up',
                                   'pos_down']:
                pos_ref = getattr(self, image_reference)
                pos_img_ref = getattr(image, image_reference)
                offset += pos_ref - pos_img_ref
            elif image_reference not in ['middle', None]:
                raise ValueError(
                    'invalid image reference: %r' % image_reference)
            image.offset = offset
        else:
            self._drawshape = self._init_drawshape(color=self.color or black,
                                                   linecolor=self.linecolor,
                                                   linewidth=self.linewidth)

    @lazy
    def _input(self):
        return conf.get_input()

    color = colorproperty('color')
    linecolor = colorproperty('linecolor')

    @property
    def image(self):
        img = self._image
        if img is None:
            return None
        img.pos = self.pos + img.offset
        return img

    @image.setter
    def image(self, value):
        if value is None:
            self._image = None
            return
        if isinstance(value, str):
            value = Image(value, self.pos)
        self._image = value

    @property
    def drawable(self):
        return self.image or self.drawshape

    @property
    def drawshape(self):
        if self._drawshape is None:
            return None
        self._drawshape.pos = self.pos
        return self._drawshape

    def show(self):
        """
        Makes object visible.
        """

        self.visible = True

    def hide(self):
        """
        Makes object invisible.

        It keeps interacting with the wold, but it is not shown on the screen.
        """

        self.visible = False

    def draw(self, screen):
        """
        Draw object in a canvas-like screen.
        """

        img = self.image
        if img is not None:
            img.pos = self.pos + img.offset
            return img.draw(screen)
        else:
            return self.draw_shape(screen)

    def draw_shape(self, screen):
        """
        Draw a shape identical to the object's bounding box.
        """

        raise NotImplementedError('must be implemented on subclass.')

    def destroy(self):
        super().destroy()
        if self.world is not None:
            self.world.remove(self)
            self.world = None

    def _init_drawshape(self, color=None, linecolor=None, linewidth=1):
        bbox = self.bb
        cls = getattr(draw, type(bbox).__name__)
        return cls(*bbox, color=color, linecolor=linecolor, linewidth=linewidth)


class AABB(Body, physics.AABB):
    """
    Object with an axis aligned bounding box.

    AABB objects cannot rotate and thus have an infinite inertia.
    """

    def draw_shape(self, screen):
        bb = self.bb

        if self._color is not None:
            color = self._color
            lw, lc = self.linewidth, self._linecolor
            screen.draw_aabb(bb, color, lw, lc)

        elif self.linewidth:
            lw, lc = self.linewidth, self._linecolor
            screen.draw_aabb(bb, black, lw, lc)

    @property
    def drawshape(self):
        if self._drawshape is None:
            return None
        self._drawshape.xmin = self.xmin
        self._drawshape.xmax = self.xmax
        self._drawshape.ymin = self.ymin
        self._drawshape.ymax = self.ymax
        return self._drawshape


class Circle(Body, physics.Circle):
    """
    Object with a circular bounding box.
    """

    def draw_shape(self, screen):
        bb = self.bb
        if self._color is not None:
            color = self._color
            lw, lc = self.linewidth, self._linecolor
            screen.draw_circle(bb, color, lw, lc)

        elif self.linewidth:
            lw, lc = self.linewidth, self._linecolor
            screen.draw_circle(bb, black, lw, lc)


class Poly(Body, physics.Poly):
    """
    Object with a convex polygonal bounding box.
    """

    def draw_shape(self, screen):
        if self._color is not None:
            color = self._color
            lw, lc = self.linewidth, self._linecolor
            screen.draw_poly(self.bb, color, lw, lc)

        elif self.linewidth:
            lw, lc = self.linewidth, self._linecolor
            screen.draw_poly(self.bb, black, lw, lc)

    def _init_drawshape(self, color=None, linecolor=None, linewidth=1):
        return draw.Poly(self.bb,
                         color=color, linecolor=linecolor,
                         linewidth=linewidth)


class Rectangle(Poly, physics.Rectangle):
    """
    Similar to Poly, but all instances are rectangles.

    This is useful if you want an AABB that needs to rotate.
    """


class RegularPoly(Poly, physics.RegularPoly):
    """
    Similar to Poly, but restricted to regular polygons.
    """


