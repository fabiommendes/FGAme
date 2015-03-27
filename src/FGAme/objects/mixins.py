'''
Created on 22/03/2015

@author: chips
'''

from FGAme.mathutils import Vector
from FGAme.physics import Dynamic, flags
from FGAme.core import EventDispatcherMeta, signal
from FGAme.draw import Color, Shape
from FGAme.util import lazy


class HasLocalForces(object):

    '''Classe mix-in para todos os objetos que possuam uma gravidade e damping
    locais associados a um mundo

    **Forças locais**

    gravity
        Valor da aceleração da gravidade aplicada ao objeto
    damping, adamping
        Constante de amortecimento linear/angular para forças viscosas
        aplicadas ao objeto
    owns_gravity, owns_damping, owns_adamping
        Se Falso (padrão) utiliza os valores de gravity e damping/adamping
        fornecidos pelo mundo
    accel_static
        Caso verdadeiro, aplica as acelerações de gravidade, damping/adamping
        no objeto mesmo se ele for estático


    Example
    -------

    >>> elem = PhysWorldElement(gravity=9.8)
    >>> elem.gravity
    Vector(0, -9.8)
    >>> elem.owns_gravity
    True
    >>> elem.owns_damping
    False

    '''

    _slots_ = ['_damping', '_adamping', '_gravity', '_damping']
    _is_mixin_ = True

    def _init_has_local_forces(
            self,
            gravity=None, damping=None, adamping=None,
            owns_gravity=None, owns_damping=None, owns_adamping=None):

        self._damping = 0.0
        if damping is not None:
            self.flags |= flags.OWNS_ADAMPING
            self._damping = float(damping)

        self._adamping = 0.0
        if adamping is not None:
            self.flags |= flags.OWNS_DAMPING
            self._adamping = float(adamping)

        self._gravity = Vector(0, 0)
        if gravity is not None:
            self.flags |= flags.OWNS_GRAVITY
            self._gravity = (Vector(0, -gravity)
                             if isinstance(gravity, (float, int))
                             else Vector(*gravity))

    # Propriedades ############################################################
    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value):
        self._gravity = Vector(*value)
        self.flags |= flags.OWNS_GRAVITY

    @property
    def damping(self):
        return self._damping

    @damping.setter
    def damping(self, value):
        self._damping = float(value)
        self.flags |= flags.OWNS_DAMPING

    @property
    def adamping(self):
        return self._adamping

    @adamping.setter
    def adamping(self, value):
        self._adamping = float(value)
        self.flags |= flags.OWNS_ADAMPING

    # Redireciona as propriedades acessoras das flags para manter simetria
    # entre os argumentos do construtor e atributos do objeto
    @property
    def owns_gravity(self):
        return bool(self.flags & flags.OWNS_GRAVITY)

    @property
    def owns_damping(self):
        return bool(self.flags & flags.OWNS_DAMPING)

    @property
    def owns_adamping(self):
        return bool(self.flags & flags.OWNS_ADAMPING)

    # Métodos #################################################################
    def global_force(self):
        '''Calcula a força total devido à gravidade e amortecimento'''

        return self._mass * (self._gravity - self._damping * self._vel)

    def global_accel(self):
        '''Calcula a contribuição para a aceleração devido à gravidade e
        amortecimento'''

        return self._gravity - self._damping * self._vel

    def init_accel(self):
        '''Inicializa o vetor de aceleração com os valores devidos à gravidade
        e ao amortecimento'''

        a = self._accel
        if self._damping:
            a.update(self._vel)
            a *= -self._damping
            if self._gravity is not None:
                a += self._gravity
        elif self._gravity is not None:
            a.update(self._gravity)
        else:
            a *= 0

    def init_alpha(self):
        '''Inicializa o vetor de aceleração com os valores devidos à gravidade
        e ao amortecimento'''

        self._alpha = - self._adamping * self._omega


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


class ObjectMixin(WorldObject, HasLocalForces, HasVisualization):
    _mixin_args = set([
        'world', 'color', 'line_color',
        'gravity', 'damping', 'adamping',
        'owns_gravity', 'owns_damping', 'owns_adamping',
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
                    color=None,
                    gravity=None, damping=None, adamping=None,
                    owns_gravity=None, owns_damping=None, owns_adamping=None):
        self._init_has_visualization(color)
        self._init_has_local_forces(gravity, damping, adamping,
                                    owns_gravity, owns_damping, owns_adamping)
        self._init_world_object(world)
