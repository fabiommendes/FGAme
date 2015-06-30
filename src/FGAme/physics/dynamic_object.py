# -*- coding: utf8 -*-
from FGAme.events import EventDispatcher, EventDispatcherMeta, signal
from FGAme.mathutils import Vec2, sin, cos, sqrt, null2D, Circle
from FGAme.util import six
from FGAme.physics.flags import BodyFlags as flags


__all__ = ['Body', 'LinearRigidBody']


###############################################################################
#                              Funções úteis
###############################################################################
NOT_IMPLEMENTED = NotImplementedError('must be implemented at child classes')
INERTIA_SCALE = 1
INF = float('inf')


# TODO: mover para FGAme.util
def do_nothing(*args, **kwds):
    '''A handle that does nothing'''


def raises_method(exception=NOT_IMPLEMENTED):
    '''Returns a method that raises the given exception'''

    def method(self, *args, **kwds):
        raise exception
    return method


def popattr(obj, attr, value=None):
    '''Returns attribute `attr` from `obj` and delete it afterwards.
    If attribute does not exist, return `value`'''

    try:
        result = getattr(obj, attr)
    except AttributeError:
        return value
    else:
        delattr(obj, attr)
        return result

###############################################################################
#          Classes Base --- todos objetos físicos derivam delas
###############################################################################
Body = None


class PhysElementMeta(EventDispatcherMeta):

    '''Metaclasse para todas as classes que representam objetos físicos'''

    BLACKLIST = ['_is_mixin_', '__module__', '__doc__', '__module__',
                 '__dict__', '__weakref__', '__slots__', '__subclasshook__']

    def __new__(cls, name, bases, ns):
        # Aplica transformações da EventDispatcherMeta
        has_slots = '__slots__' in ns
        slots = ns.setdefault('__slots__', [])
        ns = cls._populate_namespace(name, bases, ns)

        # Remove __slots__ creiados pela EventDispatcher
        ns['__slots__'] = slots

        # Força EventDispatcher ser a classe mãe na hierarquia
        if bases == (object,):
            bases = (EventDispatcher,)

        # Insere uma cláusula de __slots__ vazia
        ns.setdefault('__slots__', [])

        # Verifica se existem classes mix-in entre as bases
        true_bases = tuple(B for B in bases
                           if not getattr(B, '_is_mixin_', False))
        if len(bases) != len(true_bases):
            for i, B in enumerate(bases):
                if not getattr(B, '_is_mixin_', False):
                    continue

                # Encontra quais variáveis/métodos foram definidos nas classes
                # mixin
                allvars = {attr: getattr(B, attr) for attr in dir(B)}
                for var in cls.BLACKLIST:
                    if var in allvars:
                        del allvars[var]
                for attr, value in list(allvars.items()):
                    if hasattr(object, attr):
                        if getattr(object, attr) is value:
                            del allvars[attr]

                # Insere as variáveis que não foram definidas em ns nem em
                # nenhuma base anterior
                prev_bases = bases[:i]
                for attr in list(allvars.keys()):
                    if attr in ns:
                        del allvars[attr]
                        continue

                    for B in prev_bases:
                        if hasattr(B, attr):
                            del allvars[attr]
                            break

                # Em Python 2, utiliza o objeto im_func dos métodos, caso ele
                # exista
                allvars = {name: getattr(var, 'im_func', var) for (name, var)
                           in allvars.items()}

                ns.update(allvars)

                # Atualiza a lista de __slots__ utilizando o atributo _slots_
                # do mixin e toda hierarquia inferior
                for tt in B.mro():
                    slots = getattr(tt, '_slots_', [])
                    ns['__slots__'].extend(slots)

        # Atualiza a lista de propriedades e retira slots repetidos
        ns['__slots__'] = list(set(ns['__slots__']))
        if not has_slots:
            del ns['__slots__']
        else:
            if Body is None:
                ns['__slots__'].append('__dict__')
        new = type.__new__(cls, name, true_bases, ns)

        # Atualiza as docstrings vazias utilizando as docstrings da primeira
        # base válida
        mro = new.mro()[1:-1]
        for name, method in ns.items():
            if not callable(method):
                continue

            doc = getattr(method, '__doc__', '<no docstring>')
            if not doc:
                for base in mro:
                    try:
                        other = getattr(base, name)
                    except AttributeError:
                        continue
                    if other.__doc__:
                        # TODO: six it
                        try:
                            method.__doc__ = other.__doc__
                        except AttributeError:
                            pass
                    break

        return new


