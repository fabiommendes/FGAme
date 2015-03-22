#-*- coding: utf8 -*-
from FGAme.mathutils import Vector, cross, dot, shadow_x, shadow_y
from FGAme.util import multifunction

#=========================================================================
# Classe Colisão -- representa uma colisão entre dois objetos.
# Resolve a colisão sob demanda.
#=========================================================================


class Collision(object):

    '''Representa a colisão entre dois objetos.

    Subclasses de Collision devem implementar o método .resolve(dt) que resolve
    a colisão entre os objetos respeitando os vínculos de is_dynamic*.
    '''

    def __init__(self, A, B, pos, n, delta=None, world=None):
        self.objects = A, B
        self.world = world
        self.pos = pos
        self.normal = n
        self.delta = delta

    def get_impulse(self, dt=0):
        '''Calcula o impulso devido à colisão. Retorna o impulso gerado pelo
        objeto A em cima do objeto B. (Ou seja: A recebe o negativo do impulso,
        enquanto B recebe o valor positivo).'''

        A, B = self.objects
        pos = self.pos
        n = self.normal
        e = self.rest_coeff()
        mu = self.friction_coeff()

        # Calcula a resposta impulsiva
        vrel = B.vel - A.vel
        J_denom = A._invmass + B._invmass

        if A._invinertia or A._omega:
            x, y = R = pos - A.pos
            vrel -= A._omega * Vector(-y, x)
            J_denom += cross(R, n) ** 2 * A._invinertia

        if B._invinertia or B._omega:
            x, y = R = pos - B.pos
            vrel += B.omega * Vector(-y, x)
            J_denom += cross(R, n) ** 2 * B._invinertia

        # Determina o impulso total
        if not J_denom:
            return 0

        # Não resolve colisão se o impulso estiver orientado a favor da normal
        # Isto acontece se a superposição não cessa no frame seguinte ao da
        # colisão.
        vrel_n = dot(vrel, n)
        if vrel_n > 0:
            return None

        J = -(1 + e) * vrel_n / J_denom

        # Determina influência do atrito
        if mu:
            # Encontra o vetor tangente adequado
            t = Vector(-n.y, n.x)
            if dot(t, vrel) > 0:
                t *= -1

            # Calcula o impulso tangente máximo
            vrel_tan = -dot(vrel, t)
            Jtan = abs(mu * J)

            # Limita a ação do impulso tangente
            A_can_move = A._invmass or A._invinertia
            B_can_move = B._invmass or B._invinertia
            if A_can_move and B_can_move:
                Jtan = min([Jtan, vrel_tan * A.mass, vrel_tan * B.mass])
            elif A_can_move:
                Jtan = min([Jtan, vrel_tan * A.mass])
            elif B_can_move:
                Jtan = min([Jtan, vrel_tan * B.mass])

            return J * n + Jtan * t
        else:
            return J * n

    def resolve(self, dt=0):
        '''Resolve a colisão entre A e B, distribuindo os impulsos de acordo
        com as propriedades can_move* do objeto'''

        A, B = self.objects
        delta = self.delta
        n = self.normal

        # Obtêm propriedades do impulso
        J = self.get_impulse(dt)
        pos = self.pos
        if J is None:
            return

        # Resolve as colisões
        if A._invmass:
            A.apply_impulse(-J)
        if A._invinertia:
            A.apply_aimpulse(cross(pos - A.pos, -J))
        if B._invmass:
            B.apply_impulse(J)
        if B._invinertia:
            B.apply_aimpulse(cross(pos - B.pos, J))

        # Move objetos para evitar as superposições
        if delta is not None:
            if A._invmass and B._invmass:
                A.move(-delta * n / 2)
                B.move(delta * n / 2)
            elif A._invmass:
                A.move(-(delta + 0.1) * n)
            elif B._invmass:
                B.move((delta + 0.1) * n)

        # Pausa objetos, caso a velocidade seja muito baixa
#         if A.is_still() and B.is_still():
#             if self.world.gravity:
#                 g = self.world.gravity
#                 sin_t = cross(g, J) / (J.norm() * g.norm())
#                 if abs(sin_t) < 1e-3:
#                     A.pause()
#                     B.pause()

    def adjust_overlap(self):
        '''Move objects so they finish superposition.'''

        if A.can_move and B.can_move:
            adjust_overlap(A, B, self)
        elif A.can_move:
            avoid_overlap(A, B, self)
        elif B.can_move:
            avoid_overlap(B, A, self)

    def rest_coeff(self):
        '''Retorna o coeficiente de restituição entre os dois objetos'''

        return self.world.rest_coeff if self.world is not None else 1

    def friction_coeff(self):
        '''Retorna o coeficiente de restituição entre os dois objetos'''

        return self.world.dfriction if self.world is not None else 0

    def swapped(self):
        '''Retorna uma colisão com o papel dos objetos A e B trocados'''

        A, B = self.objects
        return Collision(B, A, self.pos, -self.normal, self.world)

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

#=========================================================================
# Funções de detecção e início de resolução de colisão
#=========================================================================


class CollisionError(Exception):

    '''Declara que não existem colisões disponíveis para os dois tipos de
    objetos'''
    pass


@multifunction(None, None)
def get_collision(A, B):
    '''Retorna um objeto de colisão caso ocorra uma colisão com o objeto
    other. Caso não haja colisão, retorna None.

    Esta função é implementada por multidispatch. As classes derivadas de
    PhysicsObject devem registrar explicitamente a colisão entre todos os pares
    suportados (ex.: Circle com Circle, Circle com AABB, etc). Caso não tenha
    nenhuma implementação registrada, então utiliza-se a lógica de AABB's.'''

    tA = type(A).__name__
    tB = type(B).__name__
    raise CollisionError('no collision defined for: (%s, %s)' % (tA, tB))


def get_collision_aabb(A, B):
    '''Retorna uma colisão com o objeto other considerando apenas a caixas
    de contorno alinhadas ao eixo.'''

    # Detecta colisão pelas sombras das caixas de contorno
    shadowx = shadow_x(A, B)
    shadowy = shadow_y(A, B)
    if shadowx <= 0 or shadowy <= 0:
        return None

    # Calcula ponto de colisão
    x_col = max(A.xmin, B.xmin) + shadowx / 2.
    y_col = max(A.ymin, B.ymin) + shadowy / 2.
    pos_col = Vector(x_col, y_col)

    # Define sinal dos vetores normais: colisões tipo PONG
    if shadowx > shadowy:
        n = Vector(0, (1 if A.ymin < B.ymin else -1))
    else:
        n = Vector((1 if A.xmin < B.xmin else -1), 0)

    return Collision(A, B, pos_col, n)
