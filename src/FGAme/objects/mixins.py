'''
Created on 22/03/2015

@author: chips
'''

from FGAme.core import EventDispatcherMeta, signal
from FGAme.draw import Color, Shape
from FGAme.util import lazy


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


@EventDispatcherMeta.decorate
class HasInputEvents(object):
    _is_mixin_ = True
    _slots_ = ['_input']

    long_press = signal('long-press', 'key', delegate_to='_input')
    key_up = signal('key-up', 'key', delegate_to='_input')
    key_down = signal('key-down', 'key', delegate_to='_input')
    mouse_motion = signal('mouse-motion', delegate_to='_input')
    mouse_click = signal('mouse-click', 'button', delegate_to='_input')

    @lazy
    def input(self):
        self.input = self.world._simulation.input
        return self.input


@EventDispatcherMeta.decorate
class HasEvents(object):
    _is_mixin_ = True

    # Eventos privados
    frame_enter = signal('frame-enter')
    collision = signal('collision', num_args=1)


class WorldObject(object):
    _is_mixin_ = True
    _slots_ = ['_world']

    def _init_world_object(self, world=None):
        if world is not None:
            world.add(self)


class ObjectMixin(WorldObject, HasVisualization):
    _mixin_args = set([
        'world', 'color', 'line_color',
    ])

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
        self._init_world_object(world)
