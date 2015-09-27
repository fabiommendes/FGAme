# -*- coding: utf8 -*-
import copy
import six
from FGAme.events import EventDispatcher, EventDispatcherMeta, signal
from FGAme.mathtools import Vec2, asvector, sin, cos, null2D, shapes
from FGAme.physics.flags import BodyFlags as flags
from FGAme.physics.forces import ForceProperty
from FGAme.physics.bodies.body_interfaces import (HasAABB, HasGlobalForces,
                                                  HasInertia)

__all__ = ['Body', 'LinearRigidBody']


###############################################################################
#                              Funções úteis
###############################################################################
NOT_IMPLEMENTED = NotImplementedError('must be implemented at child classes')
INERTIA_SCALE = 1
INF = float('inf')


def flag_property(flag):
    '''Retorna uma propriedade que controla a flag especificada no argumento'''

    def fget(self):
        return self.flags & flag

    def fset(self, value):
        if value:
            self.flags |= flag
        else:
            self.flags &= ~flag
    return property(fget, fset)

# TODO: mover para FGAme.util


def do_nothing(*args, **kwds):
    '''A handle that does nothing'''


def raises_method(exception=NOT_IMPLEMENTED):
    '''Returns a method that raises the given exception'''

    def method(self, *args, **kwds):
        raise exception
    return method


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
class Body(HasAABB, HasGlobalForces, HasInertia):

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
                 restitution=None, friction=None,
                 baseshape=None, world=None, col_layer=0, col_group=0,
                 flags=DEFAULT_FLAGS):

        self._world = world
        EventDispatcher.__init__(self)

        # Flags de objeto
        self.flags = flags

        # Variáveis de estado #################################################
        self._pos = asvector(pos)
        self._vel = asvector(vel)
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
            try:
                density = mass / self.area()
            except ZeroDivisionError:
                density = float('inf')
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
        self._friction = 0.0
        self._restitution = 1.0
        if damping is not None:
            self.damping = damping
        if adamping is not None:
            self.adamping = adamping
        if gravity is not None:
            self.gravity = gravity
        if restitution is not None:
            self.restitution = restitution
        if friction is not None:
            self.friction = friction

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

        return shapes.Circle(self.cbb_radius, self.pos)

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

    #
    # Propriedades definidas por flags
    #
    can_rotate = flag_property(flags.can_rotate)
    owns_gravity = flag_property(flags.owns_gravity)
    owns_damping = flag_property(flags.owns_damping)
    owns_adamping = flag_property(flags.owns_adamping)
    owns_restitution = flag_property(flags.owns_restitution)
    owns_friction = flag_property(flags.owns_friction)

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
            self.flags |= flags.active

    def is_rogue(self):
        '''Retorna True se o objeto não estiver associado a uma simulação'''

        return (self._world is None)

    def destroy(self):
        '''Destrói o objeto físico'''

        if not self.is_rogue():
            if self in self.world:
                self.world.remove(self)

        # TODO: desaloca todos os sinais

    def copy(self):
        '''Cria uma cópia do objeto'''

        try:
            world, self._world = self._world, None
            cp = copy.copy(self)
        finally:
            self._world = world
        return cp

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
    force = ForceProperty()

    def linearK(self):
        '''Energia cinética das variáveis lineares'''

        if self._invmass:
            return self._vel.norm_sqr() / (2 * self._invmass)
        else:
            return 0.0

    def angularK(self):
        '''Energia cinética das variáveis angulares'''

        if self._invinertia:
            return self._omega ** 2 / (2 * self._invinertia)
        else:
            return 0.0

    def energyK(self):
        '''Energia cinética total'''

        return self.linearK() + self.angularK()

    def energyU(self):
        '''Energia potencial associada à gravidade e às forças externas'''

        return -self.gravity.dot(self._pos) / self._invmass

    def energy(self):
        '''Energia total do objeto'''

        return self.energyK() + self.energyU()

    def momentumP(self):
        '''Momentum linear'''

        try:
            return self._vel / self._invmass
        except ZeroDivisionError:
            return Vec2(float('inf'), float('inf'))

    def momentumL(self, pos_or_x=None, y=None):
        '''Momentum angular em torno do ponto dado (usa o centro de massa
        como padrão)

        Examples
        --------

        Considere uma partícula no ponto (0, 1) com velocidade (1, 0). É fácil
        calcular o momentum linear resultante

        >>> b1 = Body(pos=(0, 1), vel=(1, 0), mass=2)
        >>> b1.momentumL(0, 0)
        -2.0

        É lógico que este valor muda de acordo com o ponto de referência

        >>> b1.momentumL(0, 2)
        2.0

        Quando chamamos a função sem argumentos, o padrão é utilizar o centro
        de massa. Numa partícula pontual sem velocidade angular, este valor é
        sempre zero

        >>> b1.momentumL(b1.pos)
        0.0


        '''

        if pos_or_x is None:
            momentumL = 0.0
        elif y is None:
            delta_pos = self.pos - asvector(pos_or_x)
            momentumL = delta_pos.cross(self.momentumP())
        else:
            delta_pos = self.pos - Vec2(pos_or_x, y)
            momentumL = delta_pos.cross(self.momentumP())

        if self._invinertia:
            return momentumL + self.omega * self.inertia
        else:
            return momentumL

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

    def apply_accel(self, a, dt, method=None):
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

            x(t + dt) = x(t) + v(t) * dt
            v(t + dt) = v(t) + a(t) * dt

        Em código Python,

        >>> self.move(self.vel * dt + a * (dt**2/2))           # doctest: +SKIP
        >>> self.boost(a * dt)                                 # doctest: +SKIP

        Este método simples e intuitivo sofre com o efeito da "deriva de
        energia". Devido aos erros de aproximação, o valor da energia da
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
        a = asvector(a)

        if method is None or method == 'euler-semi-implicit':
            self.boost(a * dt)
            self.move(self._vel * dt + a * (0.5 * dt * dt))
        elif method == 'verlet':
            raise NotImplementedError
        elif method == 'euler':
            self.move(self._vel * dt + a * (0.5 * dt * dt))
            self.boost(a * dt)
        else:
            raise ValueError('invalid method: %r' % method)

    def apply_impulse(self, impulse_or_x, y=None, pos=None, relative=False):
        '''Aplica um impulso linear ao objeto. Isto altera sua velocidade
        linear com relação ao centro de massa.

        Se for chamado com dois agumentos aplica o impulso em um ponto
        específico e também resolve a dinâmica angular.

        Examples
        --------

        Considere um objeto criado na origem e outro na posição (4, 3)

        >>> b1 = Body(pos=(2, 0), mass=1)
        >>> b2 = Body(pos=(-1, 0), mass=2)

        Criamos um impulso J e aplicamos o mesmo em b1

        >>> J = Vec2(0, 2)
        >>> b1.apply_impulse(J)

        Note que isto afeta a velocidade do corpo de acordo com a fórmula
        $\delta v = J / m$:

        >>> b1.vel
        Vec(0, 2)

        Se aplicarmos um impulso oposto à b2, o resultado não deve alterar o
        momento linear, que permanece nulo

        >>> b2.apply_impulse(-J, pos=(0, 0)); b2.vel
        Vec(0, -1)
        >>> b1.momentumP() + b2.momentumP()
        Vec(0, 0)

        O exemplo anterior é bastante simples pois os dois objetos não possuem
        momentum de inércia. As mesmas leis de conservação valem na presença
        de rotações ou mesmo de velocidades iniciais

        >>> b1 = Body(pos=(0, 0), mass=1, inertia=1, vel=(2, 0), omega=1)
        >>> b2 = Body(pos=(4, 3), mass=2, inertia=2, vel=(-1, 1))

        Primeiro calculamos os momentos iniciais

        >>> P0 = b1.momentumP() + b2.momentumP()

        Note que o momentum linear exige um ponto de referência para a
        realização do cálculo. Escolhemos o centro de massa, mas os resultados
        devem valer para qualquer escolha arbitrária.

        >>> from FGAme.physics import center_of_mass
        >>> Rcm = center_of_mass(b1, b2)
        >>> L0 = b1.momentumL(Rcm) + b2.momentumL(Rcm)

        Aplicamos momentos opostos respeitando a terceira lei de Newton. Note
        que no problema com rotações devemos tomar cuidado em aplicar o impulso
        no mesmo ponto nos dois objetos. Caso isto não ocorra, haverá a
        produção de um torque externo, violando a lei de conservação do momento
        angular.

        >>> b1.apply_impulse(J, pos=(4, 0))
        >>> b2.apply_impulse(-J, pos=(4, 0))

        E verificamos que os valores finais são iguais aos iniciais

        >>> b1.momentumP() + b2.momentumP() == P0
        True
        >>> b1.momentumL(Rcm) + b2.momentumL(Rcm) == L0
        True
        '''

        if y is None:
            impulse = asvector(impulse_or_x)
        else:
            impulse = Vec2(impulse_or_x, y)
        self.boost(impulse * self._invmass)

        if pos is not None and self._invinertia:
            R = asvector(pos)
            R = R if relative else R - self.pos
            self.aboost(R.cross(impulse) * self._invinertia)

    # Variáveis angulares #####################################################
    def rotate(self, theta):
        '''Rotaciona o objeto por um ângulo _theta'''

        self._theta += theta
        if theta != 0.0:
            self.flags |= flags.dirty_any

    def aboost(self, delta):
        '''Adiciona um valor delta à velocidade angular'''

        self._omega += delta

    def vpoint(self, pos_or_x, y=None, relative=False):
        '''Retorna a velocidade linear de um ponto preso rigidamente ao
        objeto.

        Se o parâmetro `relative` for verdadeiro, o vetor de entrada é
        interpretado como a posição relativa ao centro de massa. O padrão é
        considerá-lo como a posição absoluta no sistema de coordenadas do
        mundo.

        Example
        -------

        Criamos um objeto inicialmente sem rotação

        >>> b1 = Body(pos=(1, 1), vel=(1, 1), mass=1, inertia=1)

        Neste caso, a velocidade relativa a qualquer ponto corresponde à
        velocidade do centro de massa

        >>> b1.vpoint(0, 0), b1.vpoint(1, 1)
        (Vec(1, 1), Vec(1, 1))

        Quando aplicamos uma rotação, a velocidade em cada ponto assume uma
        componente rotacional.

        >>> b1.aboost(1.0)
        >>> b1.vpoint(0, 0), b1.vpoint(1, 1)
        (Vec(2, 0), Vec(1, 1))

        Note que quando o parâmetro ``relative=True``, as posições são
        calculadas relativas ao centro de massa do objeto

        >>> b1.vpoint(0, 0, relative=True), b1.vpoint(1, 1, relative=True)
        (Vec(1, 1), Vec(0, 2))
        '''

        if y is None:
            pos = asvector(pos_or_x)
        else:
            pos = Vec2(pos_or_x, y)

        if not relative:
            pos -= self.pos

        return self._vel + pos.perp() * self._omega

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

    def apply_aimpulse(self, angular_delta):
        '''Aplica um impulso angular ao objeto.

        O parâmetro de entrada corresponde à variação do momento angular do
        objeto.
        '''

        self.aboost(angular_delta * self._invinertia)


def vec_property(slot):
    '''Fabrica um slot que força a conversão de uma variável para a classe
    vetor.'''

    getter = slot.__get__
    setter = slot.__set__

    class VecProperty(object):
        __slots__ = []

        def __set__(self, obj, value):
            if not isinstance(value, Vec2):
                value = asvector(value)
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
