'''
Created on 22/03/2015

@author: chips
'''

from FGAme.events import EventDispatcherMeta, signal
from FGAme.core import conf
from FGAme.draw import Color
from FGAme.util import lazy
DEBUG = False


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
