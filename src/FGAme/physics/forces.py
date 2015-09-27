# -*- coding: utf8 -*-
'''
======
Forças
======

Forças externas podem ser inseridas manualmente nos objetos físicos da FGAme
através do atributo obj.force das instâncias de `Body()` ou criadas através de
um objeto da classe Force().

No caso mais simples, podemos simplesmente atribuir uma função que retorna o
vetor de força como função do tempo:

>>> from FGAme import Circle
>>> obj = Circle(5)
>>> obj.force = lambda t: (4, 3) - obj.pos

Neste caso, podemos simplesmente calcular a força chamando

>>> obj.force(0)
Vec(4, 3)

O attributo obj.force aceita várias regras de composição. A mais útil delas,
de soma de forças, permite aplicar várias forças externas a um mesmo objeto.

>>> obj.force += lambda t: (10, 10)

Neste caso, a composição de forças corresponde à adição dos valores de cada
componente

>>> obj.force(0)
Vec(14, 13)


Objetos do tipo Force()
=======================

Caso se trate de uma força comum, é mais conveniente utilizar uma classe que
automatiza a criação e configuração da força do objeto. Existem várias classes
pré-definidas, implementando forças como molas, gravidade, etc.


Forças simples
--------------

Estas são as forças que atuam em uma única partícula. Todas elas herdam da
classe `Single`. Existem ainda as classes `Conservative` e `Dissipative` que
implementam forças conservativas e aquelas que dependem apenas da velocidade.

Para criar uma força de atração gravitacional para o centro da tela, por
exemplo, basta criar o objeto do tipo Gravity() e atribuir ao atributo
obj.force:

>>> obj.force = Gravity(obj, G=1e5, pos=(400, 300))

Como conveniência, podemos também usar a função set_force_gravity():

>>> set_force_gravity(obj, G=1e5, pos=(400, 300))          # doctest: +ELLIPSIS
<...>

.. autoclass::Gravity
.. autoclass::Spring
.. autoclass::SpringTensor
.. autoclass::Viscous
.. autoclass::Drag
.. autoclass::Friction


Forças de pares
---------------

São forças que atuam em um par de partículas respeitando a Terceira Lei de
Newton (lei da ação e reação). Elas podem derivar de `Pair` ou
`ConservativePair`.

.. autoclass::GravityPair
.. autoclass::SpringPair
.. autoclass::SpringTensorPair


Sistemas de forças
------------------

São forças aplicáveis a qualquer número arbitrariamente grande de partículas.
Podem corresponder a sistemas auto-gravitantes, ou forças de molas, etc. Herdam
de `Pool` ou de `ConservativePool`

.. autoclass::GravityPool
.. autoclass::SpringPool
'''

from FGAme.mathtools import Vec2, null2D, asvector

EMPTY_FORCE = lambda t: null2D
NO_UPDATE = object()


