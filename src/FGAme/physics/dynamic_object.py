# -*- coding: utf8 -*-
from FGAme.core import EventDispatcher, EventDispatcherMeta, signal
from FGAme.mathutils import Vec2
from FGAme.mathutils import sqrt, sin, cos, null2D
from FGAme import mathutils as shapes
from FGAme.util import six
from FGAme.physics import flags


__all__ = ['Dynamic']


###############################################################################
#                                 Funções úteis
###############################################################################

NOT_IMPLEMENTED = NotImplementedError('must be implemented at child classes')
INF = float('inf')
ORIGIN = Vec2(0, 0)


def do_nothing(*args, **kwds):
    pass


def raises_method(ex=NOT_IMPLEMENTED):
    def method(self, *args, **kwds):
        raise ex
    return method

###############################################################################
#          Classes Base --- todos objetos físicos derivam delas
###############################################################################
Dynamic = None


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
            if Dynamic is None:
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
class Dynamic(object):

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

    '''

    __slots__ = [
        'flags', 'cbb_radius',
        '_pos', '_vel', '_accel', 'theta', 'omega', 'alpha',
        '_invmass', '_invinertia', '_e_vel', '_e_omega',
    ]

    def __init__(self, pos=(0, 0), vel=(0, 0), theta=0.0, omega=0.0,
                 mass=1.0, inertia=1.0,
                 gravity=None, damping=None, adamping=None,
                 owns_gravity=None, owns_damping=None, owns_adamping=None):

        EventDispatcher.__init__(self)

        # Flags de objeto
        self.flags = 0

        # Variáveis de estado
        self._pos = Vec2(*pos)
        self._vel = Vec2(*vel)
        self._e_vel = Vec2(0, 0)
        self._e_omega = 0.0
        self.theta = float(theta)
        self.omega = float(omega)

        # Acelerações
        self._accel = Vec2(0, 0)
        self.alpha = 0.0

        # Inércias
        self._invmass = self._invinertia = 1.0
        self.mass = mass
        self.inertia = inertia

        # Controle de gravidade/damping/adamping locais
        self._damping = float(damping or 0.0)
        self._adamping = float(adamping or 0.0)
        if damping is not None:
            self.flags |= flags.OWNS_DAMPING
        if adamping is not None:
            self.flags |= flags.OWNS_ADAMPING
        if gravity is None:
            self._gravity = Vec2(0, 0)
        else:
            self.gravity = gravity

        # Controle de is_sleep
        self.is_sleep = False

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

        return shapes.AABB(self.xmin, self.xmax, self.ymin, self.ymax)

    @property
    def shape_bb(self):
        '''Retorna o formato da caixa de contorno que melhor envolve o objeto
        (pode ser um círculo, AABB ou poĺígono)'''

        return NotImplemented

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
    #                    Controle de criação e destruição
    ###########################################################################
    def is_rogue(self):
        '''Retorna True se o objeto não estiver associado a uma simulação'''

        return getattr(self, 'simulation', None) is not None

    def destroy(self):
        '''Destrói o objeto físico'''

        if not self.is_rogue():
            self.simulation.remove(self)

        # TODO: desaloca todos os sinais

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
        self._invmass = 1.0 / value

    @property
    def inertia(self):
        try:
            return 1.0 / self._invinertia
        except ZeroDivisionError:
            return float('inf')

    @inertia.setter
    def inertia(self, value):
        value = float(value)
        if value <= 0:
            raise ValueError('inertia cannot be null or negative')
        self._invinertia = 1.0 / value

    # Grandezas físicas derivadas
    def linearE(self):
        '''Energia cinética das variáveis lineares'''

        return self._vel.dot(self._vel) / (2 * self._invmass)

    def angularE(self):
        '''Energia cinética das variáveis angulares'''

        if self.omega:
            return self.omega ** 2 / (2 * self._invinertia)
        else:
            return 0

    def kineticE(self):
        '''Energia cinética total'''

        return self.linearE() + self.angularE()

    def potentialE(self):
        '''Energia potencial associada à gravidade'''

        return self.gravity.dot(self._pos) / self._invmass

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
            delta = (self._pos - pos).cross(self._vel)
        if self.omega:
            return delta + self.inertia * self.omega
        else:
            return delta

    ###########################################################################
    #                        Propriedades Geométricas
    ###########################################################################
    def area(self):
        '''Retorna a área do objeto'''

        raise NotImplementedError('must be implemented in child classes')

    def ROG_sqr(self):
        '''Retorna o raio de giração ao quadrado'''

        raise NotImplementedError('must be implemented in child classes')

    def ROG(self):
        '''Retorna o raio de giração'''

        return sqrt(self.ROG_sqr())

    ###########################################################################
    #                      Aplicação de forças e torques
    ###########################################################################
    def move(self, delta_or_x, y=None):
        '''Move o objeto por vetor de deslocamento delta'''

        if y is None:
            self._pos += delta_or_x
        else:
            self._pos += (delta_or_x, y)

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

        return ORIGIN

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

    def update_linear(self, dt):
        '''Aplica aceleração linear acumulada pelo objeto ao longo do frame'''

        self.apply_accel(self._accel, dt)

    def update_angular(self, dt):
        '''Aplica aceleração angular acumulada pelo objeto ao longo do frame'''

        self.apply_alpha(self._alpha, dt)

    # Variáveis angulares #####################################################
    def rotate(self, theta):
        '''Rotaciona o objeto por um ângulo theta'''

        self.theta += theta

    def aboost(self, delta):
        '''Adiciona um valor delta à velocidade ângular'''

        self.omega += delta

    def vpoint(self, pos_or_x, y=None, relative=False):
        '''Retorna a velocidade linear de um ponto em _pos preso rigidamente ao
        objeto.

        Se o parâmetro `relative` for verdadeiro, o vetor `_pos` é interpretado
        como a posição relativa ao centro de massa. O padrão é considerá-lo
        como a posição absoluta no centro de coordenadas do mundo.'''

        if relative:
            if y is None:
                x, y = pos_or_x
                return self._vel + self.omega * Vec2(-y, x)
            else:
                return self._vel + self.omega * Vec2(-y, pos_or_x)

        else:
            if y is None:
                x, y = pos_or_x - self._pos
                return self._vel + self.omega * Vec2(-y, x)
            else:
                x = pos_or_x - self._pos.x
                y = y - self._pos.y
                return self._vel + self.omega * Vec2(-y, x)

    def orientation(self, theta=0.0):
        '''Retorna um vetor unitário na direção em que o objeto está orientado.
        Pode aplicar um ângulo adicional a este vetor fornecendo o parâmetro
        theta.'''

        theta += self.theta
        return Vec2(cos(theta), sin(theta))

    def torque(self, t):
        '''Define uma torque externo análogo ao método .force()'''

        return 0.0

    def init_alpha(self):
        '''Inicializa o vetor de aceleração angular com os valores devido ao
        amortecimento'''

        self._alpha = - self._adamping * self.omega

    def apply_torque(self, torque, dt):
        '''Aplica um torque durante um intervalo de tempo dt.'''

        self.apply_alpha(torque * self._invinertia, dt)

    def apply_alpha(self, alpha, dt):
        '''Aplica uma aceleração angular durante um intervalo de tempo dt.

        Tem efeito em objetos cinemáticos.'''

        if alpha is None:
            alpha = self._alpha
        self.aboost(alpha * dt)
        self.rotate(self.omega * dt + alpha * dt ** 2 / 2.)

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

    @property
    def owns_gravity(self):
        return bool(self.flags & flags.OWNS_GRAVITY)

    @property
    def owns_damping(self):
        return bool(self.flags & flags.OWNS_DAMPING)

    @property
    def owns_adamping(self):
        return bool(self.flags & flags.OWNS_ADAMPING)

    ###########################################################################
    #               Manipulação/consulta do estado dinâmico
    ###########################################################################

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

    def make_dynamic(self, what=None):
        '''Resgata a massa, inércia e velocidades anteriores de um objeto
        paralizado pelo método `obj.make_static()` ou `obj.make_kinematic()`.

        Aceita um argumento com a mesma semântica de is_dynamic()
        '''

        if what is None or what == 'both':
            self.make_dynamic_linear()
            self.make_dynamic_angular()
        elif what == 'linear':
            self.make_dynamic_linear()
        elif what == 'angular':
            self.make_dynamic_angular()
        else:
            raise ValueError('unknown mode: %r' % what)

    def make_dynamic_linear(self):
        '''Resgata os parâmetros dinâmicos lineares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        if not self.is_dynamic_linear():
            # Regata a massa
            mass = self._getp('old_mass', None)
            if mass is None:
                raise RuntimeError('old mass is not available for recovery')
            else:
                self.mass = mass

            # Resgata a velocidade
            if self._vel == ORIGIN:
                self._vel = self._getp('old_vel', ORIGIN)

        self._clearp('old_mass', 'old_vel')

    def make_dynamic_angular(self):
        '''Resgata os parâmetros dinâmicos angulares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        if not self.is_dynamic_angular():
            # Regata a massa
            inertia = self._getp('old_inertia', None)
            if inertia is None:
                raise RuntimeError('old inertia is not available for recovery')
            else:
                self.inertia = inertia

            # Resgata a velocidade
            if self.omega == 0:
                self.omega = self._getp('old_omega', 0)

        self._clearp('old_inertia', 'old_omega')

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

        if not self.is_kinematic_linear():
            self._old_mass = self.mass
            self.mass = 'inf'

    def make_kinematic_angular(self):
        '''Resgata os parâmetros dinâmicos angulares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        if not self.is_kinematic_angular():
            self._old_inertia = self.inertia
            self.inertia = 'inf'

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

        return self.is_kinematic_linear() and self._vel == ORIGIN

    def is_static_angular(self):
        '''Verifica se o objeto é dinâmico nas variáveis angulares'''

        return self.is_kinematic_angular() and self.omega == 0

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
        if self._vel != ORIGIN:
            self._old_vel = self._vel
            self._vel = Vec2(0, 0)

    def make_static_angular(self):
        '''Resgata os parâmetros dinâmicos angulares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        self.make_kinematic_angular()
        if self.omega != 0:
            self._old_omega = self.omega
            self.omega = 0.0


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

Dynamic.pos = vec_property(Dynamic._pos)
Dynamic.vel = vec_property(Dynamic._vel)
Dynamic.accel = vec_property(Dynamic._accel)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
