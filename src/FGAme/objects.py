# -*- coding: utf8 -*-
'''
Re-define os objetos do módulo FGAme.physics e adiciona propriades extras de
renderização
'''


from FGAme import physics
from FGAme.events import EventDispatcherMeta, signal
from FGAme.core import conf
from FGAme.draw import Color, color
from FGAme.util import lazy
DEBUG = False

__all__ = ['AABB', 'Circle', 'Poly', 'RegularPoly', 'Rectangle']


class HasVisualization(object):
    _is_mixin_ = True
    _slots_ = ['_color', '_linecolor', '_linewidth']

    def _init_has_visualization(self,
                                color='black',
                                linecolor=None, linewidth=1):

        self._color = None if color is None else Color(color)
        self._linecolor = None if linecolor is None else Color(linecolor)
        self._linewwidth = linewidth

    # Desenhando objeto #######################################################
    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if value is None:
            self._color = None
        else:
            self._color = Color(value)

    @property
    def linecolor(self):
        return self._linecolor

    @linecolor.setter
    def linecolor(self, value):
        if value is None:
            self._linecolor = None
        else:
            self._color = Color(value)

    def _debug(self, screen):
        if DEBUG:
            self.paint_contact_points(screen)

    def paint_contact_points(self, screen):
        for col in self._contacts:
            screen.paint_circle(2, col.pos, Color('black'))


@EventDispatcherMeta.decorate
class ObjectMixin(HasVisualization):
    _mixin_args = set(['color', 'line_color'])

    long_press = signal('long-press', 'key', delegate_to='_input')
    key_up = signal('key-up', 'key', delegate_to='_input')
    key_down = signal('key-down', 'key', delegate_to='_input')
    mouse_motion = signal('mouse-motion', delegate_to='_input')
    mouse_button_up = signal(
        'mouse-button-up', 'button', delegate_to='_input')
    mouse_button_down = signal(
        'mouse-button-down', 'button', delegate_to='_input')
    mouse_long_press = signal(
        'mouse-long-press', 'button', delegate_to='_input')

    @lazy
    def _input(self):
        return conf.get_input()

    def __init__(self, *args, **kwds):
        mixin_kwds = self._extract_mixin_kwargs(kwds)
        self._init_physics(*args, **kwds)
        self._init_mixin(**mixin_kwds)

    def _extract_mixin_kwargs(self, kwds):
        D = {}
        mixin_args = self._mixin_args
        for k in kwds:
            if k in mixin_args:
                D[k] = kwds[k]
        for k in D:
            del kwds[k]
        return D

    def _init_mixin(self,
                    world=None,
                    color='black', linecolor=None, linewidth=1):

        self._init_has_visualization(color=color,
                                     linecolor=linecolor, linewidth=linewidth)


class AABB(ObjectMixin, physics.AABB):
    _init_physics = physics.AABB.__init__

    def paint(self, screen):
        if self.color is not None:
            screen.paint_rect(self.rect, self.color)
            self._debug(screen)


class Circle(ObjectMixin, physics.Circle):
    _init_physics = physics.Circle.__init__

    def paint(self, screen):
        if self._color is not None:
            color = self._color
            screen.paint_circle(self.radius, self.pos, color)
        if self._linecolor is not None:
            screen.paint_circle(self.radius, self.pos,
                                self._linecolor,
                                self._linewidth)
        self._debug(screen)


class Poly(ObjectMixin, physics.Poly):
    _init_physics = physics.Poly.__init__

    def paint(self, screen):
        if self.color is not None:
            screen.paint_poly(self.vertices, self.color)
            self._debug(screen)


class Rectangle(ObjectMixin, Poly, physics.Rectangle):
    _init_physics = physics.Rectangle.__init__


class RegularPoly(ObjectMixin, Poly, physics.RegularPoly):
    _init_physics = physics.RegularPoly.__init__


if __name__ == '__main__':
    x = AABB(shape=(100, 200), world=set())
    type(x)
    print(x.mass)