class ForceProperty(object):

    '''Implementa o atributo obj.force dos objetos da classe Body.

    ForceProperty facilita a composição de forças num mesmo objeto e apresenta
    um sintaxe conveniente para especificar as forças atuantes em um objeto.

    Exemplo
    -------

    Considere uma classe com uma propriedade do tipo ForceProperty()

    >>> class HasForce(object):
    ...     force = ForceProperty()

    Criamos um objeto desta classe e atribuimos uma força a ele.

    >>> obj = HasForce()
    >>> obj.force = lambda x: (0, x**2)
    >>> obj.force(2)
    Vec(0, 4)

    Também podemos definir a força utilizando um decorador se for mais
    conveniente

    >>> @obj.force.define
    ... def force(x):
    ...     return (0, x**3)
    >>> obj.force(2)
    Vec(0, 8)

    O recurso mais importante, no entanto, é a composição de forças. Podemos
    definir uma composição de forças simplesmente adicionando ou subtraindo
    forças ao atributo original

    >>> obj.force += lambda x: (0, x**2)
    >>> obj.force(2) # => 2**2 + 2**3
    Vec(0, 12)

    Outras operações algébricas também estão definidas

    >>> obj.force *= 2
    >>> obj.force(2)
    Vec(0, 24)

    Os decoradores também estão disponíveis para as operações de adição e
    subtração de forças.

    >>> @obj.force.add
    ... def force(x):
    ...     return (0, x**4)
    >>> obj.force(2)
    Vec(0, 40)

    Notas
    -----

    A função que calcula a força será sempre gravada no atributo obj._force. O
    acesso via este atributo é mais rápido e pode ser utilizado internamente
    para os implementadores da classe.

    Um segundo atributo _force_ctrl também é criado para guardar o objeto que
    controla e coordena a composição de forças e os outros recursos da
    ForceProperty.

    O trabalho pesado é feito pela class ForceCtrl. Todos os acessos à
    obj.force do exemplo anterior simplesmente retornam o valor do atributo
    obj._force_ctl, que é a instância de ForceCtrl que realmente faz a
    coordenação das forças

    >>> obj._force_ctrl                                    # doctest: +ELLIPSIS
    <...ForceCtrl object at 0x...>
    >>> obj.force                                          # doctest: +ELLIPSIS
    <...ForceCtrl object at 0x...>

    Lembramos que obj._force é uma função simples que executa mais rapidamente
    que obj.force pois não precisa passar pelo mecanismo que implementa as
    propriedades no Python.

    >>> obj._force # doctest: +ELLIPSIS
    <function ... at 0x...>

    Caso não possua nenhuma força registrada no objeto, é garantido que o
    atributo obj._force possui a identidade da função EMPTY_FORCE, que recebe
    um argumento temporal e retorna sempre o vetor nulo.
    '''

    def __get__(self, obj, cls):
        if obj is None:
            return self
        try:
            return obj._force_ctrl
        except AttributeError:
            obj._force_ctrl = ctrl = ForceCtrl(obj)
            obj._force = EMPTY_FORCE
            return ctrl

    def __set__(self, obj, func):
        # matemática inplace acaba gravando valores espúrios na força.
        # obj.x.__iadd__() é o mesmo que obj.x = y.__iadd__(), onde y é o valor
        # retornado por obj.x. Deste modo, o retorno de __iadd__ acaba sendo
        # atribuido novamente para obj.x. A solução aqui foi fazer __iadd__
        # retornar um objeto especial NO_UPDATE e checar explicitamente se
        # este está sendo atribuído à propriedade.
        if func is not NO_UPDATE:
            ctrl = self.__get__(obj, type(obj))
            ctrl.define(func)


