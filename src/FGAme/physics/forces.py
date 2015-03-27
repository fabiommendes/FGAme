# -*- coding: utf8 -*-
'''
Created on 19/11/2014

@author: chips
'''

from FGAme.mathutils import Vector, VectorM


class ForceProperty(object):

    '''Implementa o atributo external_force dos objetos da classe Object.

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
    Vector(0, 4)

    Também podemos definir a força utilizando um decorador se for mais
    conveniente

    >>> @obj.force
    ... def force(x):
    ...     return (0, x**3)
    >>> obj.force(2)
    Vector(0, 8)

    O recurso mais importante, no entanto, é a composição de forças. Podemos
    definir uma composição de forças simplesmente adicionando ou subtraindo
    forças ao atributo original

    >>> obj.force += lambda x: (0, x**2)
    >>> obj.force(2) # => 2**2 + 2**3
    Vector(0, 12)

    Outras operações algébricas também estão definidas

    >>> obj.force *= 2
    >>> obj.force(2)
    Vector(0, 24)

    Os decoradores também estão disponíveis para as operações de adição e
    subtração de forças.

    >>> @obj.force.add
    ... def force(x):
    ...     return (0, x**4)
    >>> obj.force(2)
    Vector(0, 40)

    Notas
    -----

    A função que executa a força será sempre gravada no atributo correspondente
    ao nome da propriedade iniciado com um '_'. O acesso via este atributo é
    mais rápido e pode ser utilizado internamente para os implementadores da
    classe.

    Um segundo atributo com o sufixo '_ctrl' também é criado para controlar
    como as forças se compõe e como parte da implementação do idioma mostrado
    anteriormente. Ambos nomes podem ser  modificados no construtor da
    propriedade.

    >>> obj._force # doctest: +ELLIPSIS
    <function ... at 0x...>
    >>> obj._force_ctrl # doctest: +ELLIPSIS
    <...ForcePropertyCtrl object at 0x...>
    '''

    def __init__(self, attr_name=None, ctrl_name=None):
        self.attr_name = attr_name
        self.ctrl_name = ctrl_name

    # Acessa nome e ctrl ou calcula sob demanda
    def _name(self, cls):
        name = self.attr_name
        if name is None:
            name = self.attr_name = '_' + self._inspect_name(cls)
        return name

    def _ctrl(self, cls):
        name = self.ctrl_name
        if name is None:
            name = self.ctrl_name = self._name(cls) + '_ctrl'
        return name

    def _inspect_name(self, cls):
        '''Tenta descobrir o nome que a propriedade possui dentro da classe
        cls'''

        for attr in dir(cls):
            if getattr(cls, attr) is self:
                return attr
        raise RuntimeError('property is not attached to a class')

    # getters e setters para classes Python
    def __get__(self, obj, cls):
        if obj is None:
            return self
        try:
            return getattr(obj, self._ctrl(cls))
        except AttributeError:
            ctrl = ForcePropertyCtrl(obj, self._name(cls))
            setattr(obj, self._ctrl(cls), ctrl)
            setattr(obj, self._name(cls), None)
            return ctrl

    def __set__(self, obj, func):
        ctrl = self.__get__(obj, type(obj))
        if ctrl is not func:
            ctrl.clear()
            ctrl.add(func)


class ForcePropertyCtrl(object):

    '''
    Controla as operações com forças em um objeto. Pode ser chamado com um
    argumento numérico para calcular a força. Também aceita o idioma de
    composição de forças descrito na classe ForceProperty
    '''

    def __init__(self, obj, attr_name):
        self._funcs = []
        self._obj = obj
        self._attr = attr_name
        self._fast = None

    def add(self, other):
        '''Adiciona uma nova força à interação com a partícula'''

        self._funcs.append((None, other))
        self._update_fast()

    def mul(self, other):
        '''Multiplica todas as forças por uma constante multiplicativa'''

        assert not callable(other)
        L = self._funcs
        for i, (k, f) in enumerate(L):
            k = other if k is None else other * k
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
            muls = {k: [] for (k, _) in self._funcs if k is not None}
            for k, f in self._funcs:
                if k is not None:
                    muls[k].append(f)
            fmuls = {k: L for (k, L) in muls.items() if callable(k)}
            nmuls = {k: L for (k, L) in muls.items() if not callable(k)}

            # Implementa versões específicas da mais especializada para a menos
            # Começamos no caso onde só existem forças aditivas
            if not fmuls and not nmuls:
                fast_func = self._make_fast_adds(adds)

            # Agora o caso onde todas as multiplicações são numéricas. Criamos
            # uma lista de tuplas (k, f) com a constante multiplicativa e
            # com a função
            elif not fmuls:
                combined = [(1, f) for f in adds]
                for (k, L) in nmuls.items():
                    combined.extend((k, f) for f in L)
                fast_func = self._make_fast_combined(combined)

            else:
                raise NotImplementedError(nmuls, fmuls)

            # Salva a função rápida
            self._fast = fast_func
            setattr(self._obj, self._attr, fast_func)

        # Não existe nenhuma função registrada: atribui o atributo de acesso
        # rápido a None
        else:
            self._fast = None
            setattr(self._obj, self._attr, None)

    def _make_fast_adds(self, adds):
        '''Cria função que retorna a força como a soma de todas as forças em
        adds'''

        F = VectorM(0, 0)
        Fmul = F.__imul__  # usamos estas funções para evitar problemas de
        Fadd = F.__iadd__  # escopo no closure fa função fast_func

        def fast_func(t):
            Fmul(0)
            for func in adds:
                Fadd(func(t))
            return F
        return fast_func

    def _make_fast_combined(self, combined):
        '''Cria função que retorna a força como a soma de todas as constantes
        k e forças f para cada elemento (k, f) em combined'''

        F = VectorM(0, 0)
        Fmul = F.__imul__
        Fadd = F.__iadd__

        def fast_func(t):
            Fmul(0)
            for k, func in combined:
                fi = func(t)
                Fadd((k * fi[0], k * fi[1]))
            return F
        return fast_func

    # Métodos mágicos --------------------------------------------------------
    def __call__(self, t):
        # Se o argumento for uma função, significa que estamos usando o
        # decorador para definir o valor da força
        if callable(t):
            func = t
            self.clear()
            self.add(func)
            return func

        # Caso contrário, assume que o argumento é numérico e executa
        t = float(t)
        if self._fast is not None:
            return Vector(*self._fast(t))
        else:
            return Vector(0, 0)

    def __iadd__(self, other):
        self.add(other)
        return self

    def __imul__(self, other):
        self.mul(other)
        return self


