'''
Created on 22/03/2015

@author: chips
'''

from FGAme.mathutils import Vector
from FGAme.physics.elements import PhysElement
from FGAme.core import EventDispatcherMeta, signal
from FGAme.draw import Color, RectEcho
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
            self.flag_owns_damping = True
            self._damping = float(damping)

        self._adamping = 0.0
        if adamping is not None:
            self.flag_owns_adamping = True
            self._adamping = float(adamping)

        self._gravity = Vector(0, 0)
        if gravity is not None:
            self.flag_owns_gravity = True
            self._gravity = (Vector(0, -gravity)
                             if isinstance(gravity, (float, int))
                             else Vector(*gravity))

    #==========================================================================
    # Propriedades
    #==========================================================================

    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value):
        self._gravity = Vector(*value)
        self.owns_gravity = True

    @property
    def damping(self):
        return self._damping

    @damping.setter
    def damping(self, value):
        self._damping = float(value)
        self.owns_damping = True

    @property
    def adamping(self):
        return self._adamping

    @adamping.setter
    def adamping(self, value):
        self._adamping = float(value)
        self.owns_adamping = True

    # Redireciona as propriedades acessoras das flags para manter simetria
    # entre os argumentos do construtor e atributos do objeto
    owns_gravity = PhysElement.flag_owns_gravity
    owns_damping = PhysElement.flag_owns_damping
    owns_adamping = PhysElement.flag_owns_adamping

    #==========================================================================
    # Métodos
    #==========================================================================
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
            a.copy_from(self._vel)
            a *= -self._damping
            if self._gravity is not None:
                a += self._gravity
        elif self._gravity is not None:
            a.copy_from(self._gravity)
        else:
            a *= 0

    def init_alpha(self):
        '''Inicializa o vetor de aceleração com os valores devidos à gravidade
        e ao amortecimento'''

        self._alpha = - self._adamping * self._omega


class HasVisualization(object):
    _is_mixin_ = True
    _slots_ = ['_visualization', '_color']

    def _init_has_visualization(self, color=None, visualization=None):
        self._color = None
        if color is not None:
            self._color = Color(color)
        self._visualization = RectEcho(self)

    @property
    def visualization(self):
        return self._visualization

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = Color(value)

    #=========================================================================
    # Desenhando objeto
    #=========================================================================
    def get_drawable(self, color='black', lw=0, solid=True):
        '''Retorna um objeto que respeita a interface Drawable e pode ser
        utilizado para a renderização do objeto físico.'''

        return self.drawable

    def get_primitive_drawable(self):

        raise NotImplementedError

    def get_aabb_drawable(self, color='black', lw=0, solid=True):
        '''Retorna um objeto que pode ser utilizado para desenhar a AABB do
        objeto físico considerado'''

        return RectEcho(self, color=color, lw=lw, solid=solid)


@EventDispatcherMeta.decorate
class HasInputEvents(object):
    _is_mixin_ = True
    _slots_ = ['_input']

    long_press = signal('long-press', 'key', delegate='_input')
    key_up = signal('key-up', 'key', delegate='_input')
    key_down = signal('key-down', 'key', delegate='_input')
    mouse_motion = signal('mouse-motion', delegate='_input')
    mouse_click = signal('mouse-click', 'button', delegate='_input')

    @lazy
    def input(self):
        self.input = self.world.simulation.input
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

    def _init_mixin(self,
                    world=None,
                    color=None,
                    gravity=None, damping=None, adamping=None,
                    owns_gravity=None, owns_damping=None, owns_adamping=None):
        self._init_world_object(world)
        self._init_has_visualization(color)
        self._init_has_local_forces(gravity, damping, adamping,
                                    owns_gravity, owns_damping, owns_adamping)
