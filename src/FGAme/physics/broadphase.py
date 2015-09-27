# -*- coding: utf8 -*-

from collections import MutableSequence
from FGAme.mathtools import shadow_y
from FGAme.physics import CBBContact, AABBContact
from FGAme.physics import get_collision
from FGAme.physics.flags import BodyFlags


class AbstractCollisionPhase(MutableSequence):

    '''Base para BroadPhase e NarrowPhase'''

    __slots__ = ['world', '_data']

    def __init__(self, data=[], world=None):
        self.world = world
        self._data = []
        self._data.extend(data)

    def __call__(self, objects):
        self.update(objects)
        return self

    def __repr__(self):
        tname = type(self).__name__
        return '%s(%r)' % (tname, self._data)

    def update(self, objects):
        '''Atualiza a lista de pares utilizando a lista de objetos dada.'''

        raise NotImplementedError

    def objects(self):
        '''Iterador sobre a lista com todos os objetos obtidos na fase de
        colisão'''

        objs = set()
        for A, B in self._data:
            objs.add(A)
            objs.add(B)
        return iter(objs)

    # MutableSequence interface ###############################################
    def __len__(self):
        return len(self._data)

    def __iter__(self):
        for p in self._data:
            yield p

    def __getitem__(self, i):
        return self._data[i]

    def __setitem__(self, i, value):
        self._data[i] = value

    def __delitem__(self, i, value):
        del self._data[i]

    def pop(self, idx=None):
        if idx is None:
            return self._data.pop()
        else:
            return self._data.pop(idx)

    def insert(self, idx, value):
        self._data.insert(idx, value)

    def append(self, value):
        self._data.append(value)

    def remove(self, value):
        self._data.remove(value)

    def sort(self, *args, **kwds):
        self._data.sort(*args, **kwds)

###############################################################################
#                               Broad phase
###############################################################################


class BroadPhase(AbstractCollisionPhase):

    '''Controla a broad-phase do loop de detecção de colisões de uma
    simulação.

    Um objeto do tipo BroadPhase possui uma interface simples que define dois
    métodos:

        bf.update(L) -> executa algoritmo em lista de objetos L
        iter(bf)     -> itera sobre todos os pares gerados no passo anterior

    '''

    __slots__ = []

    def pairs(self):
        '''Retorna a lista de pares encontradas por update'''

        return list(self._data)


class BroadPhaseAABB(BroadPhase):

    '''Implementa a broad-phase detectando todos os pares de AABBs que estão
    em contato no frame'''

    __slots__ = []

    def update(self, L):
        IS_SLEEP = BodyFlags.is_sleeping
        can_collide = self.world.can_collide
        col_idx = 0
        objects = sorted(L, key=lambda obj: obj.xmin)
        self._data[:] = []

        # Os objetos estão ordenados. Este loop detecta as colisões da CBB e
        # salva o resultado na lista broad collisions
        for i, A in enumerate(objects):
            A_right = A.xmax
            A_dynamic = A.is_dynamic()

            for j in range(i + 1, len(objects)):
                B = objects[j]
                if not can_collide(A, B):
                    continue

                # Procura na lista enquanto xmin de B for menor que xmax de A
                B_left = B.xmin
                if B_left > A_right:
                    break

                # Não detecta colisão entre dois objetos estáticos/cinemáticos
                if not A_dynamic and not B.is_dynamic():
                    continue
                if A.flags & B.flags & IS_SLEEP:
                    continue

                # Testa a colisão entre as AABBs
                if shadow_y(A, B) <= 0:
                    continue

                # Adiciona à lista de colisões grosseiras
                col_idx += 1
                self._data.append(AABBContact(A, B))


class BroadPhaseCBB(BroadPhase):

    '''Implementa a broad-phase detectando todos os pares de CBBs que estão
    em contato no frame'''

    __slots__ = []

    def update(self, L):
        can_collide = self.world.can_collide
        L = sorted(L, key=lambda obj: obj.pos.x - obj.cbb_radius)
        N = len(L)
        self._data[:] = []

        # Os objetos estão ordenados. Este loop detecta as colisões da CBB e
        # salva o resultado na lista broad collisions
        for i, A in enumerate(L):
            rA = A.cbb_radius
            Amax = A.pos.x + rA

            for j in range(i + 1, N):
                B = L[j]
                if not can_collide(A, B):
                    continue
                rB = B.cbb_radius

                # Procura na lista enquanto xmin de B for menor que xmax de A
                if B._pos.x - rB > Amax:
                    break

                # Testa a colisão entre os círculos de contorno
                if (A.pos - B.pos).norm() > rA + rB:
                    continue

                # Adiciona à lista de colisões grosseiras
                self._data.append(CBBContact(A, B))


class BroadPhaseMixed(BroadPhase):

    '''Implementa a broad-phase detectando todos os pares de CBBs que estão
    em contato no frame'''

    __slots__ = []

    def update(self, L):
        IS_SLEEP = BodyFlags.is_sleeping
        can_collide = self.world.can_collide
        col_idx = 0
        objects = sorted(L, key=lambda obj: obj.pos.x - obj.cbb_radius)
        self._data[:] = []

        # Os objetos estão ordenados. Este loop detecta as colisões da CBB e
        # salva o resultado na lista broad collisions
        for i, A in enumerate(objects):
            A_radius = A.cbb_radius
            A_right = A.pos.x + A_radius
            A_dynamic = A.is_dynamic()

            for j in range(i + 1, len(objects)):
                B = objects[j]
                if not can_collide(A, B):
                    continue

                B_radius = B.cbb_radius

                # Procura na lista enquanto xmin de B for menor que xmax de A
                B_left = B._pos.x - B_radius
                if B_left > A_right:
                    break

                # Não detecta colisão entre dois objetos estáticos/cinemáticos
                if not A_dynamic and not B.is_dynamic():
                    continue
                if A.flags & B.flags & IS_SLEEP:
                    continue

                # Testa a colisão entre os círculos de contorno
                if (A.pos - B.pos).norm() > A_radius + B_radius:
                    continue

                # Adiciona à lista de colisões grosseiras
                col_idx += 1
                if has_overlap(A.aabb, B.aabb):
                    self._data.append(AABBContact(A, B))


###############################################################################
#                               Narrow phase
###############################################################################
class NarrowPhase(AbstractCollisionPhase):

    '''Implementa a fase fina da detecção de colisão'''

    __slots__ = []

    def update(self, broad_cols):
        '''Escaneia a lista de colisões grosseiras e detecta quais delas
        realmente aconteceram'''

        # Detecta colisões e atualiza as listas internas de colisões de
        # cada objeto
        self._data = cols = []

        for A, B in broad_cols:
            if A._invmass > B._invmass:
                A, B = B, A
            col = get_collision(A, B)

            if col is not None:
                A.add_contact(col)
                B.add_contact(col)
                col.world = self.world
                cols.append(col)

    def get_groups(self, cols=None):
        '''Retorna uma lista com todos os grupos de colisões fechados'''

        if cols is None:
            cols = self

        meta_cols = BroadPhaseAABB(cols)
        print(meta_cols)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
