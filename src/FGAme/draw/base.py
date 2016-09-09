import copy

import smallshapes as shapes
import smallshapes.core.locatable
from colortools import *


class Drawable(smallshapes.core.locatable.mLocatable):
    """
    Abstract base class for all objects that can be drawn on the screen.
    """

    # It would require a 'visible' slot, but we need to be able to use multiple
    # inheritance, which requires empty slots.
    # These slots might be inserted manually or we might rely on the object's
    # __dict__
    __slots__ = ()
    _slots = ('visible',)

    def __init__(self, visible=True):
        self.visible = visible

    def show(self):
        """
        Makes object visible.
        """

        self.visible = True

    def hide(self):
        """
        Makes object invisible.
        """

        self.visible = False

    def copy(self):
        """
        Return a copy of object.
        """

        return copy.copy(self)

    def draw(self, canvas):
        """
        Draw object on the screen using primitive drawing functions from the
        Canvas object.
        """

        raise NotImplementedError

    def _prepare_canvas(self, canvas_obj):
        name = 'draw_' + type(self).__name__.lower()
        type(self)._canvas_func = getattr(canvas_obj, name)
        type(self)._canvas_obj = canvas_obj
