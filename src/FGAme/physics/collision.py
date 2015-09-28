# -*- coding: utf8 -*-
from math import sqrt
from FGAme.mathtools import Vec2, asvector


#
# Pontos de Contato/Manifolds
#
class ContactPoint(Vec2):

    '''Representa um ponto de contato com um certo nível de penetração'''

    __slots__ = ['depth']

    def __init__(self, x, y, depth):
        super(Vec2, self).__init__(x, y)
        self.depth = depth


class BaseContactManifold(object):

    '''Classe mãe para ContactManifold restitution SimpleContactManifold'''

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


#
# Contatos abstratos
#
class Pair(object):

    '''Representa alguma ligação, conexão ou agrupamento de dois objetos'''

    __slots__ = ('A', 'B')

    def __init__(self, A, B):
        self.A = A
        self.B = B

    def swap(self):
        '''Troca os dois objetos do par *INPLACE*'''

        self.B, self.A = self.A, self.B

    def swapped(self):
        '''Retorna um par com os elementos trocados'''

        new = self.copy()
        new.swap()
        return new

    def other(self, obj):
        '''Se for chamada com o objeto A, retorna o objeto B e vice-versa'''

        if obj is self.A:
            return self.B
        elif obj is self.B:
            return self.A
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

    #
    # Propriedades físicas
    #
    def center_of_mass(self):
        A, B = self
        return (A. mass * A.pos + B.mass * B.pos) / (A.mass + B.mass)

    def energyK(self):
        return self.A.energyK() + self.B.energyK()

    def momentumP(self):
        return self.A.momentumP() + self.B.momentumP()

    def momentumL(self):
        pos = (0, 0)
        return self.A.momentumL(pos) + self.B.momentumL(pos)

    #
    # Magic methods
    #
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

    def __contains__(self, element):
        return element is self.A or element is self.B


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

    Subclasses de Collision devem implementar o método .resolve() que resolve
    a colisão entre os dois objetos.

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

    Podemos investigar as propriedades físicas da colisão restitution verificar
    que as leis de conservação são preservadas

    >>> col.energyK(); col.momentumP(); col.momentumL()
    0.5
    Vec(1, 0)
    -1.0

    Podemos resolver a colisão utilizando ou o método step() ou o resolve(). O
    segundo é chamado apenas uma vez restitution já aciona os sinais de
    colisão. O método step() é utilizado em resoluções iterativas com vários
    objetos colidindo simultaneamente.

    >>> col.resolve()

    Agora investigamos os valores finais restitution vemos que as leis de
    conservação foram satisfeitas.

    >>> col.energyK(); col.momentumP(); col.momentumL()
    0.5
    Vec(1, 0)
    -1.0

    Investigando as propriedades, verificamos que de fato a velocidade dos dois
    objetos foi invertida

    >>> A.vel; B.vel
    Vec(0, 0)
    Vec(1, 0)


    Suponha agora que a colisão não se deu no ponto selecionado anteriormente.

    >>> A.vel, B.vel = (1, 0), (0, 0)
    >>> col = Collision(A, B,
    ...                 pos=(0, 0),    # ponto de colisão
    ...                 normal=(1, 0)) # normal da colisão

    Esta posição induz a uma velocidade de rotação e transferência de energia
    de movimento linear para angular.

    >>> col.resolve()
    >>> A.linearK() + B.linearK(), A.angularK() + B.angularK(), col.energyK()
    (0.2777777777777778, 0.2222222222222222, 0.5)

    As leis de conservação continuam sendo satisfeitas
    >>> col.energyK(); col.momentumP(); col.momentumL()
    0.5
    Vec(1, 0)
    -1.0
    '''

    def __init__(self, A, B, normal=None, pos=None, delta=0.0):
        super(Collision, self).__init__(A, B)
        self.normal = normal = asvector(normal)
        self.pos = pos = asvector(pos)
        self.delta = delta = float(delta)
        self.active = True

        # Obtêm parâmetros da colisão
        self.restitution = sqrt(A.restitution * B.restitution)
        self.friction = sqrt(A.friction * B.friction)

        # Posições e velocidades relativas
        rA = self.pos - A.pos
        rB = self.pos - B.pos

        # Massa efetiva
        invmass = A.invmass + B.invmass
        invmass += A.invinertia * (rA.cross(normal) ** 2)
        invmass += B.invinertia * (rB.cross(normal) ** 2)
        self.effmass = 1.0 / invmass

        # Asserções
        assert rA.dot(normal) >= 0, 'normal is pointing towards the first body'

    def resolve(self):
        A, B = self
        normal = self.normal
        pos = self.pos
        vrel = B.vpoint(pos) - A.vpoint(pos)
        vrel_normal = vrel.dot(normal)

        if vrel_normal < 0:
            # Impulso normal
            J = self.effmass * (1 + self.restitution) * vrel_normal
            Jvec = J * normal
            pos = self.pos

            # Impulso tangente

            A.apply_impulse(Jvec, pos=pos)
            B.apply_impulse(-Jvec, pos=pos)

    def apply_tangent(self, J):
        # Aplica incremento no impulso
        if J <= 0:
            return

        A, B = self.A, self.B
        vrel = self.vrel
        tangent = self.get_tangent()

        # Calcula o impulso tangente máximo
        vrel_tan = -vrel.dot(tangent)
        Jtan_max = abs(self.friction * J)

        # Limita a ação do impulso tangente
        if A._invmass and B._invmass:
            J = min(Jtan_max, vrel_tan / A._invmass, vrel_tan / B._invmass)
        elif A._invmass:
            J = min(Jtan_max, vrel_tan / A._invmass)
        elif B._invmass:
            J = min(Jtan_max, vrel_tan / B._invmass)
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

    def finalize(self, clear=True, trigger=True):
        if self.impulse > 0:
            self.apply_impulse(self.impulse)
        # self.apply_tangent(self.impulse)

        if trigger:
            # TODO: inspect collision triggers
            # self.A.trigger_collision(self)
            # self.B.trigger_collision(self)
            pass
        if clear:
            self.A.remove_contact(self)
            self.B.remove_contact(self)

    def get_tangent(self):
        # Vetor unitário tangente à colisão
        n = self.normal
        tangent = Vec2(-n.y, n.x)
        if tangent.dot(self.vrel) > 0:
            tangent = -tangent
        return tangent

    ###########################################################################
    #                       Métodos da API de Collision
    ###########################################################################
    def is_simple(self):
        '''Retorna True se o contato for o único contato de ambos os objetos
        envolvidos'''

        print('foo')
        return (len(self.A._contacts) <= 1) and (len(self.B._contacts) <= 1)

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
