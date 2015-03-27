# -*- coding: utf8 -*-

import six
from FGAme.core import EventDispatcher, EventDispatcherMeta, signal
from FGAme.mathutils import Vector, VectorM, asvector, dot, cross, sqrt

__all__ = ['Dynamic']


###############################################################################
#                                 Funções úteis
###############################################################################

NOT_IMPLEMENTED = NotImplementedError('must be implemented at child classes')
INF = float('inf')
ORIGIN = Vector(0, 0)


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
                        method.__doc__ = other.__doc__
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

    '''

    __slots__ = [
        'flags', 'cbb_radius',
        '_pos', '_vel', '_accel', '_theta', '_omega', '_alpha',
        '_invmass', '_invinertia'
    ]

    def __init__(self, pos=(0, 0), vel=(0, 0), theta=0.0, omega=0.0,
                 mass=1.0, inertia=1.0):
        EventDispatcher.__init__(self)

        self.flags = 0

        self._pos = VectorM(*pos)
        self._vel = VectorM(*vel)
        self._theta = float(theta)
        self._omega = float(omega)

        self._accel = VectorM(0, 0)
        self._alpha = 0.0

        self._invmass = self._invinertia = 1.0
        self.mass = mass
        self.inertia = inertia

    ###########################################################################
    #                            Serviços Python
    ###########################################################################

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)

    def __repr__(self):
        tname = type(self).__name__
        pos = ', '.join('%.1f' % x for x in self.pos)
        vel = ', '.join('%.1f' % x for x in self.vel)
        return '%s(pos=(%s), vel=(%s))' % (tname, pos, vel)

    # TODO: def __copy__(self): ?
    # TODO: def __getstate__(self): ?

    # Sinais
    collision = signal('collision', num_args=1)

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
            if self.vel == ORIGIN:
                self.vel = self._getp('old_vel', ORIGIN)

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

        return self.is_kinematic_linear() and self.vel == ORIGIN

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
        if self.vel != ORIGIN:
            self._old_vel = self.vel
            self.vel = (0, 0)

    def make_static_angular(self):
        '''Resgata os parâmetros dinâmicos angulares de um objeto estático ou
        cinemático paralizado pelos métodos `obj.make_static()` ou
        `obj.make_kinematic()`.'''

        self.make_kinematic_angular()
        if self.omega != 0:
            self._old_omega = self.omega
            self.omega = 0.0

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

    # Variáveis de estado
#     @property
#     def pos(self):
#         return Vector(*self._pos)
#
#     @pos.setter
#     def pos(self, value):
#         self.move(value - self._pos)
#     @property
#     def vel(self):
#         return Vector(*self._vel)
#
#     @vel.setter
#     def vel(self, value):
#         self.boost(value - self._vel)
#
#     @property
#     def accel(self):
#         return Vector(*self._accel)
#
#     @accel.setter
#     def accel(self, value):
#         self._accel.update(value)

    # Grandezas físicos derivadas
    def linearE(self):
        '''Energia cinética das variáveis lineares'''

        return dot(self.vel, self.vel) / (2 * self._invmass)

    def angularE(self):
        '''Energia cinética das variáveis angulares'''

        if self.omega:
            return self.omega ** 2 / (2 * self._invinertia)
        else:
            return 0

    def kineticE(self):
        '''Energia cinética total'''

        return self.linearE() + self.angularE()

    def momentumP(self):
        '''Momentum linear'''

        return self.vel / self._invmass

    def momentumL(self):
        '''Momentum angular em torno do centro de massa'''

        if self.omega:
            return self.inertia * self.omega
        else:
            return 0.0

    def momentumL_origin(self):
        '''Momentum angular em torno da origem'''

        return cross(self.pos, self.momentumP()) + self.momentumL()

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
            self._vel += (delta_or_x, y)

    # Resposta a forças, impulsos e atualização da física #####################
    def force(self, t):
        '''Define uma força externa que depende do tempo t.

        Pode ser utilizado por sub-implementações para definir uma força
        externa aplicada aos objetos de uma sub-classe ou usando o recurso de
        "monkey patching" do Python
        '''

        return ORIGIN

    def init_accel(self):
        '''Inicializa o vetor de aceleração com o valor nulo'''

        self._accel *= 0

    def apply_force(self, force, dt, pos=None, relative=False):
        '''Aplica uma força linear durante um intervalo de tempo dt'''

        if force is None:
            if self._invmass:
                self.apply_accel(self._accel, dt)
        else:
            self.apply_accel(force * self._invmass, dt)

        if pos is not None:
            if relative:
                tau = cross(pos, force)
            else:
                tau = cross(pos - self._pos, force)
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
        if a is None:
            a = self._accel
        else:
            a = asvector(a)

        self.move(self._vel * dt + a * (dt ** 2 / 2.0))
        self.boost(a * dt)

    def apply_impulse(self, impulse_or_x, y=None):
        '''Aplica um impulso linear ao objeto. Isto altera sua velocidade
        linear com relação ao centro de massa.

        Se for chamado com dois agumentos aplica o impulso em um ponto
        específico e também resolve a dinâmica angular.
        '''

        if y is None:
            self.boost(impulse_or_x * self._invmass)
        else:
            self.boost(Vector(impulse_or_x, y) * self._invmass)

    # Variáveis angulares #####################################################
    def rotate(self, theta):
        '''Rotaciona o objeto por um ângulo theta'''

        self._theta += theta

    def aboost(self, delta):
        '''Adiciona um valor delta à velocidade ângular'''

        self._omega += delta

    def vpoint(self, pos_or_x, y=None, relative=False):
        '''Retorna a velocidade linear de um ponto em pos preso rigidamente ao
        objeto.

        Se o parâmetro `relative` for verdadeiro, o vetor `pos` é interpretado
        como a posição relativa ao centro de massa. O padrão é considerá-lo
        como a posição absoluta no centro de coordenadas do mundo.'''

        if relative:
            if y is None:
                x, y = pos_or_x
                return self._vel + self._omega * Vector(-y, x)
            else:
                return self._vel + self._omega * Vector(-y, pos_or_x)

        else:
            if y is None:
                x, y = pos_or_x - self._pos
                return self._vel + self._omega * Vector(-y, x)
            else:
                x = pos_or_x - self._pos.x
                y = y - self._pos.y
                return self._vel + self._omega * Vector(-y, x)

    def torque(self, t):
        '''Define uma torque externo análogo ao método .force()'''

        return None

    def init_alpha(self):
        '''Reinicializa a aceleração angular com o valor nulo.'''

        self._alpha = 0

    def apply_torque(self, torque, dt):
        '''Aplica um torque durante um intervalo de tempo dt.'''

        self.apply_alpha(torque * self._invinertia, dt)

    def apply_alpha(self, alpha, dt):
        '''Aplica uma aceleração angular durante um intervalo de tempo dt.

        Tem efeito em objetos cinemáticos.'''

        dt = dt / 2
        self.aboost(alpha * dt)
        self.rotate(self._omega * dt + alpha * dt ** 2 / 2.)

    def apply_aimpulse(self, itorque):
        '''Aplica um impulso angular ao objeto.'''

        self.aboost(itorque / self.inertia)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
