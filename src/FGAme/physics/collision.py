# -*- coding: utf8 -*-
from FGAme.core import env
from FGAme.mathutils import Vector, cross, dot
from FGAme.util import lazy

###############################################################################
#                         Classe Colisão
# ----------------------------------------------------------------------------
#
# Representa uma colisão entre dois objetos.  Resolve a colisão sob demanda.
#
###############################################################################


class Collision(object):

    '''Representa a colisão entre dois objetos.

    Subclasses de Collision devem implementar o método .resolve(dt) que resolve
    a colisão entre os objetos respeitando os vínculos de is_dynamic*.
    '''

    def __init__(self, A, B, world=None, **kwds):
        self._A = A
        self._B = B
        self.objects = A, B
        self.world = world
        self.is_active = True
        self.__dict__.update(kwds)

    ###########################################################################
    #                 Propriedades calculadas sob demanda
    ###########################################################################
    @lazy
    def pos(self):
        '''Posição (em coordenadas absolutas) do ponto de contato entre A e
        B'''

        raise NotImplementedError

    @lazy
    def delta(self):
        '''Tamanho da superposição entre A e B'''

        return 0

    @lazy
    def normal(self):
        '''Vetor unitário normal à colisão. Normal sai do corpo A para o B.'''

        raise NotImplementedError

    @lazy
    def tangent(self):
        '''Vetor unitário tangente à colisão'''

        n = self.normal
        tangent = Vector(-n.y, n.x)
        if dot(tangent, self.vrel_contact) > 0:
            tangent *= -1
        return tangent

    @lazy
    def vrel_cm(self):
        '''Velocidade relativa do centro de massa entre A e B'''

        return self._B._vel - self._A._vel

    @lazy
    def vrel_contact(self):
        '''Velocidade relativa entre o ponto de contato provável de A com B'''

        A, B = self.objects
        pos = self.pos
        vrel = self.vrel_cm.copy()

        if A._invinertia or A.omega:
            x, y = pos - A._pos
            vrel -= A.omega * Vector(-y, x)

        if B._invinertia or B.omega:
            x, y = pos - B._pos
            vrel += B.omega * Vector(-y, x)

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
            R = pos - A._pos
            J_denom += cross(R, n) ** 2 * A._invinertia

        if B._invinertia or B.omega:
            R = pos - B._pos
            J_denom += cross(R, n) ** 2 * B._invinertia

        # Determina o impulso total
        if J_denom == 0.0:
            return 0.0

        vrel_n = dot(self.vrel_contact, n)
        if vrel_n > 0:
            return 0.0

        return -(1 + self.e) * vrel_n / J_denom

    @lazy
    def J_tangent(self):
        '''Retorna o módulo da componente tangencial do atrito'''

        A, B = self.objects
        vrel = self.vrel_contact

        # Calcula o impulso tangente máximo
        vrel_tan = -dot(vrel, self.tangent)
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

    ###########################################################################
    #                       Métodos da API de Collision
    ###########################################################################

    def resolve(self, dt=0):
        '''Resolve a colisão entre A e B, distribuindo os impulsos de acordo
        com as propriedades can_move* do objeto'''

        A, B = self.objects

        # Impulso nulo
        if not self.J_normal:
            return None

        # Move objetos para evitar as superposições
        self.adjust_overlap()

        # Resolve as colisões
        J = self.J_vec
        pos = self.pos
        if A._invmass:
            A.apply_impulse(-J)
        if A._invinertia:
            A.apply_aimpulse(cross(pos - A._pos, -J))
        if B._invmass:
            B.apply_impulse(J)
        if B._invinertia:
            B.apply_aimpulse(cross(pos - B._pos, J))

    def adjust_overlap(self):
        '''Move objetos para encerrar a superposição.'''

        A, B = self.objects
        mu = 3 * (A._invmass + B._invmass)
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
        return Collision(B, A,
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