class ForceCtrl(object):

    '''
    Controla as operações com forças em um objeto. Pode ser chamado com um
    argumento numérico para calcular a força. Também aceita o idioma de
    composição de forças descrito na classe ForceProperty
    '''

    def __init__(self, obj):
        self._funcs = []
        self._obj = obj
        self._fast = EMPTY_FORCE

    def define(self, force):
        '''Limpa todas as forças anteriores e redefine o objeto de força.

        Pode ser chamado como um decorador.'''

        self.clear()
        self.add(force)
        return force

    def add(self, force):
        '''Adiciona uma nova força à interação com a partícula.

        O resultado é uma força cujo resultado é a soma de force(t) com as
        forças já definidas anteriormente.
        '''

        self._funcs.append((None, force))
        self._update_fast()
        return force

    def mul(self, factor):
        '''Multiplica todas as forças já definidas por uma constante
        multiplicativa. A constante deve ser um número.'''

        assert not callable(factor)
        L = self._funcs
        for i, (k, f) in enumerate(L):
            k = factor if k is None else factor * k
            L[i] = (k, f)
        self._update_fast()

    def clear(self):
        '''Limpa todas as forças que atuam no objeto'''

        self._funcs = []
        self._update_fast()

    # Funções privadas -------------------------------------------------------
    def _update_fast(self):
        '''Atualiza a função que calcula a força de acordo com os tipos de
        transformações presentes até o momento.

        Atualiza o método de acesso rápido do objeto em questão.'''
        if self._funcs:
            # Monta hierarquia de funções rápidas
            adds = [f for (k, f) in self._funcs if k is None]
            muls = [(k, f) for (k, f) in self._funcs if k is not None]
            fmuls = [(k, f) for (k, f) in muls if callable(k)]
            nmuls = [(k, f) for (k, f) in muls if not callable(k)]

            #
            # Implementa versões específicas, da mais especializada para a
            # menos especializada.
            #

            # Começamos no caso onde só existem forças aditivas
            if not fmuls and not nmuls:
                fast_func = self._make_fast_adds(adds)

            # Agora o caso onde todas as multiplicações são numéricas. Criamos
            # uma lista de tuplas (k, f) com a constante multiplicativa e
            # com a função
            elif not fmuls:
                nmuls += [(1, f) for f in adds]
                fast_func = self._make_fast_nmuls(nmuls)

            # Agora existem algumas multiplicações por funções
            else:
                nmuls += [(1, f) for f in adds]
                fmuls += [(lambda x: 1, f) for f in adds]
                fast_func = self._make_fast_fmuls(fmuls)

            # Salva a função rápida
            self._obj._force = self._fast = fast_func

        # Não existe nenhuma função registrada: atribui o atributo de acesso
        # rápido a None
        else:
            self._fast = EMPTY_FORCE
            self._obj._force = EMPTY_FORCE

    def _make_fast_adds(self, adds):
        '''Cria função que retorna a força como a soma de todas as forças na
        lista adds'''

        adds = tuple(adds)
        assert None not in adds, adds

        def fast_func(t):
            F = null2D
            for func in adds:
                F += func(t)
            return F
        return fast_func

    def _make_fast_nmuls(self, nmuls):
        '''Cria função que retorna a força como a soma do produto de cada
        constante k com a força f presente como as tuplas (k, f) em nmuls'''

        nmuls = tuple(nmuls)

        def fast_func(t):
            F = null2D
            for k, func in nmuls:
                Fi = asvector(func(t))
                try:
                    F += Fi * k
                except TypeError:
                    x, y = Fi
                    F += Vec2(k * x, k * y)
            return F
        return fast_func

    def _make_fast_fmuls(self, fmuls):
        '''Cria função que retorna a força como a soma do produto de cada
        constante k(t) com a força f presente como as tuplas (k, f) em fmuls'''

        fmuls = tuple(fmuls)

        def fast_func(t):
            F = null2D
            for scalar_func, func in fmuls:
                Fi = func(t)
                k = scalar_func(t)
                try:
                    F += Fi * k
                except TypeError:
                    x, y = Fi
                    F += Vec2(k * x, k * y)
            return F
        return fast_func

    # Métodos mágicos --------------------------------------------------------
    def __call__(self, t):
        return self._fast(t)

    def __iadd__(self, other):
        self.add(other)
        return NO_UPDATE

    def __imul__(self, other):
        self.mul(other)
        return NO_UPDATE


class Force(object):

    '''Implementa uma força que atua em um conjunto de objetos.'''

    @classmethod
    def setting_force(cls, *args, **kwds):
        '''Inicializa a força e já registra no atributo obj.force de todos os
        objetos envolvidos'''

        if 'register' in kwds:
            raise TypeError('invalid argument: register')

        kwds['register'] = True
        return cls(*args, **kwds)


###############################################################################
#         Implementações de forças específicas -- forças de 1 objeto
###############################################################################
def set_force_single(obj, func, mode):
    '''Define uma força simples sobre a partícula `obj`.

    Parameters
    ----------

    obj : Body
        Objeto em que a força atua
    force : callable
        Uma função que retorna o vetor com a força resultante. A assinatura da
        função depende do argumento `mode`.
    mode : str
        Existem quatro possibilidades. Cada um assume uma assinatura
        específica.
            'none':
                force() -> F
            'time':
                force(t) -> F
            'object':
                force(obj) -> F
            'position':
                force(obj.pos) -> F
            'velocity':
                force(obj.vel) -> F
            'all':
                force(obj.pos, obj.vel, t) -> F
        O valor padrão é 'time', que corresponde à convenção empregada pelo
        atributo obj.force dos objetos físicos.

    See also
    --------

    `Single`
    '''

    return Single.setting_force(obj, func, mode)


