# -*- coding: utf8 -*-
from FGAme.physics import CBBContact, AABBContact
from mathtools import shadow_y


class BroadPhase(object):

    '''Controla a broad-phase do loop de detecção de colisões de uma
    simulação.'''

    def __init__(self):
        self.pairs = []

    def update(self, objects):
        pass

    def __iter__(self):
        for p in self.pairs:
            yield p


class BroadPhaseAABB(BroadPhase):

    '''Implementa a broad-phase detectando todos os pares de AABBs que estão
    em contato no frame'''

    def update(self, objects):
        col_idx = 0
        objects.sort(key=lambda obj: obj.pos.x - obj.cbb_radius)
        self.pairs[:] = []

        # Os objetos estão ordenados. Este loop detecta as colisões da CBB e
        # salva o resultado na lista broad collisions
        for i, A in enumerate(objects):
            A_right = A.xmax
            A_dynamic = A.is_dynamic()

            for j in range(i + 1, len(objects)):
                B = objects[j]

                # Procura na lista enquanto xmin de B for menor que xmax de A
                B_left = B.xmin
                if B_left > A_right:
                    break

                # Não detecta colisão entre dois objetos estáticos/cinemáticos
                if not A_dynamic and not B.is_dynamic():
                    continue
                if A.is_sleep and B.is_sleep:
                    continue

                # Testa a colisão entre as AABBs
                if shadow_y(A, B) <= 0:
                    continue

                # Adiciona à lista de colisões grosseiras
                col_idx += 1
                self.pairs.append(AABBContact(A, B))


class BroadPhaseCBB(BroadPhase):

    '''Implementa a broad-phase detectando todos os pares de CBBs que estão
    em contato no frame'''

    def update(self, objects):
        col_idx = 0
        objects.sort(key=lambda obj: obj.pos.x - obj.cbb_radius)
        self.pairs[:] = []

        # Os objetos estão ordenados. Este loop detecta as colisões da CBB e
        # salva o resultado na lista broad collisions
        for i, A in enumerate(objects):
            A_radius = A.cbb_radius
            A_right = A.pos.x + A_radius
            A_dynamic = A.is_dynamic()

            for j in range(i + 1, len(objects)):
                B = objects[j]
                B_radius = B.cbb_radius

                # Procura na lista enquanto xmin de B for menor que xmax de A
                B_left = B._pos.x - B_radius
                if B_left > A_right:
                    break

                # Não detecta colisão entre dois objetos estáticos/cinemáticos
                if not A_dynamic and not B.is_dynamic():
                    continue
                if A.is_sleep and B.is_sleep:
                    continue

                # Testa a colisão entre os círculos de contorno
                if (A.pos - B.pos).norm() > A_radius + B_radius:
                    continue

                # Adiciona à lista de colisões grosseiras
                col_idx += 1
                self.pairs.append(CBBContact(A, B))
