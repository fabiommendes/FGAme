import copy
from _warnings import warn
from math import sqrt, pi

from generic import generic

from FGAme.mathtools import Vec2, asvector, ux2D
from FGAme.physics import pre_collision_signal, post_collision_signal

DEFAULT_DIRECTIONS = [ux2D.rotate(n * pi / 12) for n in
                      [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11]]


class CollisionError(Exception):
    """
    Error during collision detection.
    """


class ContactPoint(Vec2):
    """
    A contact point with a level of penetration.
    """

    __slots__ = ('depth',)

    def __init__(self, x, y, depth):
        super().__init__(x, y)
        self.depth = depth


class BaseContactManifold(object):
    def __iter__(self):
        return iter(self.points)


class ContactManifold(BaseContactManifold):
    """Representa uma lista de pontos de contato associados a uma única
    normal."""

    __slots__ = ('normal', 'points')

    def __init__(self, normal, points):
        self.normal = normal.normalize()
        self.points = list(points)


class SimpleContactManifold(BaseContactManifold):
    """Representa um contato simples com apenas um ponto"""

    __slots__ = ['normal', 'point']

    def __init__(self, normal, point):
        self.normal = normal
        self.point = point

    @property
    def points(self):
        return [self.point]

    def __iter__(self):
        yield self.point


class Pair(object):
    """
    A pair of physical objects.
    """

    __slots__ = ('_A', '_B')

    def __init__(self, A, B):
        self.A = A
        self.B = B

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

    def iswap(self):
        """
        Swap objects *INPLACE*.
        """

        self.B, self.A = self.A, self.B

    def swap(self):
        """
        Return a new pair of swap objects.
        """

        new = self.copy()
        new.iswap()
        return new

    def other(self, obj):
        """
        Return the other object in the pair.

        Raises ValueError if obj is not in the pair.
        """

        if obj is self.A:
            return self.B
        elif obj is self.B:
            return self.A
        else:
            raise ValueError('object does not participate in the connection')

    def copy(self):
        """
        Return a copy of pair
        """

        return copy.copy(self)

    def center_of_mass(self):
        """
        Center of mass of the two objects.
        """

        A, B = self
        return (A.mass * A.pos + B.mass * B.pos) / (A.mass + B.mass)

    def energyK(self):
        """
        Total kinetic energy.
        """
        return self.A.energyK() + self.B.energyK()

    def momentumP(self):
        """
        Total linear momentum.
        """
        return self.A.momentumP() + self.B.momentumP()

    def momentumL(self):
        """
        Total angular momentum.
        """

        pos = (0, 0)
        return self.A.momentumL(pos) + self.B.momentumL(pos)


class BroadContact(Pair):
    """
    Contact in broad phase.

    Objects are close to each other and might or might not be touching.
    """

    def get_collision(self):
        """
        Return the collision object if there is superposition.
        """

        raise NotImplementedError


class CBBContact(BroadContact):
    """
    Broad phase contact using circular bounding boxes.
    """


class AABBContact(BroadContact):
    """
    Broad phase contact using AABBs.
    """