class Single(Force):

    '''Força simples aplicada a um objeto.

    Ver `set_force_single()` para descrição dos argumentos.'''

    def __init__(self, obj, force, mode='time', register=False):
        self._obj = obj
        self._force = force
        self._mode = mode

        # Converte force para a assinatura force(t) -> F
        if mode == 'time':
            self._worker = force
        elif mode == 'none':
            self._worker = lambda t: force()
        elif mode == 'object':
            self._worker = lambda t: force(obj)
        elif mode == 'all':
            self._worker = lambda t: force(obj, t)
        elif mode == 'position':
            self._worker = lambda t: force(obj.pos)
        elif mode == 'velocity':
            self._worker = lambda t: force(obj.vel)
        else:
            raise ValueError('invalid mode: %r' % mode)

        if register:
            self._obj.force.add(self._worker)

    def __call__(self, t):
        return self._worker(t)

    obj = property(lambda self: self._obj)
    force = property(lambda self: self._force)
    mode = property(lambda self: self._mode)


def set_force_viscous(obj, gamma):
    ''''''
    # TODO: documente-me!
    return Viscous.setting_force(obj, gamma)


class Viscous(Single):

    def __init__(self, obj, gamma=0, register=False):
        self.gamma = gamma
        self._viscous_force = force = lambda v: -gamma * obj.vel
        super(Viscous, self).__init__(obj, force, 'velocity', register)


def set_force_conservative(obj, force, potential):
    '''Força conservativa que atua em um único objeto.

    Parameters
    ----------
    obj : Body
        Objeto em que a força atua
    force : callable
        Função do vetor posição que retorna a força resultante.
    potential : callable
        Função do vetor posição que retorna a energia potencial.

    See also
    --------

    `Conservative`

    '''
    return Conservative.setting_force(obj, force, potential)


class Conservative(Single):

    '''Força conservativa que atua em um único objeto.

    Veja `set_force_conservative()` para descrição dos argumentos.'''

    def __init__(self, obj, force, potential, register=False):
        super(Conservative, self).__init__(
            obj, force, 'position', register=register)
        self._potential = potential

    def energyT(self):
        '''Energia total do par de partículas'''

        return self.obj.energyK() + self.energyU()

    def energyK(self):
        '''Energia cinética do par de partículas'''

        return self.obj.energyK()

    def energyU(self):
        '''Energia potencial do par de partículas'''

        return self.U(self.obj.pos)

    potential = property(lambda self: self._potential)


def set_force_gravity(obj, G, M=None, epsilon=0, pos=(0, 0)):
    '''Força de gravitacional produzida por um objeto de massa "M" fixo na
    posição "pos".

    A expressão para o potencial gravitacional é

        U(r) = - G M m / (|r - pos| + epsilon),

    onde m é a massa de obj e r a sua posição. A expressão anterior resulta na
    força

        F(r) = - G M m / (|r - pos| + epsilon)**2 * u,

    onde u = (r - pos) / |r - pos| é o vetor unitário na direção da linha que
    separa os centros.

    Parameters
    ----------
    obj : Body
        Objeto em que a força atua
    G : float
        Constante gravitacional. Como a FGAme não utiliza unidades físicas, não
        faz sentido atribuir um valor padrão para G. Deve ser calibrado em cada
        caso para adequar à dinâmica do jogo.
    M : float
        Massa da fonte gravitacional. Não precisa ser fornecido, já que o que
        importa é o produto entre M e G.
    epsilon : float
        Parâmetro de suavização da força da gravidade. Impede que ela exploda
        quando a distância tende a zero. Para distâncias menores que epsilon,
        a força gravitacional começa a se assemelhar a uma força de mola.
    pos : Vec2
        Vetor com a posição do centro da fonte de gravidade.

    See also
    --------

    `Gravity`
    '''

    return Gravity.setting_force(obj, G=G, M=M, epsilon=epsilon, pos=pos)