###############################################################################
#         Implementações de forças específicas -- forças de 1 objeto
###############################################################################


class SingleForce(object):

    '''Implementa uma força simples aplicada a um objeto.

    O argumento 'mode' possui o mesmo significado que na classe PairForce().'''

    def __init__(self, obj, func, mode='time'):
        self._obj = obj
        self._func = func
        self._mode = mode

        # Converte func para a assinatura func(t) -> F
        if mode == 'time':
            self._func_ready = func
        elif mode == 'none':
            self._func_ready = lambda t: func()
        elif mode == 'objects':
            self._func_ready = lambda t: func(obj)
        elif mode == 'all':
            self._func_ready = lambda t: func(obj, t)
        elif mode == 'positions':
            pos = obj._pos

            def new_func(t):
                assert pos is obj._pos
                return func(pos)
            self._func_ready = new_func
        else:
            raise ValueError('invalid value for fargs: %r' % fargs)

    def __call__(self, t):
        return self._func_ready(t)

    obj = property(lambda x: x._obj)
    func = property(lambda x: x._func)
    mode = property(lambda x: x._mode)


class SingleConservativeForce(SingleForce):

    '''Força conservativa que atua em um único objeto.

    Recebe o elemento, a força e o potencial como argumentos'''

    def __init__(self, obj, force, U):
        super(SingleConservativeForce, self).__init__(obj, force, 'positions')
        self._U = U

    def totalE(self):
        '''Energia total do par de partículas'''

        return self.obj.kineticE() + self.potentialE()

    def kineticE(self):
        '''Energia cinética do par de partículas'''

        return self.obj.kineticE()

    def potentialE(self):
        '''Energia potencial do par de partículas'''

        return self.U(self.obj._pos)

    U = property(lambda x: x._U)


class GravitySF(SingleConservativeForce):

    '''Implementa uma força de gravitacional produzida por um objeto de massa M
    fixo na posição r0.

    O parâmetro de suavização epsilon possui o mesmo significado que em
    GravityF'''

    def __init__(self, obj, G, M=None, epsilon=0, r0=(0, 0)):
        if M is None:
            M = obj.mass
        M = self._M = float(M)
        self._epsilon = float(epsilon)
        self._G = float(G)
        r0 = self._r0 = Vector(*r0)

        def F(R):
            R = r0 - R
            r = R.norm()
            r3 = (r + epsilon) ** 2 * r
            R *= G * obj.mass * M / r3
            return R

        def U(R):
            R = (R - r0).norm()
            return -self._G * obj.mass * M / (R + self._epsilon)

        super(GravitySF, self).__init__(obj, F, U)

    G = property(lambda x: x._G)
    M = property(lambda x: x._M)
    epsilon = property(lambda x: x._epsilon)
    r0 = property(lambda x: x._r0)


class SpringSF(SingleConservativeForce):

    '''Implementa uma força devido a uma mola com constante elástica k fixa na
    posição r0. Consulte a documentação de SpringF() para verificar como
    configurar a anisotropia da mola.'''

    def __init__(self, obj, k, r0=(0, 0)):
        kxy = 0
        x0, y0 = self._r0 = Vector(*r0)

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
            Dx = x0 - R._x
            Dy = y0 - R._y
            return Vector(kx * Dx + kxy * Dy, ky * Dy + kxy * Dx)

        def U(R):
            Dx = x0 - R.x
            Dy = y0 - R.y
            return (kx * Dx ** 2 + ky * Dy ** 2 + 2 * kxy * Dx * Dy) / 2

        super(SpringSF, self).__init__(obj, F, U)

    k = property(lambda x: x._k)
    r0 = property(lambda x: x._r0)


