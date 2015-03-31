'''
Created on 22/03/2015

@author: chips
'''

from FGAme.core import EventDispatcherMeta, signal
from FGAme.draw import Color, Shape
from FGAme.util import lazy


class HasVisualization(object):
    _is_mixin_ = True
    _slots_ = ['_visualization']

    def _init_has_visualization(self,
                                color='black',
                                line_color='black', line_width=0.0):

        c = color or 'black'
        lc = line_color or 'black'
        lw = line_width
        self._visualization = Shape.from_primitive(self, c, lc, lw)

    # Desenhando objeto #######################################################
    @property
    def visualization(self):
        return self._visualization

    @property
    def color(self):
        return self._visualization.color

    @color.setter
    def color(self, value):
        self._visualization.color = Color(value)

    @property
    def line_color(self):
        return self._visualization.line_color

    @line_color.setter
    def line_color(self, value):
        self._visualization.line_color = Color(value)


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
                    color=None):
        self._init_has_visualization(color)
        self._init_world_object(world)