class Gravity(Conservative):

    '''Força de gravitacional produzida por um objeto de massa "M" fixo na
    posição "pos".

    Veja `set_force_gravity()` para descrição dos argumentos.'''

    def __init__(self, obj, G, M=None, epsilon=0, pos=(0, 0), register=False):
        if M is None:
            M = obj.mass
        self._M = M = float(M)
        self._epsilon = epsilon = float(epsilon)
        self._G = G = float(G)
        self._pos = pos = Vec2(*pos)

        def F(R):
            R = pos - R
            r = R.norm()
            r3 = (r + epsilon) ** 2 * r
            R *= G * obj.mass * M / r3
            return R

        def U(R):
            R = (R - pos).norm()
            return -self._G * obj.mass * M / (R + epsilon)

        super(Gravity, self).__init__(obj, F, U, register=register)

    G = property(lambda self: self._G)
    M = property(lambda self: self._M)
    epsilon = property(lambda self: self._epsilon)
    pos = property(lambda self: self._pos)


def set_force_spring(obj, k, gamma=0, pos=(0, 0)):
    # TODO: documentação
    return Spring.setting_force(obj, k, gamma, pos)


class Spring(Conservative):
    # TODO, implementar mola regular isotrópica e amortecida

    def __init__(self, k, gamma=0, pos=(0, 0)):
        raise NotImplementedError


def set_force_spring_tensor(obj, k, pos=(0, 0)):
    # TODO: documentação
    return SpringTensor.setting_force(obj, k, pos)


class SpringTensor(Conservative):

    '''Implementa uma força devido a uma mola com constante elástica k fixa na
    posição r0. Consulte a documentação de SpringTensorPair() para verificar
    como configurar a anisotropia e parâmetros da mola.'''

    def __init__(self, obj, k, pos=(0, 0), register=False):
        self._k = k
        kxy = 0
        x0, y0 = self._pos = Vec2(*pos)

        try:  # Caso isotrópico
            kx = ky = k = self._k = float(k)
        except TypeError:  # Caso anisotrópico
            k = self._k = tuple(map(float, k))
            if len(k) == 2:
                kx, ky = k
            else:
                kx, ky, kxy = k

        # Define forças e potenciais
        def F(R):
            Dx = x0 - R.x
            Dy = y0 - R.y
            return Vec2(kx * Dx + kxy * Dy, ky * Dy + kxy * Dx)

        def U(R):
            Dx = x0 - R.x
            Dy = y0 - R.y
            return (kx * Dx ** 2 + ky * Dy ** 2 + 2 * kxy * Dx * Dy) / 2.0

        super(SpringTensor, self).__init__(obj, F, U, register=register)

    k = property(lambda self: self._k)
    r0 = property(lambda self: self._pos)


###############################################################################
#        Implementações de forças específicas -- forças de 2 objetos
###############################################################################
def set_force_pair(A, B, func, mode='time'):
    '''
    Força que opera em um par de partículas respeitando a lei de ação e reação.

    Parameters
    ----------

    A, B : Object instances
        Objetos em que a força atua
    force : callable
        Uma função que retorna o vetor com a força resultante. A assinatura da
        função depende do último argumento `mode`. Por convenção é a força que
        A produz em B (ou força sofrida por B devido à A).
    mode : str
        Existem cinco possibilidades. Cada um assume uma assinatura específica.
            'none':
                force() -> F
            'time':
                force(t) -> F
            'object':
                force(A, B) -> F
            'position':
                force(A.pos, B.pos) -> F
            'all':
                force(A.pos, B.pos, t) -> F
        O valor padrão é 'time', que corresponde à convenção empregada pelo
        atributo obj.force dos objetos físicos.

    See also
    --------

    `Pair`
    '''
    return Pair.setting_force(A, B, func, mode, True)


