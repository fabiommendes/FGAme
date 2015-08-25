# -*- coding: utf8 -*-
from FGAme.mathtools import Vec2, asvector, null2D
from FGAme.physics.flags import BodyFlags
from FGAme.util import lazy
from math import exp


###############################################################################
#                 Pontos de Contato/Manifolds
###############################################################################


class ContactPoint(Vec2):

    '''Representa um ponto de contato com um certo nível de penetração'''

    __slots__ = ['depth']

    def __init__(self, x, y, depth):
        super(Vec2, self).__init__(x, y)
        self.depth = depth


class BaseContactManifold(object):

    '''Classe mãe para ContactManifold e SimpleContactManifold'''

    def __iter__(self):
        return iter(self.points)


class ContactManifold(BaseContactManifold):

    '''Representa uma lista de pontos de contato associados a uma única
    normal.'''

    __slots__ = ['normal', 'points']

    def __init__(self, normal, points):
        self.normal = normal.normalized()
        self.points = list(points)


class SimpleContactManifold(BaseContactManifold):

    '''Representa um contato simples com apenas um ponto'''

    __slots__ = ['normal', 'point']

    def __init__(self, normal, point):
        self.normal = normal
        self.point = point

    @property
    def points(self):
        return [self.point]

    def __iter__(self):
        yield self.point


###############################################################################
#                           Contatos abstratos
###############################################################################

class Pair(object):

    '''Representa alguma ligação/conexão entre dois objetos'''

    __slots__ = ('A', 'B')

    def __init__(self, A, B):
        self.A = A
        self.B = B

    def _constructor(self, A, B):
        '''Cria um novo objeto tipo Pair a partir dos dois objetos
        fornecidos'''

        return type(self)(A, B)

    def swapped(self):
        '''Retorna uma colisão com o papel dos objetos A e B trocados'''

        A, B = self.objects
        return self._constructor(B, A)

    def other(self, obj):
        '''Se for chamada com o objeto A, retorna o objeto B e vice-versa'''

        A, B = self.objects
        if obj is A:
            return B
        elif obj is B:
            return A
        else:
            raise ValueError('object does not participate in the connection')

    def isvalid(self):
        '''Retorna True caso o contato ainda seja válido ou False caso já tenha
        sido desfeito.'''

        raise NotImplementedError

    def update(self):
        '''Recalcula todas as propriedades que modem ser modificadas de um
        frame para o outro'''

        raise NotImplementedError

    # __magic__ ###############################################################
    def __eq__(self, other):
        return self is other

    def __getitem__(self, i):
        if i == 0:
            return self.A
        elif i == 1:
            return self.B
        else:
            raise IndexError(i)

    def __hash__(self):
        return id(self)

    def __iter__(self):
        yield self.A
        yield self.B

    def __getattr_(self, attr):
        if not attr.startswith('get_'):
            value = getattr(self, 'get_' + attr)()
            setattr(self, value)
            return value
        else:
            raise AttributeError(attr)


class BroadContact(Pair):

    '''Representa um contato na Broad phase'''

    def get_collision(self):
        '''Retorna o objecto de collisão associado ao contato. Caso não haja
        colisão, retorna None'''

        raise NotImplementedError


class CBBContact(BroadContact):

    '''Representa um par de objetos com caixas de contorno circulares que
    se sobrepõem'''

    pass


class AABBContact(BroadContact):

    '''Representa um par de objetos com caixas de contorno alinhadas ao eixo
    que se sobrepõem'''

    pass


###############################################################################
#                         Classe Colisão
# ----------------------------------------------------------------------------
#
# Representa uma colisão entre dois objetos.  Resolve a colisão sob demanda.
#
###############################################################################