class Collision(Pair):
    """
    Collision between two overlapping objects.
    """

    def __init__(self, A, B, normal=None, pos=None, delta=0.0):
        super(Collision, self).__init__(A, B)
        self.normal = normal = asvector(normal)
        self.pos = pos = asvector(pos)
        self.delta = delta = float(delta)
        self.restitution = sqrt(A.restitution * B.restitution)
        self.friction = sqrt(A.friction * B.friction)
        self.active = True

    def iswap(self):
        super().iswap()
        self.normal *= -1

    def resolve(self):
        """
        Solve for velocities of each element in the collision pair.
        """

        if self.friction:
            self.__resolve_with_friction()
        else:
            self.__resolve_simple()

    def __resolve_simple(self):
        """
        Solve frictionless collision.
        """

        A, B = self
        pos = self.pos
        normal = self.normal
        vrel = B.vpoint(pos) - A.vpoint(pos)
        vrel_normal = vrel.dot(normal)

        if vrel_normal < 0:
            # Relative positions
            rA = pos - A.pos
            rB = pos - B.pos

            # Effective mass
            invmass = A.invmass + B.invmass
            invmass += A.invinertia * (rA.cross(normal) ** 2)
            invmass += B.invinertia * (rB.cross(normal) ** 2)
            effmass = 1.0 / invmass

            # Normal impulse
            Jn = effmass * (1 + self.restitution) * vrel_normal
            Jvec = Jn * normal

            # Total impulse
            A.apply_impulse_at(Jvec, pos)
            B.apply_impulse_at(-Jvec, pos)

    def __resolve_with_friction(self):
        """
        Solve collision with friction.
        """

        A, B = self
        normal = self.normal
        pos = self.pos
        vrel = B.vpoint(pos) - A.vpoint(pos)
        vrel_normal = vrel.dot(normal)
        friction = self.friction
        restitution = self.restitution

        if vrel_normal < 0:
            # Tangent vector
            tangent = normal.perp()
            vrel_tangent = vrel.dot(tangent)
            if vrel_tangent < 0:
                vrel_tangent *= -1
                tangent *= -1

            # Relative positions
            rA = pos - A.pos
            rB = pos - B.pos
            rA_n, rA_t = rA.dot(normal), rA.dot(tangent)
            rB_n, rB_t = rB.dot(normal), rB.dot(tangent)

            # Inverse effective masses
            invmassN = (A.invmass + A.invinertia * rA.cross(normal) ** 2 +
                        B.invmass + B.invinertia * rB.cross(normal) ** 2)
            invmassT = (A.invmass + A.invinertia * rA.cross(tangent) ** 2 +
                        B.invmass + B.invinertia * rB.cross(tangent) ** 2)
            invmassD = A.invinertia * rA_n * rA_t + B.invinertia * rB_n * rB_t

            # Precisamos encontrar o valor do vetor J = Jn * n + Jt * t, onde
            # as componentes Jn e Jt são desconhecidas.
            # 
            # Existem alguns guias para realizar esta tarefa. O primeiro é a 
            # relação entre as velocidades relativas normais antes e depois
            # da colisão. Isto é dado pela expressão do coeficiente de 
            # restituição e resulta em
            #
            #     Jn / Mn - Jt / Md = (1 + e) * urel_n 
            #
            # Posteriormente, queremos aplicar a lei de Coulomb para o atrito,
            # que estabelece que a força de atrito máxima carrega a seguinte
            # relação com a normal 
            #
            #     |Ft| = mu * |Fn|,
            #
            # o que se traduz imediatamente em uma expressão para os impulsos:
            #
            #     |Jt| = mu * |Jn|,
            #
            # Sabemos que Jt > 0, pois o vetor de velocidade relativa está 
            # alinhado ao tangente. A força de atrito produz um impulso na
            # direção de t para o corpo A e na direção oposta para B. Já Jn < 0,
            # pois o impulso que o corpo A recebe deve ser necessariamente na
            # direção oposta à normal. A relação anterior fica portanto
            #
            #     Jt = -mu * Jn.
            #
            # Onde esperamos obter apenas o valor máximo do impulso devido ao 
            # atrito. Como então saber se o atrito satura ou se o valor máximo
            # deve ser utilizado? Usamos o critério de que o sinal da velocidade
            # relativa tangencial de saída deve permanecer positivo: ou seja,
            # o atrito é capaz de interromper o deslocamento tangencial, mas 
            # não de invertê-lo. 
            #
            # Assim, usa-se o critério:
            #
            #     vrel_tangent' >= 0,
            #
            # onde,
            #
            #     vrel_tangent' = vrel_tangent - Jn / Md + Jt / Mt
            #
            # Caso o critério acima seja violado, igualamos a velocidade 
            # tangencial a zero e usamos esta condição como condição suplementar
            # à da definição do coeficiente de restituição.
            #

            # Firstly, assume the non-saturated case.
            Jn = (1 + restitution) * vrel_normal / (
                invmassN - friction * invmassD)
            Jt = -friction * Jn
            vrel_tangent_out = vrel_tangent + invmassD * Jn - invmassT * Jt

            # Verifica o sinal da velocidade de saída. Se for negativo, 
            # assume que o atrito saturou e que devemos usar o critério
            # de que a velocidade tangencial de saída deve ser nula.
            if vrel_tangent_out < 0:
                denom = invmassT * invmassN - invmassD ** 2  # <= 0
                Jn = ((1 + restitution) * vrel_normal * invmassT +
                      invmassD * vrel_tangent) / denom
                Jt = ((1 + restitution) * vrel_normal * invmassD +
                      invmassN * vrel_tangent) / denom

                # Is it fair?
                if Jt < 0:
                    Jtmax = vrel_tangent / (invmassD / friction + invmassT)
                    Jn = (1 + restitution) * vrel_normal / invmassN
                    Jt = min(-friction * Jn, Jtmax)

            # Total impulse
            Jvec = Jn * normal + Jt * tangent
            A.apply_impulse_at(Jvec, pos=pos)
            B.apply_impulse_at(-Jvec, pos=pos)

    def cancel(self):
        """
        Cancel collision resolution.
        """

        self.active = False

    def pre_collision(self, simulation):
        """
        Executed before solving collisions.
        """

        A, B = self
        A.pre_collision(self)
        B.pre_collision(self)
        pre_collision_signal.trigger(simulation, self)
        if self.active:
            if A.invmass:
                A.collisions.append(self)
            if B.invmass:
                B.collisions.append(self)

    def post_collision(self, simulation):
        """
        Executed after solving collisions.
        """

        A, B = self
        A.post_collision(self)
        B.post_collision(self)
        post_collision_signal.trigger(simulation, self)
        if A.invmass:
            A.collisions.remove(self)
        if B.invmass:
            B.collisions.remove(self)

    def is_simple(self):
        """
        Return True if the current collision is the only contact for both
        objects.
        """

        return (len(self.A._contacts) <= 1) and (len(self.B._contacts) <= 1)

    def remove_overlap(self, beta=1.0):
        """
        Remove superposition between both objects by moving each one to a
        distance inversely proportional to their masses.
        """

        normal = self.normal
        A, B = self
        a = A._invmass
        b = B._invmass
        beta /= a + b
        A.move((-beta * a) * normal)
        B.move((beta * b) * normal)

    def baumgarte(self, beta, mindelta=0.3):
        """
        Baumgarte correction that gradually removes superposition between two
        objects.
        """

        delta = self.delta
        if delta > mindelta:
            A, B = self
            delta = 0.5 * delta
            Z = A.invmass + B.invmass
            delta_a = delta * A.invmass / Z
            delta_b = delta * B.invmass / Z
            if delta_a:
                A.move(-delta_a * self.normal)
            if delta_b:
                B.move(delta_b * self.normal)


class ContactOrdered(Collision):
    """
    Ordered collision object in which the first object is always heavier.

    It might swap A and B during creation.
    """

    def __init__(self, A, B, world=None, pos=None, normal=None, **kwds):
        if A._invmass > B._invmass:
            B, A = A, B
        super(ContactOrdered, self).__init__(A, B, world, pos, normal, **kwds)


class Island(object):
    def __init__(self, collisions):
        self.collisions = collisions


@generic
def get_collision(A, B, collision_class=Collision):
    """
    Return a collision object between A and B or None if there is no
    superposition.

    This is a multi-dispatch function. Derived classes must implement each
    collision pair or else objects will not collide.
    """

    tA = type(A).__name__
    tB = type(B).__name__
    warn('no collision defined for: (%s, %s)' % (tA, tB))

    return None