@six.add_metaclass(PhysElementMeta)
class Body(object):

    '''Classe mãe de todos objetos com propriedades dinâmicas.

    Attributes
    ----------

    ::
        **Propriedades físicas do objeto**
    mass
        Massa do objeto. Possui o valor padrão de 1. Uma massa infinita
        transforma o objeto num objeto cinemático que não responde a forças
        lineares.

    ::
        **Variáveis dinâmicas**
    pos
        Posição do centro de massa do objeto
    vel
        Velocidade linear medida a partir do centro de massa
    accel
        Aceleração acumulada recalculada em cada frame

    ::
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

    ::
        **Propriedades físicas do objeto**
    inertia
        Momento de inércia do objeto com relação ao eixo z no centro de massa.
        Calculado automaticamente a partir da geometria e densidade do objeto.
        Caso seja infinito, o objeto não responderá a torques.
    ROG, ROG_sqr
        Raio de giração e o quadrado do raio de giração. Utilizado para
        calcular o momento de inércia: $I = M R^2$, onde I é o momento de
        inércia, M a massa e R o raio de giração.
    density
        Densidade de massa: massa / área
    area
        Área que o objeto ocupa

    ::
        **Variáveis dinâmicas**
    theta
        Ângulo da rotação em torno do eixo saindo do centro de massa do objeto
    omega
        Velocidade angular de rotação

    ::
        **Caixa de contorno**
    xmin, xmax, ymin, ymax
        Limites da caixa de contorno alinhada aos eixos que envolve o objeto
    bbox
        Uma tupla com (xmin, xmax, ymin, ymax)
    shape
        Uma tupla (Lx, Ly) com a forma caixa de contorno nos eixos x e y.
    rect
        Uma tupla com (xmin, ymin, Lx, Ly)

        **Flags de colisão**
    col_group : int ou sequência
        Número inteiro positivoque representa o grupo a qual o objeto pertence.
        Objetos do mesmo grupo nunca colidem entre si. `col_group` pode ser uma
        sequência de valores caso o objeto pertença a vários grupos. O grupo
        zero (padrão) é tratado de forma especial e todos os objetos deste
        grupo colidem entre si.
    col_layer : int ou sequência
        Número inteiro positivo representando a camdada à qual o objeto
        pertence. O valor padrão é zero. Apenas objetos que estão na mesma
        camada colidem entre si. `col_layer` pode ser uma sequência de valores
        caso o objeto participe de várias camadas.
    '''

    __slots__ = [
        'flags', 'cbb_radius', '_baseshape', '_shape', '_aabb',
        '_pos', '_vel', '_accel', '_theta', '_omega', '_alpha',
        '_invmass', '_invinertia', '_e_vel', '_e_omega', '_world',
        '_col_layer', '_col_group_mask',
    ]

    DEFAULT_FLAGS = 0 | flags.can_rotate | flags.dirty_shape | flags.dirty_aabb

    def __init__(self, pos=null2D, vel=null2D, theta=0.0, omega=0.0,
                 mass=None, density=None, inertia=None,
                 gravity=None, damping=None, adamping=None,
                 restitution=None, sfriction=None, dfriction=None,
                 baseshape=None, world=None, col_layer=0, col_group=0,
                 flags=DEFAULT_FLAGS):

        self._world = world
        EventDispatcher.__init__(self)

        # Flags de objeto
        self.flags = flags

        # Variáveis de estado #################################################
        self._pos = Vec2(pos)
        self._vel = Vec2(vel)
        self._e_vel = null2D
        self._e_omega = 0.0
        self._theta = float(theta)
        self._omega = float(omega)
        self._accel = null2D
        self._alpha = 0.0

        # Harmoniza massa, inércia e densidade ################################
        self._baseshape = self._shape = baseshape
        self._aabb = getattr(baseshape, 'aabb', None)
        if density is not None:
            density = float(density)
            if mass is None:
                mass = density * self.area()
            else:
                mass = float(mass)
            if inertia is None:
                inertia = density * \
                    self.area() * self.ROG_sqr() / INERTIA_SCALE
            else:
                inertia = float(inertia)

        elif mass is not None:
            mass = float(mass)
            density = mass / self.area()
            if inertia is None:
                inertia = mass * self.ROG_sqr() / INERTIA_SCALE
            else:
                inertia = float(inertia)

        else:
            density = 1.0
            mass = density * self.area()
            if inertia is None:
                inertia = density * \
                    self.area() * self.ROG_sqr() / INERTIA_SCALE
            else:
                inertia = float(inertia)

        self._invmass = 1.0 / mass
        self._invinertia = 1.0 / inertia
        self._density = float(density)

        # Controle de parâmetros físicos locais ###############################
        self._gravity = null2D
        self._damping = self._adamping = 0.0
        self._sfriction = self._dfriction = 0.0
        self._restitution = 1.0
        if damping is not None:
            self.damping = damping
        if adamping is not None:
            self.adamping = adamping
        if gravity is not None:
            self.gravity = gravity
        if restitution is not None:
            self.restitution = restitution
        if sfriction is not None:
            self.sfriction = sfriction
        if sfriction is not None:
            self.dfriction = dfriction

        # Vínculos e contatos #################################################
        self._contacts = []
        self._joints = []

        # Filtros de colisões #################################################
        # Colide se objetos estão em groupos diferentes (exceto os que estão
        # no grupo 0) e no mesmo layer
        if col_layer:
            if isinstance(col_layer, int):
                self._col_layer_mask = 1 << col_layer
            else:
                mask = 0
                for n in col_layer:
                    mask |= 1 << n
                self._col_layer_mask = mask
        else:
            self._col_layer_mask = 0

        if col_group:
            if isinstance(col_group, int):
                self._col_group_mask = 1 << (col_group - 1)
            else:
                mask = 0
                for n in col_group:
                    mask |= 1 << (n - 1)
                self._col_group_mask = mask
        else:
            self._col_group_mask = 0

        # Presença em mundo ###################################################
        if world is not None:
            self._world.add(self)

    ###########################################################################
    #                            Serviços Python
    ###########################################################################

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)

    def __repr__(self):
        tname = type(self).__name__
        pos = ', '.join('%.1f' % x for x in self._pos)
        vel = ', '.join('%.1f' % x for x in self._vel)
        return '%s(pos=(%s), vel=(%s))' % (tname, pos, vel)

    # TODO: def __copy__(self): ?
    # TODO: def __getstate__(self): ?

    ###########################################################################
    #                      Propriedades geométricas
    ###########################################################################
    @property
    def cbb(self):
        '''Caixa de contorno circular que envolve o objeto'''

        return Circle(self.cbb_radius, self.pos)

    @property
    def aabb(self):
        '''Caixa de contorno alinhada aos eixos que envolve o objeto'''

        if self.flags & flags.dirty_aabb:
            self._aabb = self.bounding_box.get_aabb()
            self.flags &= flags.not_dirty_aabb
        return self._aabb

    @property
    def bounding_box(self):
        '''Retorna um objeto que representa o formato geométrico do corpo
        físico, ex.: Circle, AABB, Poly, etc'''

        if self.flags & flags.dirty_any:
            self._shape = self._baseshape.move(self.pos).rotate(self._theta)
            self.flags &= flags.not_dirty
        return self._shape

    # Propriedades da caixa de contorno #######################################
    @property
    def xmin(self):
        raise NotImplementedError

    @property
    def xmax(self):
        raise NotImplementedError

    @property
    def ymin(self):
        raise NotImplementedError

    @property
    def ymax(self):
        raise NotImplementedError

    @property
    def bbox(self):
        return (self.xmin, self.xmax, self.ymin, self.ymax)

    @property
    def shape(self):
        return (self.xmax - self.xmin, self.ymax - self.ymin)

    @property
    def width(self):
        return self.xmax - self.xmin

    @property
    def height(self):
        return self.ymax - self.ymin

    @property
    def rect(self):
        x, y = self.xmin, self.ymin
        return (x, y, self.xmax - x, self.ymax - y)

    @property
    def pos_sw(self):
        return Vec2(self.xmin, self.ymin)

    @property
    def pos_se(self):
        return Vec2(self.xmax, self.ymin)

    @property
    def pos_nw(self):
        return Vec2(self.xmin, self.ymax)

    @property
    def pos_ne(self):
        return Vec2(self.xmax, self.ymax)

    @property
    def pos_right(self):
        return Vec2(self.xmax, self.pos.y)

    @property
    def pos_left(self):
        return Vec2(self.xmin, self.pos.y)

    @property
    def pos_up(self):
        return Vec2(self.pos.x, self.ymax)

    @property
    def pos_down(self):
        return Vec2(self.pos.x, self.ymin)

    ###########################################################################
    #                          Contatos e vínculos
    ###########################################################################
    def add_contact(self, contact):
        '''Registra um contato à lista de contatos do objeto'''

        L = self._contacts
        invmass = contact.A._invmass
        for i, C in enumerate(L):
            if invmass < C.A._invmass:
                L.insert(i, C)
                break
        else:
            L.append(contact)

    def remove_contact(self, contact):
        '''Remove um contato da lista de contatos do objeto'''

        try:
            self._contacts.remove(contact)
        except ValueError:
            pass

    ###########################################################################
    #                                Sinais
    ###########################################################################
    collision = signal('collision', num_args=1)
    frame_enter = signal('frame-enter')
    out_of_bounds = signal('out-of-bounds', num_args=1)

    ###########################################################################
    #                            Controle de flags
    ###########################################################################
    def set_flag(self, flag, value):
        '''Atribui um valor de verdade para a flag especificada.

        O argumento pode ser uma string ou a constante em FGAme.physics.flags
        associada à flag'''

        if isinstance(flag, str):
            flag = self._get_flag(flag)
        if value:
            self.flags |= flag
        else:
            self.flags &= ~flag

    def toggle_flag(self, flag):
        '''Inverte o valor da flag.

        O argumento pode ser uma string ou a constante em FGAme.physics.flags
        associada à flag'''

        if isinstance(flag, str):
            flag = self._get_flag(flag)

        value = not (self.flags & flag)
        if value:
            self.flags |= flag
        else:
            self.flags &= ~flag

    def get_flag(self, flag):
        '''Retorna o valor da flag.

        O argumento pode ser uma string ou a constante em FGAme.physics.flags
        associada à flag'''

        if isinstance(flag, str):
            flag = self._get_flag(flag)
        return bool(self.flags | flag)

    ###########################################################################
    #        Controle de criação e destruição e interação com o mundo
    ###########################################################################
    @property
    def world(self):
        if self._world is None:
            raise ValueError('trying to access rogue object')
        else:
            return self._world

    def set_active(self, value):
        '''Determina o estado ativo do objeto'''

        if value:
            self.flags &= flags.not_active
        else:
            self.world.set_active(self)
            self.flags |= flags.is_active

    def is_rogue(self):
        '''Retorna True se o objeto não estiver associado a uma simulação'''

        return self.world is None

    def destroy(self):
        '''Destrói o objeto físico'''

        if not self.is_rogue():
            if self in self.world:
                self.world.remove(self)

        # TODO: desaloca todos os sinais

    ###########################################################################
    #                          Estado dinâmico
    ###########################################################################
    @property
    def omega(self):
        return self._omega

    @omega.setter
    def omega(self, value):
        if self.flags & flags.can_rotate:
            self._omega = value + 0.0
        elif value:
            self._raise_cannot_rotate_error()

    @property
    def theta(self):
        return self._theta

    @theta.setter
    def theta(self, value):
        if self.flags & flags.can_rotate:
            self._theta = value + 0.0
        elif value:
            self._raise_cannot_rotate_error()

    ###########################################################################
    #                        Propriedades físicas
    ###########################################################################

    @property
    def mass(self):
        try:
            return 1.0 / self._invmass
        except ZeroDivisionError:
            return float('inf')

    @mass.setter
    def mass(self, value):
        value = float(value)

        if value <= 0:
            raise ValueError('mass cannot be null or negative')
        elif value != INF:
            self._density = value / self.area()
            if self._invinertia:
                inertia = value * self.ROG_sqr()
                self._invinertia = 1.0 / inertia
            self._invmass = 1.0 / value
        else:
            self._invmass = 0.0
            self._invinertia = 0.0

    @property
    def inertia(self):
        try:
            return 1.0 / self._invinertia
        except ZeroDivisionError:
            return INF

    @inertia.setter
    def inertia(self, value):
        value = float(value)

        if self.flags & flags.can_rotate:
            if value <= 0:
                raise ValueError('inertia cannot be null or negative')
            elif value != INF:
                self._invinertia = 1.0 / value
            else:
                self._invinertia = 0.0
        else:
            self._raise_cannot_rotate_error()

    @property
    def density(self):
        return self._density

    @density.setter
    def density(self, value):
        rho = float(value)
        self._density = rho
        if self._invmass:
            self._invmass = 1.0 / (self.area() * rho)
        if self._invinertia:
            self._invinertia = 1.0 / (self.area() * rho * self.ROG_sqr())

    # Grandezas físicas derivadas
    def linearE(self):
        '''Energia cinética das variáveis lineares'''

        if self._invmass:
            return self._vel.norm_sqr() / (2 * self._invmass)
        else:
            return 0.0

    def angularE(self):
        '''Energia cinética das variáveis angulares'''

        if self._invinertia:
            return self._omega ** 2 / (2 * self._invinertia)
        else:
            return 0.0

    def kineticE(self):
        '''Energia cinética total'''

        return self.linearE() + self.angularE()

    def potentialE(self):
        '''Energia potencial associada à gravidade'''

        return -self.gravity.dot(self._pos) / self._invmass

    def totalE(self):
        '''Energia total do objeto'''

        return self.kineticE() + self.potentialE()

    def momentumP(self):
        '''Momentum linear'''

        return self._vel / self._invmass

    def momentumL(self, pos=None):
        '''Momentum angular em torno do ponto dado (usa o centro de massa
        como padrão)'''

        if pos is None:
            delta = 0.0
        else:
            delta = (self._pos - pos).cross(self._vel) / self._invmass
        if self._invinertia:
            return delta + self._omega / self._invinertia
        else:
            return delta

    ###########################################################################
    #                        Propriedades Geométricas
    ###########################################################################
    def area(self):
        '''Retorna a área do objeto'''

        return self._baseshape.area

    def ROG_sqr(self):
        '''Retorna o raio de giração ao quadrado'''

        return self._baseshape.ROG_sqr

    def ROG(self):
        '''Retorna o raio de giração'''

        return sqrt(self.ROG_sqr)

    ###########################################################################
    #                      Aplicação de forças e torques
    ###########################################################################
    def move(self, delta_or_x, y=None):
        '''Move o objeto por vetor de deslocamento delta'''

        if y is None:
            if delta_or_x is null2D:
                return
            self._pos += delta_or_x
        else:
            self._pos += (delta_or_x, y)

        self.flags |= flags.dirty_any

    def boost(self, delta_or_x, y=None):
        '''Adiciona um valor vetorial delta à velocidade linear'''

        if y is None:
            self._vel += delta_or_x
        else:
            self._vel += Vec2(delta_or_x, y)

    # Resposta a forças, impulsos e atualização da física #####################
    def force(self, t):
        '''Define uma força externa que depende do tempo t.

        Pode ser utilizado por sub-implementações para definir uma força
        externa aplicada aos objetos de uma sub-classe ou usando o recurso de
        "monkey patching" do Python
        '''

        return null2D

    def init_accel(self):
        '''Inicializa o vetor de aceleração com os valores devidos à gravidade
        e ao amortecimento'''

        if self._damping:
            a = self._vel
            a *= -self._damping
            if self.gravity is not None:
                a += self._gravity
        elif self._gravity is not None:
            a = self._gravity
        else:
            a = null2D
        self._accel = a

    def apply_force(self, force, dt, pos=None, relative=False):
        '''Aplica uma força linear durante um intervalo de tempo dt'''

        if force is None:
            if self._invmass:
                self.apply_accel(self._accel, dt)
        else:
            self.apply_accel(force * self._invmass, dt)

        if pos is not None and self._invinertia:
            if relative:
                tau = pos.cross(force)
            else:
                tau = (pos - self._pos).cross(force)
            self.apply_torque(tau, dt)

    def apply_accel(self, a, dt):
        '''Aplica uma aceleração linear durante um intervalo de tempo dt.

        Tem efeito em objetos cinemáticos.

        Observations
        ------------

        Implementa a integração de Velocity-Verlet para o sistema. Este
        integrador é superior ao Euler por dois motivos: primeiro, trata-se de
        um integrador de ordem superior (O(dt^4) vs O(dt^2)). Além disto, ele
        possui a propriedade simplética, o que implica que o erro da energia
        não tende a divergir, mas sim oscilar ora positivamente ora
        negativamente em torno de zero. Isto é extremamente desejável para
        simulações de física que parecam realistas.

        A integração de Euler seria implementada como:

            x(t + dt) = x(t) + v(t) * dt + a(t) * dt**2 / 2
            v(t + dt) = v(t) + a(t) * dt

        Em código Python

        >>> self.move(self.vel * dt + a * (dt**2/2))           # doctest: +SKIP
        >>> self.boost(a * dt)                                 # doctest: +SKIP

        Este método simples e intuitivo sofre com o efeito da "deriva de
        energia". Devido aos erros de truncamento, o valor da energia da
        solução numérica flutua com relação ao valor exato. Na grande maioria
        dos sistemas, esssa flutuação ocorre com mais probabilidade para a
        região de maior energia e portanto a energia tende a crescer
        continuamente, estragando a credibilidade da simulação.

        Velocity-Verlet está numa classe de métodos numéricos que não sofrem
        com esse problema. A principal desvantagem, no entanto, é que devemos
        manter uma variável adicional com o último valor conhecido da
        aceleração. Esta pequena complicação é mais que compensada pelo ganho
        em precisão numérica. O algorítmo consiste em:

            x(t + dt) = x(t) + v(t) * dt + a(t) * dt**2 / 2
            v(t + dt) = v(t) + [(a(t) + a(t + dt)) / 2] * dt

        O termo a(t + dt) normalemente só pode ser calculado se soubermos como
        obter as acelerações como função das posições x(t + dt). Na prática,
        cada iteração de .apply_accel() calcula o valor da posição em x(t + dt)
        e da velocidade no passo anterior v(t). Calcular v(t + dt) requer uma
        avaliação de a(t + dt), que só estará disponível na iteração seguinte.
        A próxima iteração segue então para calcular v(t + dt) e x(t + 2*dt), e
        assim sucessivamente.

        A ordem de acurácia de cada passo do algoritmo Velocity-Verlet é de
        O(dt^4) para uma força que dependa exclusivamente da posição e tempo.
        Caso haja dependência na velocidade, a acurácia reduz e ficaríamos
        sujeitos aos efeitos da deriva de energia. Normalmente as forças
        físicas que dependem da velocidade são dissipativas e tendem a reduzir
        a energia total do sistema muito mais rapidamente que a deriva de
        energia tende a fornecer energia espúria ao sistema. Deste modo, a
        acurácia ficaria reduzida, mas a simulação ainda manteria alguma
        credibilidade.
        '''

        # TODO: reimplementar algoritmo correto
        a = Vec2.from_seq(a)
        self.move(self._vel * dt + a * (dt ** 2 / 2.0))
        self.boost(a * dt)

    def apply_impulse(self, impulse_or_x, y=None):
        '''Aplica um impulso linear ao objeto. Isto altera sua velocidade
        linear com relação ao centro de massa.

        Se for chamado com dois agumentos aplica o impulso em um ponto
        específico e também resolve a dinâmica angular.
        '''

        self.boost(Vec2(impulse_or_x, y) * self._invmass)

    # Variáveis angulares #####################################################
    def rotate(self, theta):
        '''Rotaciona o objeto por um ângulo _theta'''

        self._theta += theta
        if theta != 0.0:
            self.flags |= flags.dirty_any

    def aboost(self, delta):
        '''Adiciona um valor delta à velocidade ângular'''

        self._omega += delta

    def vpoint(self, pos_or_x, y=None, relative=False):
        '''Retorna a velocidade linear de um ponto em _pos preso rigidamente ao
        objeto.

        Se o parâmetro `relative` for verdadeiro, o vetor `_pos` é interpretado
        como a posição relativa ao centro de massa. O padrão é considerá-lo
        como a posição absoluta no centro de coordenadas do mundo.'''

        if relative:
            if y is None:
                x, y = pos_or_x
                return self._vel + self._omega * Vec2(-y, x)
            else:
                return self._vel + self._omega * Vec2(-y, pos_or_x)

        else:
            if y is None:
                x, y = pos_or_x - self._pos
                return self._vel + self._omega * Vec2(-y, x)
            else:
                x = pos_or_x - self._pos.x
                y = y - self._pos.y
                return self._vel + self._omega * Vec2(-y, x)

    def orientation(self, theta=0.0):
        '''Retorna um vetor unitário na direção em que o objeto está orientado.
        Pode aplicar um ângulo adicional a este vetor fornecendo o parâmetro
        _theta.'''

        theta += self._theta
        return Vec2(cos(theta), sin(theta))

    def torque(self, t):
        '''Define uma torque externo análogo ao método .force()'''

        return 0.0

    def init_alpha(self):
        '''Inicializa o vetor de aceleração angular com os valores devido ao
        amortecimento'''

        self._alpha = - self._adamping * self._omega

    def apply_torque(self, torque, dt):
        '''Aplica um torque durante um intervalo de tempo dt.'''

        self.apply_alpha(torque * self._invinertia, dt)

    def apply_alpha(self, alpha, dt):
        '''Aplica uma aceleração angular durante um intervalo de tempo dt.

        Tem efeito em objetos cinemáticos.'''

        if alpha is None:
            alpha = self._alpha
        self.aboost(alpha * dt)
        self.rotate(self._omega * dt + alpha * dt ** 2 / 2.)

    def apply_aimpulse(self, itorque):
        '''Aplica um impulso angular ao objeto.'''

        self.aboost(itorque / self.inertia)

    ###########################################################################
    #                    Controle de forças locais/globais
    ###########################################################################

    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value):
        try:
            self._gravity = Vec2(*value)
        except TypeError:
            self._gravity = Vec2(0, -value)
        self.flags |= flags.owns_gravity

    @property
    def damping(self):
        return self._damping

    @damping.setter
    def damping(self, value):
        self._damping = float(value)
        self.flags |= flags.owns_damping

    @property
    def adamping(self):
        return self._adamping

    @adamping.setter
    def adamping(self, value):
        self._adamping = float(value)
        self.flags |= flags.owns_adamping

    @property
    def restitution(self):
        return self._restitution

    @restitution.setter
    def restitution(self, value):
        self._restitution = float(value)
        self.flags |= flags.owns_restitution

    @property
    def dfriction(self):
        return self._dfriction

    @dfriction.setter
    def dfriction(self, value):
        self._dfriction = float(value)
        self.flags |= flags.owns_dfriction

    @property
    def sfriction(self):
        return self._sfriction

    @sfriction.setter
    def sfriction(self, value):
        self._sfriction = float(value)
        self.flags |= flags.owns_sfriction

    @property
    def owns_gravity(self):
        return bool(self.flags & flags.owns_gravity)

    @property
    def owns_damping(self):
        return bool(self.flags & flags.owns_damping)

    @property
    def owns_adamping(self):
        return bool(self.flags & flags.owns_adamping)

    @property
    def owns_restitution(self):
        return bool(self.flags & flags.owns_restitution)

    @property
    def owns_dfriction(self):
        return bool(self.flags & flags.owns_dfriction)

    @property
    def owns_sfriction(self):
        return bool(self.flags & flags.owns_sfriction)

    ###########################################################################
    #               Manipulação/consulta do estado dinâmico
    ###########################################################################
    # Simplificar e usar apenas a massa e a flag can_rotate como quesito de
    # teste.
    # FIXME: Alterar as flags nas funções make_*
    def is_dynamic(self, what=None):
        '''Retorna True se o objeto for dinâmico ou nas variáveis lineares ou
        nas angulares. Um objeto é considerado dinâmico nas variáveis lineares
        se possuir massa finita. De maneira análoga, o objeto torna-se dinâmico
        nas variáveis angulares se possuir momento de inércia finito.

        Opcionalmente pode especificar um parâmetro posicional 'linear',
        'angular', 'both' or 'any' (padrão) para determinar o tipo de consulta
        a ser realizada'''

        if what is None or what == 'any':
            return self.is_dynamic_linear() or self.is_dynamic_angular()
        elif what == 'both':
            return self.is_dynamic_linear() and self.is_dynamic_angular()
        elif what == 'linear':
            return self.is_dynamic_linear()
        elif what == 'angular':
            return self.is_dynamic_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def is_dynamic_linear(self):
        '''Verifica se o objeto é dinâmico nas variáveis lineares'''

        return bool(self._invmass)

    def is_dynamic_angular(self):
        '''Verifica se o objeto é dinâmico nas variáveis angulares'''

        return bool(self._invinertia)

    def make_dynamic(self, what=None, restore_speed=True):
        '''Resgata a massa, inércia e velocidades anteriores de um objeto
        paralizado pelo método `obj.make_static()` ou `obj.make_kinematic()`.

        Aceita um argumento com a mesma semântica de is_dynamic()
        '''

        if what is None or what == 'both':
            self.make_dynamic_linear(restore_speed)
            self.make_dynamic_angular(restore_speed)
        elif what == 'linear':
            self.make_dynamic_linear(restore_speed)
        elif what == 'angular':
            self.make_dynamic_angular(restore_speed)
        else:
            raise ValueError('unknown mode: %r' % what)

    def make_dynamic_linear(self, restore_speed=True):
        '''Resgata os parâmetros dinâmicos lineares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        if not self.is_dynamic_linear():
            self._invmass = 1.0 / (self.area() * self._density)

            # Resgata a velocidade
            if restore_speed and self._vel.is_null():
                self._vel = popattr(self, '_old_vel', null2D)

    def make_dynamic_angular(self, restore_speed=True):
        '''Resgata os parâmetros dinâmicos angulares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        if not self.is_dynamic_angular():
            self._inertia = 1.0 / (self._density * self.ROG_sqr())

            # Resgata a velocidade
            if restore_speed and self._omega == 0:
                self._omega = popattr(self, '_old_omega', 0.0)

    # Kinematic ###############################################################
    def is_kinematic(self, what=None):
        '''Retorna True se o objeto for cinemático ou nas variáveis lineares ou
        nas angulares. Um objeto é considerado cinemático (em uma das
        variáveis) se não for dinâmico. Se, além de cinemático, o objeto
        possuir velocidade nula, ele é considerado estático.

        Opcionalmente pode especificar um parâmetro posicional 'linear',
        'angular', 'both' (padrão) or 'any' para determinar o tipo de consulta
        a ser realizada.
        '''

        if what is None or what == 'both':
            return not (self.is_dynamic_linear() or self.is_dynamic_angular())
        elif what == 'any':
            return (
                not self.is_dynamic_linear()) or (
                not self.is_dynamic_angular())
        elif what == 'linear':
            return not self.is_dynamic_linear()
        elif what == 'angular':
            return not self.is_dynamic_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def is_kinematic_linear(self):
        '''Verifica se o objeto é dinâmico nas variáveis lineares'''

        return not self.is_dynamic_linear()

    def is_kinematic_angular(self):
        '''Verifica se o objeto é dinâmico nas variáveis angulares'''

        return not self.is_dynamic_angular()

    def make_kinematic(self, what=None):
        '''Define a massa e/ou inércia como infinito.

        Aceita um argumento com a mesma semântica de is_kinematic()
        '''

        if what is None or what == 'both':
            self.make_kinematic_linear()
            self.make_kinematic_angular()
        elif what == 'linear':
            self.make_kinematic_linear()
        elif what == 'angular':
            self.make_kinematic_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def make_kinematic_linear(self):
        '''Resgata os parâmetros dinâmicos lineares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        self._invmass = 0.0

    def make_kinematic_angular(self):
        '''Resgata os parâmetros dinâmicos angulares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        self._invinertia = 0.0

    # Static ##################################################################
    def is_static(self, what=None):
        '''Retorna True se o objeto for estatático nas variáveis lineares e
        nas angulares. Um objeto é considerado estático (em uma das variáveis)
        se além de cinemático, a velocidade for nula.

        Opcionalmente pode especificar um parâmetro posicional 'linear',
        'angular', 'both' (padrão) or 'any' para determinar o tipo de consulta
        a ser realizada'''

        if what is None or what == 'both':
            return self.is_static_linear() and self.is_static_angular()
        elif what == 'any':
            return self.is_static_linear() or self.is_static_angular()
        elif what == 'linear':
            return self.is_static_linear()
        elif what == 'angular':
            return self.is_static_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def is_static_linear(self):
        '''Verifica se o objeto é dinâmico nas variáveis lineares'''

        return self.is_kinematic_linear() and self._vel == null2D

    def is_static_angular(self):
        '''Verifica se o objeto é dinâmico nas variáveis angulares'''

        return self.is_kinematic_angular() and self._omega == 0

    def make_static(self, what=None):
        '''Define a massa e/ou inércia como infinito.

        Aceita um argumento com a mesma semântica de is_static()
        '''

        if what is None or what == 'both':
            self.make_static_linear()
            self.make_static_angular()
        elif what == 'linear':
            self.make_static_linear()
        elif what == 'angular':
            self.make_static_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def make_static_linear(self):
        '''Resgata os parâmetros dinâmicos lineares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        self.make_kinematic_linear()
        self._old_vel = self._vel
        self._vel = null2D

    def make_static_angular(self):
        '''Resgata os parâmetros dinâmicos angulares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        self.make_kinematic_angular()
        self._old_omega = self._omega
        self._omega = 0.0

    ###########################################################################
    # Erros e miscelânea
    ###########################################################################
    def _raise_cannot_rotate_error(self):
        raise ValueError('Cannot change angular variables with disabled '
                         '`can_rotate` flag')


