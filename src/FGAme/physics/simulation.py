# -*- coding: utf8 -*-

from FGAme.mathutils import Vec2
from FGAme.physics import get_collision, get_collision_generic, CollisionError
from FGAme.physics import flags
from FGAme.core import EventDispatcher, signal

###############################################################################
#                                Simulação
# ----------------------------------------------------------------------------
# Coordena todos os objetos com uma física definida e resolve a interação
# entre eles
###############################################################################


class Simulation(EventDispatcher):

    '''Implementa a simulação de física.

    Os métodos principais são: add(obj) e remove(obj) para adicionar e remover
    objetos e update(dt) para atualizar o estado da simulação. Verifique a
    documentação do método update() para uma descrição detalhada sobre como
    a física é resolvida em cada etapa de simulação.
    '''

    def __init__(self, gravity=None, damping=0, adamping=0,
                 rest_coeff=1, sfriction=0, dfriction=0, max_speed=None,
                 bounds=None):

        super(Simulation, self).__init__()
        self._objects = []
        self._broad_collisions = []
        self._fine_collisions = []

        # Inicia a gravidade e as constantes de força dissipativa
        self.gravity = gravity or (0, 0)
        self.damping = damping
        self.adamping = adamping

        # Colisão
        self.rest_coeff = float(rest_coeff)
        self.sfriction = float(sfriction)
        self.dfriction = float(dfriction)
        self.max_speed = max_speed

        # Limita mundo
        self.bounds = bounds
        self._out_of_bounds = set()

        # Inicializa constantes de simulação
        self._dt = 0.0
        self.num_frames = 0
        self.time = 0

    ###########################################################################
    #                           Serviços Python
    ###########################################################################
    def __iter__(self):
        return iter(self._objects)

    def __contains__(self, obj):
        return obj in self._objects

    frame_enter = signal('frame-enter')
    collision = signal('collision', num_args=1)

    ###########################################################################
    #                             Propriedades
    ###########################################################################

    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value):
        try:
            gravity = self._gravity = Vec2(*value)
        except TypeError:
            gravity = self._gravity = Vec2(0, -value)

        for obj in self:
            if not obj.owns_gravity:
                obj._gravity = gravity

    @property
    def damping(self):
        return self._damping

    @damping.setter
    def damping(self, value):
        value = self._damping = float(value)

        for obj in self._objects:
            if not obj.owns_damping:
                obj._damping = value

    @property
    def adamping(self):
        return self._adamping

    @adamping.setter
    def adamping(self, value):
        value = self._adamping = float(value)

        for obj in self._objects:
            if not obj.owns_adamping:
                obj._adamping = value

    ###########################################################################
    #                   Gerenciamento de objetos e colisões
    ###########################################################################
    def add(self, obj):
        '''Adiciona um novo objeto ao mundo.

        Exemplos
        --------

        >>> from FGAme import *
        >>> obj = AABB(bbox=(-10, 10, -10, 10))
        >>> world = World()
        >>> world.add(obj, layer=1)
        '''

        if obj not in self._objects:
            self._objects.append(obj)
            if not obj.owns_gravity:
                obj._gravity = self.gravity
            if not obj.owns_damping:
                obj._damping = self.damping
            if not obj.owns_adamping:
                obj._adamping = self.adamping

    def remove(self, obj):
        '''Descarta um objeto da simulação'''

        try:
            del self._objects[self._objects.index(obj)]
        except IndexError:
            pass

    ###########################################################################
    #                     Simulação de Física
    ###########################################################################
    def update(self, dt):
        '''Rotina principal da simulação de física.'''

        self.trigger_frame_enter()
        self._dt = float(dt)

        # Loop genérico
        self.update_accelerations()
        self.resolve_accelerations()
        self.broad_phase()
        self.fine_phase()
        self.resolve_collisions()
        self.time += self._dt
        self.num_frames += 1

        # Serviços esporáticos que não são realizados em todos os frames
        if self.num_frames % 2 == 0:
            self.find_out_of_bounds()
        elif self.num_frames % 2 == 1:
            self.enforce_max_speed()

    def broad_phase(self):
        '''Detecta todas as possíveis colisões utilizando um algoritmo
        grosseiro de detecção.

        Esta função implementa a detecção via CBB (Circular bounding box), e
        salva todas os pares de possíveis objetos em colisão numa lista
        interna.'''

        objects = self._objects
        col_idx = 0
        objects.sort(key=lambda obj: obj._pos._x - obj.cbb_radius)
        self._broad_collisions[:] = []

        # Os objetos estão ordenados. Este loop detecta as colisões da CBB e
        # salva o resultado na lista broad collisions
        for i, A in enumerate(objects):
            A_radius = A.cbb_radius
            A_right = A._pos._x + A_radius
            A_dynamic = A.is_dynamic()

            for j in range(i + 1, len(objects)):
                B = objects[j]
                B_radius = B.cbb_radius

                # Procura na lista enquanto xmin de B for menor que xmax de A
                B_left = B._pos._x - B_radius
                if B_left > A_right:
                    break

                # Não detecta colisão entre dois objetos estáticos/cinemáticos
                if not A_dynamic and not B.is_dynamic():
                    continue

                # Testa a colisão entre os círculos de contorno
                if (A._pos - B._pos).norm() > A_radius + B_radius:
                    continue

                # Adiciona à lista de colisões grosseiras
                col_idx += 1
                self._broad_collisions.append((A, B))

    def fine_phase(self):
        '''Escaneia a lista de colisões grosseiras e detecta quais delas
        realmente aconteceram'''
        # Detecta colisões e atualiza as listas internas de colisões de
        # cada objeto
        self._fine_collisions[:] = []

        for A, B in self._broad_collisions:
            col = self.get_fine_collision(A, B)

            if col is not None:
                col.world = self
                self._fine_collisions.append(col)

    def update_accelerations(self):
        '''Atualiza o vetor interno que mede as acelerações lineares e
        angulares de cada objeto.

        Para tanto, usa informação tanto de forças globais quanto dos atributos
        *force* e *torque* de cada objeto.'''

        t = self.time
        dt = self._dt
        ACCEL_STATIC = flags.ACCEL_STATIC
        ALPHA_STATIC = 0  # flags.ALPHA_STATIC

        # Acumula as forças e acelerações
        for obj in self._objects:
            if obj._invmass:
                obj.init_accel()
                if obj.force is not None:
                    obj._accel += obj.force(t) * obj._invmass

            elif obj.flags & ACCEL_STATIC:
                obj.init_accel()
                obj.apply_accel(obj._accel, dt)

            if obj._invinertia:
                obj.init_alpha()
                if obj.torque is not None:
                    obj._alpha += obj.torque(t) * obj._invinertia

            elif obj.flags & ALPHA_STATIC:
                obj.init_alpha()
                obj.apply_alpha(self._alpha, dt)

    def resolve_accelerations(self):
        '''Resolve as acelerações acumuladas em update_accelerations()'''

        dt = self._dt
        for obj in self._objects:
            if obj._invmass:
                obj.apply_accel(None, dt)
            elif obj._vel._x or obj._vel.y:
                obj.move(obj._vel * dt)

            if obj._invinertia:
                obj.apply_alpha(None, dt)
            elif obj.omega:
                obj.irotate(obj.omega * dt)

    def resolve_collisions(self):
        '''Resolve as colisões'''

        for col in self._fine_collisions:
            A, B = col.objects
            A.trigger('collision', col)
            B.trigger('collision', col)
            if col.is_active:
                col.resolve()

    def get_fine_collision(self, A, B):
        '''Retorna a colisão entre os objetos A e B depois que a colisão AABB
        foi detectada'''

        try:
            return get_collision(A, B)
        except CollisionError:
            pass

        # Colisão não definida. Primeiro tenta a colisão simétrica e registra
        # o resultado caso bem sucedido. Caso a colisão simétrica também não
        # seja implementada, define a colisão como uma aabb
        try:
            col = get_collision(B, A)
            if col is None:
                return
            col.normal *= -1
        except CollisionError:
            get_collision[type(A), type(B)] = get_collision_generic
            get_collision[type(B), type(A)] = get_collision_generic
            return get_collision_generic(A, B)
        else:
            direct = get_collision.get_implementation(type(B), type(A))

            def inverse(A, B):
                '''Automatically created collision for A, B from the supported
                collision B, A'''
                col = direct(B, A)
                if col is not None:
                    return col.swapped()

            get_collision[type(A), type(B)] = inverse
            return col

    # Cálculo de parâmetros físicos ###########################################
    def kinetic_energy(self):
        '''Retorna a soma da energia cinética de todos os objetos do mundo'''

        return sum(obj.kinetic() for obj in self.objects)

    # Serviços esporáticos ####################################################
    def enforce_max_speed(self):
        '''Força que todos objetos tenham uma velocidade máxima'''

        if self.max_speed is not None:
            vel = self.max_speed
            vel_sqr = self.max_speed ** 2

            for obj in self._objects:
                if obj._vel.norm_sqr() > vel_sqr:
                    obj._vel *= vel / obj._vel.norm()

    def find_out_of_bounds(self):
        '''Emite o sinal de "out-of-bounds" para todos os objetos da
        simulação que deixarem os limites estabelecidos'''

        if self.bounds is not None:
            xmin, xmax, ymin, ymax = self.bounds
            out = self._out_of_bounds

            for obj in self._objects:
                x, y = obj._pos
                is_out = True

                if x > xmax and obj.xmin > xmax:
                    direction = 0
                elif y > ymax and obj.ymin > ymax:
                    direction = 1
                elif x < xmin and obj.xmax < xmin:
                    direction = 2
                elif y < ymin and obj.ymax < ymin:
                    direction = 3
                else:
                    is_out = False

                if is_out and obj not in out:
                    out.add(obj)
                    obj.trigger_out_of_bounds(direction)
                else:
                    out.discard(obj)

    def burn(self, frames, dt=0.0):
        '''Executa a simulação por um número específico de frames sem deixar
        o tempo rodar'''

        time = self.time
        for _ in range(frames):
            self.update(dt)
            self.time = time

    def remove_superpositions(self, num_iter=1):
        '''Remove todas as superposições entre objetos dinâmicos'''

        self._dt = 0.0
        for _ in range(num_iter):
            self.broad_phase()
            self.fine_phase()

            for col in self._fine_collisions:
                col.adjust_overlap()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
