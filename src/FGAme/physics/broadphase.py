from collections import MutableSequence

from FGAme.mathtools import shadow_y
from FGAme.physics import flags
from FGAme.physics.collision import CBBContact, AABBContact, get_collision


class AbstractCollisionPhase(MutableSequence):
    """
    Base class for BroadPhase and NarrowPhase.
    """

    __slots__ = ('simulation', '_data', '_collision_check')

    def __init__(self, data=[], simulation=None, collision_check=None):
        self.simulation = simulation
        self._data = []
        self._data.extend(data)
        self._collision_check = collision_check or simulation.collision_check

    def __call__(self, objects):
        self.update(objects)
        return self

    def __repr__(self):
        tname = type(self).__name__
        return '%s(%r)' % (tname, self._data)

    def update(self, objects):
        """
        Update list of pairs using the given objects.
        """

        raise NotImplementedError

    def objects(self):
        """
        Iterates over all objects captured in the collision phase.
        """

        objs = set()
        for A, B in self._data:
            objs.add(A)
            objs.add(B)
        return iter(objs)

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


class BroadPhase(AbstractCollisionPhase):
    """
    Broad phase in the collision detection loop.

    Broad phase checks if AABBs or CBBs collide by testing all possible
    collision pairs. This check is accelerated by a swipe algorithm that checks
    that eliminates most O(n^2) checks and performs this phase in O(n log n).
    """

    __slots__ = []

    def immutable_to_mutable_map(self):
        """Retorna a lista de pares encontradas por update"""

        return list(self._data)


class BroadPhaseAABB(BroadPhase):
    """
    AABB based broad phase
    """

    __slots__ = []

    def update(self, L):
        IS_SLEEP = flags.is_sleeping
        can_collide = self._collision_check
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
    """
    CBB based broad phase.
    """

    __slots__ = []

    def update(self, L):
        can_collide = self._collision_check
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
    """
    Mixed strategy that uses both AABBs and CBBS.
    """

    __slots__ = []

    def update(self, L):
        IS_SLEEP = flags.is_sleeping
        can_collide = self._collision_check
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


class NarrowPhase(AbstractCollisionPhase):
    """
    Narrow phase of collision detection: checks collision against the actual
    bounding box of each object.
    """

    __slots__ = []

    def update(self, broad_cols):
        """
        Scan a list of broad collisions.
        """

        # Detecta colisões e atualiza as listas internas de colisões de
        # cada objeto
        self._data = cols = []

        for A, B in broad_cols:
            col = get_collision(A, B)

            if col is not None:
                # A.add_contact(col)
                # B.add_contact(col)
                col.simulation = self.simulation
                cols.append(col)

    def get_groups(self, cols=None):
        """
        Returns all closed collision groups.
        """

        if cols is None:
            cols = self

        meta_cols = BroadPhaseAABB(cols)