def vec_property(slot):
    '''Fabrica um slot que força a conversão de uma variável para a classe
    vetor.'''

    getter = slot.__get__
    setter = slot.__set__

    class VecProperty(object):
        __slots__ = []

        def __set__(self, obj, value):
            if not isinstance(value, Vec2):
                value = Vec2(value)
            setter(obj, value)

        def __get__(self, obj, cls):
            if obj is None:
                return self
            else:
                return getter(obj, cls)

    return VecProperty()

Body.pos = vec_property(Body._pos)
Body.vel = vec_property(Body._vel)
Body.accel = vec_property(Body._accel)

###############################################################################
# Linear rigid bodies
###############################################################################
# TODO: remover esta classe e se basear no comportamento da flag can_rotate


class LinearRigidBody(Body):

    '''
    Classe que implementa corpos rígidos sem dinâmica angular.
    '''

    __slots__ = []
    DEFAULT_FLAGS = Body.DEFAULT_FLAGS & (flags.full ^ flags.can_rotate)

    def __init__(self, pos=(0, 0), vel=(0, 0),
                 mass=None, density=None, **kwds):

        super(LinearRigidBody, self).__init__(pos, vel, 0.0, 0.0,
                                              mass=mass, density=density,
                                              inertia='inf',
                                              flags=self.DEFAULT_FLAGS, **kwds)

    @property
    def inertia(self):
        return INF

    @inertia.setter
    def inertia(self, value):
        if float(value) != INF:
            raise ValueError('LinearObjects have infinite inertia, '
                             'got %r' % value)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