class Collision(Pair):

    '''Representa a colisão entre dois objetos.

    Subclasses de Collision devem implementar o método .resolve(dt) que resolve
    a colisão entre os objetos respeitando os vínculos de is_dynamic*.

    Example
    -------

    Considere a colisão unidimensional entre dois círculos

    >>> from FGAme.physics import Circle, flags
    >>> A = Circle(1, pos=(0, 1), mass=1, vel=(1, 0))
    >>> B = Circle(1, pos=(2, 1), mass=1)

    A colisão unidimensional de dois objetos de mesma massa simplesmente troca
    as velocidades. Antes disso, no entanto, é necessário passar os parâmetros
    de colisão para que se possa calcular os resultados.

    >>> col = Collision(A, B,
    ...                 pos=(1, 1),    # ponto de colisão
    ...                 normal=(1, 0)) # normal da colisão

    Podemos investigar as propriedades físicas da colisão e verificar que as
    leis de conservação são preservadas

    >>> col.kineticE(); col.momentumP(); col.momentumL()
    0.5
    Vec2(1, 0)
    -1.0

    Podemos resolver a colisão utilizando ou o método step() ou o resolve(). O
    segundo é chamado apenas uma vez e já aciona os sinais de colisão. O método
    step() é utilizado em resoluções iterativas com vários objetos colidindo
    simultaneamente.

    >>> col.resolve()

    Agora investigamos os valores finais e vemos que as leis de conservação
    foram satisfeitas.

    >>> col.kineticE(); col.momentumP(); col.momentumL()
    0.5
    Vec2(1, 0)
    -1.0

    Investigando as propriedades, verificamos que de fato a velocidade dos dois
    objetos foi invertida

    >>> A.vel; B.vel
    Vec2(0, 0)
    Vec2(1, 0)


    Suponha agora que a colisão não se deu no ponto selecionado anteriormente.

    >>> A.vel, B.vel = B.vel, A.vel
    >>> col = Collision(A, B,
    ...                 pos=(0, 0),    # ponto de colisão
    ...                 normal=(1, 0)) # normal da colisão

    Esta posição induz a uma velocidade de rotação e transferência de energia
    de movimento linear para angular.

    >>> col.resolve()
    >>> A.linearE() + B.linearE(), A.angularE() + B.angularE()
    (0.265625, 0.234375)

    As leis de conservação continuam sendo satisfeitas
    >>> col.kineticE(); col.momentumP(); col.momentumL()
    0.5
    Vec2(1, 0)
    -1.0
    '''
    min_vel_bias = 1.0

    def __init__(self, A, B, world=None, pos=None, normal=None, delta=0.0):
        super(Collision, self).__init__(A, B)
        self.objects = A, B
        self.world = world
        self.is_active = True
        self.resolved = False
        self.vrel = null2D
        if pos is None:
            raise ValueError(A, B)
        self.pos = asvector(pos)
        self.normal = asvector(normal)
        self.delta = delta
        self.Jn = 0.0
        self.vel_bias = 0.0
        self.init()

        # Certifica se normal foi bem escolhida
        if (self.rA.dot(self.normal) < 0):
            self.__init__(self.A, self.B, world=world, pos=pos, normal=-normal,
                          delta=delta)

    ###########################################################################
    #                 Propriedades calculadas sob demanda
    ###########################################################################
    def init(self):
        '''Calcula propriedades da colisão'''

        A, B = self.A, self.B
        n = self.normal
        P = self.pos

        # Coeficiente de atrito e restituição
        self.mu = self.get_friction_coeff()
        self.e = self.get_restitution()

        # Pontos de contato
        self.rA = rA = P - A.pos
        self.rB = rB = P - B.pos
        self.rA_ortho = Vec2(-rA.y, rA.x)
        self.rB_ortho = Vec2(-rB.y, rB.x)

        # Massa efetiva
        eff_invmass = A._invmass + B._invmass

        if A._invinertia:
            eff_invmass += rA.cross(n) ** 2 * A._invinertia

        if B._invinertia:
            eff_invmass += rB.cross(n) ** 2 * B._invinertia

        self.effmass = 1.0 / eff_invmass

        # Viés na velocidade relativa para definir o coeficiente de restituição
        vrel = ((B.vel + B.omega * self.rB_ortho)
                - (A.vel + A.omega * self.rA_ortho))
        vrel_normal = vrel.dot(n)
        if -vrel_normal > self.min_vel_bias:
            self.vel_bias = -self.e * vrel_normal

    def step(self):
        A, B = self.A, self.B
        n = self.normal

        # Velocidade de contato relativa
        self.vrel = vrel = ((B.vel + B.omega * self.rB_ortho)
                            - (A.vel + A.omega * self.rA_ortho))
        vrel_normal = vrel.dot(n)

        # Impulso normal calculado no passo
        deltaJ = -self.effmass * (vrel_normal - self.vel_bias)
        self.Jn += deltaJ
        self.apply_impulse(deltaJ)

    def apply_impulse(self, J):
        # Aplica incremento no impulso
        if J != 0:
            A, B = self.A, self.B
            Jvec = J * self.normal
            if A._invmass:
                A.apply_impulse(-Jvec)
                if A._invinertia:
                    A.apply_aimpulse(Jvec.cross(self.rA))
            if B._invmass:
                B.apply_impulse(Jvec)
                if B._invinertia:
                    B.apply_aimpulse(-Jvec.cross(self.rB))

    def apply_tangent(self, J):
        # Aplica incremento no impulso
        if J <= 0:
            return

        A, B = self.A, self.B
        vrel = self.vrel
        tangent = self.get_tangent()

        # Calcula o impulso tangente máximo
        vrel_tan = -vrel.dot(tangent)
        Jtan_max = abs(self.mu * J)

        # Limita a ação do impulso tangente
        if A._invmass and B._invmass:
            J = min(
                [Jtan_max, vrel_tan / A._invmass, vrel_tan / B._invmass])
        elif A._invmass:
            J = min([Jtan_max, vrel_tan / A._invmass])
        elif B._invmass:
            J = min([Jtan_max, vrel_tan / B._invmass])
        else:
            J = 0.0

        Jvec = J * tangent
        if A._invmass:
            A.apply_impulse(-Jvec)
            if A._invinertia:
                A.apply_aimpulse(Jvec.cross(self.rA))
        if B._invmass:
            B.apply_impulse(Jvec)
            if B._invinertia:
                B.apply_aimpulse(-Jvec.cross(self.rB))

    def finalize(self):
        if self.Jn < 0:
            self.apply_impulse(-self.Jn)
        self.apply_tangent(self.Jn)

    def get_tangent(self):
        # Vetor unitário tangente à colisão
        n = self.normal
        tangent = Vec2(-n.y, n.x)
        if tangent.dot(self.vrel) > 0:
            tangent = -tangent
        return tangent

    @property
    def pos_cm(self):
        A, B = self
        return (A. mass * A.pos + B.mass * B.pos) / (A.mass + B.mass)

    def kineticE(self):
        return self.A.kineticE() + self.B.kineticE()

    def momentumP(self):
        return self.A.momentumP() + self.B.momentumP()

    def momentumL(self):
        pos = (0, 0)
        return self.A.momentumL(pos) + self.B.momentumL(pos)

    ###########################################################################
    #                       Métodos da API de Collision
    ###########################################################################
    def is_simple(self):
        '''Retorna True se o contato for o único contato de ambos os objetos
        envolvidos'''

        return (len(self.A._contacts) <= 1) and (len(self.B._contacts) <= 1)

    def resolve(self, dt=0, trigger=True, clear=True):
        '''Resolve a colisão entre A e B, distribuindo os impulsos de acordo
        com as propriedades can_move* do objeto'''

        A, B = self

        # Impulso nulo
        if self.resolved:
            self.resolved = True
        else:
            # Resolve as colisões
            self.step()
            self.finalize()
            self.resolved = True

            # Dispara sinais?
            if trigger:
                A.trigger_collision(self)
                B.trigger_collision(self)
            if clear:
                A.remove_contact(self)
                B.remove_contact(self)

    def remove_overlap(self, beta=1.0):
        '''Remove a superposição entre os objetos movendo cada objeto por uma
        fração inversamente proporcional às respectivas massas'''

        normal = self.normal
        A, B = self
        a = A._invmass
        b = B._invmass
        beta /= a + b
        A.move((-beta * a) * normal)
        B.move((beta * b) * normal)

    def baumgarte(self, beta, dt, mindelta=0.3):
        delta = self.delta
        if delta > mindelta:
            A, B = self
            a = A._invmass
            b = B._invmass
            beta *= delta / (a + b) / dt
            a *= beta
            b *= beta
            A._e_vel -= a * self.normal
            B._e_vel += b * self.normal

    def baumgarte_adjust(self, beta, mindelta=0.3):
        delta = self.delta
        if delta > mindelta:
            A, B = self
            a = A._invmass
            b = B._invmass
            beta *= delta / (a + b)
            a *= beta
            b *= beta
            A.move(-a * self.normal)
            B.move(b * self.normal)

    def get_restitution(self):
        '''Retorna o coeficiente de restituição entre os dois objetos'''

        return (self.A.restitution * self.B.restitution) ** 0.5

    def get_friction_coeff(self):
        '''Retorna o coeficiente de restituição entre os dois objetos'''

        return (self.A.dfriction * self.B.dfriction) ** 0.5


class ContactOrdered(Collision):

    '''Um objeto de contato em que o primeiro objeto é sempre mais pesado que
    o segundo'''

    def __init__(self, A, B, world=None, pos=None, normal=None, **kwds):
        if A._invmass > B._invmass:
            B, A = A, B
        super(ContactOrdered, self).__init__(A, B, world, pos, normal, **kwds)


class CollisionGroup(object):

    def __init__(self, collisions):
        pass


if __name__ == '__main__':
    import doctest
    doctest.testmod()
