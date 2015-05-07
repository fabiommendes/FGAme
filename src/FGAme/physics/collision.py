# -*- coding: utf8 -*-
from FGAme.mathutils import Vec2
from FGAme.util import lazy


class Contact(object):

    '''Representa algum contato ou conexão entre dois objetos'''


class Collision(Contact):
    pass


class CoarseCollision(Contact):

    '''Representa um par de objetos que as caixas de contorno grosseiras
    estão em colisão'''


class CBBCollision(CoarseCollision):

    '''Representa um par de objetos que possuem as'''


class AABBCollision(CoarseCollision):

    ''''''

###############################################################################
#                         Classe Colisão
# ----------------------------------------------------------------------------
#
# Representa uma colisão entre dois objetos.  Resolve a colisão sob demanda.
#
###############################################################################


class FineCollision(Collision):

    '''Representa a colisão entre dois objetos.

    Subclasses de FineCollision devem implementar o método .resolve(dt) que resolve
    a colisão entre os objetos respeitando os vínculos de is_dynamic*.

    Example
    -------

    Considere a colisão entre estas duas figuras geométricas

    >>> from FGAme.physics import Rectangle
    >>> A = Rectangle(rect=(0, 0, 1, 1), vel=(1, 0), mass=1)
    >>> B = Rectangle(rect=(1, 1, 2, 1), mass=2)

    A colisão se dá no ponto (1, 1) e escolhemos a normal para atuar na
    direção x

    >>> col = FineCollision(A, B,
    ...                 pos=(1, 1),    # ponto de colisão
    ...                 normal=(1, 0)) # normal da colisão

    Com o objeto col, podemos calcular várias propriedades físicas, como por
    exemplo as velocidades relativas, no ponto de colisão, o impulso escalar
    e o vetorial, etc

    >>> col.vrel_contact; col.J_normal
    Vec2(-1, 0)
    1.1904761904761905

    Vemos os valores iniciais das grandezas físicas

    >>> col.kineticE; col.momentumP; col.momentumL
    0.5
    Vec2(1, 0)
    0.0


    Resolvemos a colisão simplesmente evocando o método `resolve()` e depois
    consultamos os valores finais das grandezas físicas

    >>> col.resolve()
    >>> col.kineticE; col.momentumP; col.momentumL
    '''

    def __init__(self, A, B, world=None, pos=None, normal=None, **kwds):
        self._A = A
        self._B = B
        self.objects = A, B
        self.world = world
        self.is_active = True
        self.resolved = False
        self.pos = None if pos is None else Vec2(pos)
        self.normal = None if pos is None else Vec2(normal)
        self.__dict__.update(kwds)

    ###########################################################################
    #                 Propriedades calculadas sob demanda
    ###########################################################################
    @lazy
    def tangent(self):
        '''Vetor unitário tangente à colisão'''

        n = self.normal
        tangent = Vec2(-n.y, n.x)
        if tangent.dot(self.vrel_contact) > 0:
            tangent *= -1
        return tangent

    @lazy
    def delta(self):
        '''Tamanho da superposição entre A e B'''

        return 0

    @lazy
    def vrel_cm(self):
        '''Velocidade relativa do centro de massa entre A e B'''

        return self._B.vel - self._A.vel

    @lazy
    def vrel_contact(self):
        '''Velocidade relativa entre o ponto de contato provável de A com B'''

        A, B = self.objects
        pos = self.pos
        vrel = self.vrel_cm

        if A._invinertia or A.omega:
            x, y = pos - A.pos
            vrel -= Vec2(-y, x) * A.omega

        if B._invinertia or B.omega:
            x, y = pos - B.pos
            vrel += Vec2(-y, x) * B.omega

        return vrel

    @lazy
    def J_normal(self):
        '''Valor absoluto do impulso normal antes de considerar o efeito do
        atrito no cálculo da componente tangencial'''

        A, B = self.objects
        pos = self.pos
        n = self.normal
        J_denom = A._invmass + B._invmass

        if A._invinertia or A.omega:
            R = pos - A.pos
            J_denom += R.cross(n) ** 2 * A._invinertia

        if B._invinertia or B.omega:
            R = pos - B.pos
            J_denom += R.cross(n) ** 2 * B._invinertia

        # Determina o impulso total
        if J_denom == 0.0:
            return 0.0

        vrel_n = self.vrel_contact.dot(n)
        if vrel_n > 0:
            return 0.0

        return -(1 + self.e) * vrel_n / J_denom

    @lazy
    def J_tangent(self):
        '''Retorna o módulo da componente tangencial do atrito'''

        A, B = self.objects
        vrel = self.vrel_contact

        # Calcula o impulso tangente máximo
        vrel_tan = -vrel.dot(self.tangent)
        Jtan_max = abs(self.mu * self.J_normal)

        # Limita a ação do impulso tangente
        A_can_move = A._invmass or A._invinertia
        B_can_move = B._invmass or B._invinertia

        # Calcula o tangente dependendo do estado dinâmico de cada objeto
        if A_can_move and B_can_move:
            return min([Jtan_max, vrel_tan * A.mass, vrel_tan * B.mass])
        elif A_can_move:
            return min([Jtan_max, vrel_tan * A.mass])
        elif B_can_move:
            return min([Jtan_max, vrel_tan * B.mass])
        else:
            return 0.0

    @lazy
    def J_vec(self):
        '''Retorna o impulso vetorial contemplando tanto a componente
        tangencial quanto a normal'''

        if self.mu:
            return self.J_normal * self.normal + self.J_tangent * self.tangent
        else:
            return self.J_normal * self.normal

    @lazy
    def mu(self):
        return self.get_friction_coeff()

    @lazy
    def e(self):
        return self.get_restitution_coeff()

    @property
    def pos_cm(self):
        A, B = self.objects
        return (A. mass * A.vel + B.mass * B.vel) / (A.mass + B.mass)

    @property
    def kineticE(self):
        return self._A.kineticE() + self._B.kineticE()

    @property
    def momentumP(self):
        return self._A.momentumP() + self._B.momentumP()

    @property
    def momentumL(self):
        pos = self.pos_cm
        return self._A.momentumL(pos) + self._B.momentumL(pos)

    ###########################################################################
    #                       Métodos da API de FineCollision
    ###########################################################################

    def resolve(self, dt=0):
        '''Resolve a colisão entre A e B, distribuindo os impulsos de acordo
        com as propriedades can_move* do objeto'''

        A, B = self.objects

        # Impulso nulo
        if not self.J_normal or self.resolved:
            self.resolved = True
            return None

        # Move objetos para evitar as superposições
        self.adjust_overlap()

        # Resolve as colisões
        J = self.J_vec
        pos = self.pos
        if A._invmass:
            A.apply_impulse(-J)
        if A._invinertia:
            A.apply_aimpulse((pos - A.pos).cross(-J))
        if B._invmass:
            B.apply_impulse(J)
        if B._invinertia:
            B.apply_aimpulse((pos - B.pos).cross(J))
        self.resolved = True

    def adjust_overlap(self):
        '''Move objetos para encerrar a superposição.'''

        A, B = self.objects
        mu = (A._invmass + B._invmass)
        alpha = A._invmass / mu
        beta = B._invmass / mu
        A.move(-alpha * self.normal)
        B.move(beta * self.normal)

    def get_restitution_coeff(self):
        '''Retorna o coeficiente de restituição entre os dois objetos'''

        return self.world.rest_coeff if self.world is not None else 1

    def get_friction_coeff(self):
        '''Retorna o coeficiente de restituição entre os dois objetos'''

        return self.world.dfriction if self.world is not None else 0

    def swapped(self):
        '''Retorna uma colisão com o papel dos objetos A e B trocados'''

        A, B = self.objects
        return FineCollision(B, A,
                             pos=self.pos, normal=-self.normal,
                             world=self.world)

    def other(self, obj):
        '''Se for chamada com o objeto A, retorna o objeto B e vice-versa'''

        A, B = self.objects
        if obj is A:
            return B
        elif obj is B:
            return A
        else:
            raise ValueError('object does not participate in the collision')

    @property
    def object_A(self):
        return self.objects[0]

    @property
    def object_B(self):
        return self.objects[1]

if __name__ == '__main__':
    import doctest
    doctest.testmod()