class Pair(Force):

    '''
    Força que opera em um par de partículas respeitando a lei de ação e reação.

    Veja `set_force_pair()` para descrição dos argumentos.'''

    def __init__(self, A, B, func, mode='time', register=False):
        self._A = A
        self._B = B
        self._force = func
        self._mode = mode
        self._cacheF = None

        # Converte force para a assinatura force(t) -> F
        if mode == 'time':
            self._worker = func
        elif mode == 'none':
            self._worker = lambda t: func()
        elif mode == 'object':
            self._worker = lambda t: func(A, B)
        elif mode == 'all':
            self._worker = lambda t: func(A.pos, B.pos, t)
        elif mode == 'position':
            self._worker = lambda t: func(A.pos, B.pos)
        else:
            raise ValueError('invalid mode: : %r' % mode)

        # Registra as forças
        if register:
            self._A.force.add(self.force_A)
            self._B.force.add(self.force_B)

    # Atributos somente para leitura
    A = property(lambda self: self._A)
    B = property(lambda self: self._B)
    force = property(lambda self: self._force)
    mode = property(lambda self: self._mode)

    def force_A(self, t):
        '''Função que calcula a força sobre o objeto A no instante t'''

        if self._cacheF is None:
            res = self._worker(t)
            self._cacheF = -res
            return res
        else:
            res = self._cacheF
            self._cacheF = None
            return res

    def force_B(self, t):
        '''Função que calcula a força sobre o objeto B no instante t'''

        if self._cacheF is None:
            res = self._worker(t)
            self._cacheF = res
            return -res
        else:
            res = self._cacheF
            self._cacheF = None
            return res

    def accel_A(self, t):
        '''Função que calcula a aceleração sobre o objeto A no instante t'''

        return self.force_A(t) / self._A.mass

    def accel_B(self, t):
        '''Função que calcula a aceleração sobre o objeto B no instante t'''

        return self.force_A(t) / self._A.mass

    def __iter__(self):
        yield self.force_A
        yield self.force_B

    def forces(self):
        '''Itera sobre as funções [force_A, force_B]'''

        yield self.force_A
        yield self.force_B

    def accels(self):
        '''Itera sobre as acelerações [accel_A, accel_B]'''

        yield self.accel_A
        yield self.accel_B


def set_force_conservative_pair(A, B, force, U):
    # TODO: documentação
    return ConservativePair.setting_force(A, B, force, U)


class ConservativePair(Pair):

    '''
    Uma força que opera em um par de partículas e possui uma energia potencial
    associada.

    Esta classe é iniciada a partir de uma função force(rA, rB) e de um
    potencial U(rA, rB).
    '''

    def __init__(self, A, B, force, U, register=False):
        super(ConservativePair, self).__init__(
            A, B, force, 'position', register=register)
        self._potential = U

    def energyT(self):
        '''Energia total do par de partículas'''

        return self.A.energyK() + self.B.energyK() + self.energyU()

    def energyK(self):
        '''Energia cinética do par de partículas'''

        return self.A.energyK + self.B.energyK

    def energyU(self):
        '''Energia potencial do par de partículas'''

        return self.U(self.A.pos, self.B.pos)

    U = property(lambda self: self._potential)


class SpringPair(Conservative):
    # TODO, implementar spring regular isotrópica e amortecida com uma
    # distância fixa de atuação.
    pass


def set_force_spring_tensor_pair(A, B, k):
    '''
    Liga as duas partículas por uma força de Hooke com uma constante de mola
    anisotrópica.

    O potencial é dado por::

        U = kx * dx**2 / 2 + ky * dy**2 /2 + kxy * dx * dy

    Onde dx e dy são as diferenças de posições nas direções x e y
    respectivamente. Este potencial resulta em uma força::

        F = -kx * dx - ky * dy -kxy * (dx + dy)

    Os termos dx e dy são as componentes do vetor ``B.pos - A.pos``.

    Parameters
    ----------

    A, B : Body
        Objetos que participam da interação de mola.
    k : float ou tupla
        Especifica a constante de mola como sendo isotrópica (se k é for um
        número) ou através de uma tuplas (kx, ky) ou (kx, ky, kxy).

    See Also
    --------

    `SpringTensorPair`
    '''
    return SpringTensorPair.setting_force(A, B, k)