###############################################################################
#        Implementações de forças específicas -- forças de 2 objetos
###############################################################################


class PairForce(object):

    '''
    Força que opera em um par de partículas respeitando a lei de ação e reação.

    Parameters
    ----------

    A, B : Object instances
        Objetos em que a força atua
    func : callable
        Uma função que retorna o vetor com a força resultante. A assinatura da
        função depende do último argumento `fargs`
    mode : str
        Existem quatro possibilidades. Cada um assume uma assinatura
        específica.
            'none':
                func() -> F
            'time':
                func(t) -> F
            'objects':
                func(A, B) -> F
            'positions':
                func(A.pos_cm, B.pos_cm) -> F
            'all':
                func(A, B, t) -> F
        O valor padrão é 'time', que corresponde à convenção empregada pelo
        sistema do obj.external_force da classe Object.

    '''

    def __init__(self, A, B, func, mode='time'):
        self._A = A
        self._B = B
        self._func = func
        self._mode = mode
        self._cacheF = None

        # Converte func para a assinatura func(t) -> F
        if mode == 'time':
            self._func_ready = func
        elif mode == 'none':
            self._func_ready = lambda t: func()
        elif mode == 'objects':
            self._func_ready = lambda t: func(A, B)
        elif mode == 'all':
            self._func_ready = lambda t: func(A, B, t)
        elif mode == 'positions':
            A_pos, B_pos = A._pos, B._pos

            def new_func(t):
                assert A_pos is A._pos and B_pos is B._pos
                return func(A_pos, B_pos)
            self._func_ready = new_func
        else:
            raise ValueError('invalid value for fargs: %r' % fargs)

    # Atributos somente para leitura
    A = property(lambda x: x._A)
    B = property(lambda x: x._B)
    func = property(lambda x: x._func)
    mode = property(lambda x: x._mode)

    def force_A(self, t):
        '''Função que calcula a força sobre o objeto A no instante t'''

        if self._cacheF is None:
            res = self._func_ready(t)
            self._cacheF = -res
            return res
        else:
            res = self._cacheF
            self._cacheF = None
            return res

    def force_B(self, t):
        '''Função que calcula a força sobre o objeto B no instante t'''

        if self._cacheF is None:
            res = self._func_ready(t)
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


class PairConservativeForce(PairForce):

    '''
    Uma força que opera em um par de partículas e possui uma energia potencial
    associada.

    Esta classe é iniciada a partir de uma função force(rA, rB) e de um
    potencial U(rA, rB).
    '''

    def __init__(self, A, B, force, U):
        super(PairConservativeForce, self).__init__(A, B, force, 'positions')
        self._U = U

    def totalE(self):
        '''Energia total do par de partículas'''

        return self.A.kineticE() + self.B.kineticE() + self.potentialE()

    def kineticE(self):
        '''Energia cinética do par de partículas'''

        return self.A.kineticE + self.B.kineticE

    def potentialE(self):
        '''Energia potencial do par de partículas'''

        return self.U(self.A._pos, self.B._pos)

    U = property(lambda x: x._U)


class SpringF(PairConservativeForce):

    '''
    Liga as duas partículas por uma força de Hooke com uma dada constante de
    mola e uma certa separação de equilíbrio delta.

    A constante de mola pode ser anisotrópica. Neste caso, deve ser
    especificado uma tupla (kx, ky) ou (kx, ky, kxy) com cada um dos termos no
    potencial:

        U_AB = kx * dx**2 / 2 + ky * dy**2 /2 + kxy * dx * dy

    Os termos dx e dy são as componentes do vetor rA - rB - delta.
    '''

    def __init__(self, A, B, k, delta=(0, 0)):
        kxy = 0
        dx, dy = delta = self._delta = Vector(*delta)

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
            Dx = rB._x - rA._x + dx
            Dy = rB._y - rA._y + dy
            return Vector(kx * Dx + kxy * Dy, +ky * Dy + kxy * Dx)

        def U(rA, rB):
            Dx = rB._x - rA._x + dx
            Dy = rB._y - rA._y + dy
            return (kx * Dx ** 2 + ky * Dy ** 2 + 2 * kxy * Dx * Dy) / 2

        super(SpringF, self).__init__(A, B, F, U)

    k = property(lambda x: x._k)
    delta = property(lambda x: x._delta)


class GravityF(PairConservativeForce):

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

    def __init__(self, A, B, G, epsilon=0):
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

        super(GravityF, self).__init__(A, B, F, U)

    G = property(lambda x: x._G)
    epsilon = property(lambda x: x._epsilon)


###############################################################################
# Implementações de forças específicas -- forças aplicadas a grupos de objetos
###############################################################################


class GravityPool(object):

    def __init__(self, objects):
        self.objects = list(objects)

    def get_force(self, obj, mutable=True):
        pass

    def get_all_forces(self, mutable=True):
        return [self.get_force(obj, mutable) for obj in self.objects]

if __name__ == '__main__':
    import doctest
    doctest.testmod()