class SpringTensorPair(ConservativePair):

    '''
    Liga as duas partículas por uma força de Hooke com uma constante de mola
    anisotrópica.

    Veja `set_force_string_tensor_pair()` para descrição dos argumentos.'''

    def __init__(self, A, B, k, register=False):
        kxy = 0
        try:  # Caso isotrópico
            kx = ky = k = self._k = float(k)
        except TypeError:  # Caso anisotrópico
            k = self._k = tuple(map(float, k))
            if len(k) == 2:
                kx, ky = k
            else:
                kx, ky, kxy = k

        # Define forças e potenciais
        def F(rA, rB):
            dx, dy = rB - rA
            return Vec2(kx * dx + kxy * dy, +ky * dy + kxy * dx)

        def U(rA, rB):
            dx, dy = rB - rA
            return (kx * dx ** 2 + ky * dy ** 2 + 2 * kxy * dx * dy) / 2.0

        super(SpringTensorPair, self).__init__(A, B, F, U, register=register)

    k = property(lambda self: self._k)
    delta = property(lambda self: self._delta)


def set_force_gravity_pair(A, B, G, epsilon=0):
    # TODO: documentação
    return GravityPair.setting_force(A, B, G, epsilon)


class GravityPair(ConservativePair):

    '''
    Implementa a força de gravidade "amaciada" com um parâmetro epsilon.

    A energia potencial desta força é dada por

        U(rA, rB) = -G mA mB / (|rB - rA| + e)

    O parâmetro de amaciamento pode ser necessário para melhorar a estabilidade
    numérica caso as duas posições rA e rB se aproximem muito. O valor padrão
    é zero e o usuário deve ponderar sobre valores adequados caso a caso. Na
    prática epsilon limita o valor máximo que a força gravitacional pode
    assumir.
    '''

    def __init__(self, A, B, G, epsilon=0, register=False):
        self._G = G = float(G)
        self._epsilon = epsilon = float(epsilon)

        def F(Ra, Rb):
            R = Rb - Ra
            r = R.norm()
            r3 = (r + epsilon) ** 2 * r
            R *= G * A.mass * B.mass / r3
            return R

        def U(Ra, Rb):
            R = (Ra - Rb).norm()
            return -self._G * B.mass * A.mass / (R + self._epsilon)

        super(GravityPair, self).__init__(A, B, F, U, register)

    G = property(lambda self: self._G)
    epsilon = property(lambda self: self._epsilon)


###############################################################################
# Implementações de forças específicas -- forças aplicadas a grupos de objetos
###############################################################################
class Pool(Force):

    '''Força que atua em um grupo arbitrariamente grande de objetos'''

    def __init__(self, objects, register=False):
        self.objects = list(objects)


class ConservativePool(Pool):

    '''Sistema de partículas com força conservativa'''


class GravityPool(ConservativePool):

    '''Força gravitacional entre um grupo arbitrariamente grande de objetos.'''

    def get_force(self, obj, mutable=True):
        pass

    def get_all_forces(self, mutable=True):
        return [self.get_force(obj, mutable) for obj in self.objects]
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
if __name__ == '__main__':
    class HasForce(object):
        force = ForceProperty()

    obj = HasForce()
    obj.force = lambda t: (2, 4 - t)
    obj.force(2)
    obj.force *= 2
    obj.force(2)

    import doctest
    doctest.testmod()

    from math import cos
    from FGAme import *
    from FGAme.physics import set_force_gravity_pair

    world = World(restitution=0)
    c1 = Circle(10, density=2, pos=(300, 200), vel=(100, -100), color='red')
    c2 = Circle(10, pos=(500, 400), vel=(-100, 100))
    c3 = Circle(10, pos=(200, 300), vel=(-100, 100))

    #k = 1000
    #c1.force = lambda t: -k * (c1.pos - c2.pos)
    #c2.force = lambda t: -k * (c2.pos - c1.pos)

    G = 1.1e5
    e = 200
    set_force_gravity_pair(c1, c2, G=G, epsilon=e)
    set_force_gravity_pair(c1, c3, G=G, epsilon=e)
    set_force_gravity_pair(c2, c3, G=G, epsilon=e)

    set_force_viscous(c1, gamma=1000)

    #c1.force += lambda t: - gamma * c1.vel
    #c2.force += lambda t: - gamma * c2.vel
    #c3.force += lambda t: - gamma * c3.vel

    world.add([c1, c2, c3])
    world.run()
