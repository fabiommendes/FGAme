# -*- coding: utf8 -*-

from collections import defaultdict
from FGAme.mathtools import Vec2, null2D
from FGAme.events import EventDispatcher, signal
from FGAme.physics.flags import BodyFlags
from FGAme.physics.broadphase import BroadPhase, BroadPhaseCBB, NarrowPhase

###############################################################################
#                                Simulação
# ----------------------------------------------------------------------------
# Coordena todos os objetos com uma física definida e resolve a interação
# entre eles
###############################################################################
SLEEP_LINEAR_VELOCITY = 3
SLEEP_ANGULAR_VELOCITY = 0.05


class Simulation(EventDispatcher):

    '''Implementa a simulação de física.

    Os métodos principais são: add(obj) e remove(obj) para adicionar e remover
    objetos e update(dt) para atualizar o estado da simulação. Verifique a
    documentação do método update() para uma descrição detalhada sobre como
    a física é resolvida em cada etapa de simulação.
    '''

    def __init__(self, gravity=None, damping=0, adamping=0,
                 restitution=1, friction=0, max_speed=None,
                 bounds=None, broad_phase=None, niter=5, beta=0.0):

        super(Simulation, self).__init__()

        # Listas de objetos e vínculos
        self._objects = []
        self._constraints = []
        self._contacts = []
        self._inactive = []

        # Parâmetros do solver
        self.niter = niter
        self.beta = beta

        # Define algortimos
        self.broad_phase = normalize_broad_phase(broad_phase, self)
        self.narrow_phase = NarrowPhase(world=self)

        # Inicia parâmetros físicos
        self._kinetic0 = None
        self._potential0 = None
        self._interaction0 = None
        self._gravity = null2D
        self._damping = self._adamping = self._friction = 0
        self._restitution = 1
        self.gravity = gravity or (0, 0)
        self.damping = damping
        self.adamping = adamping
        self.restitution = restitution
        self.friction = friction
        self.max_speed = max_speed

        # Limita mundo
        self.bounds = bounds
        self._out_of_bounds = set()

        # Inicializa constantes de simulação
        self.num_steps = 0
        self.time = 0

    ###########################################################################
    #                           Serviços Python
    ###########################################################################
    def __iter__(self):
        return iter(self._objects)

    def __contains__(self, obj):
        return obj in self._objects

    ###########################################################################
    #                               Sinais
    ###########################################################################
    frame_enter = signal('frame-enter')
    collision = signal('collision', num_args=1)
    object_add = signal('object-add', num_args=1)
    object_remove = signal('object-remove', num_args=1)
    gravity_change = signal('gravity-change', num_args=2)
    damping_change = signal('damping-change', num_args=2)
    adamping_change = signal('adamping-change', num_args=2)
    restitution_change = signal('restitution-change', num_args=2)
    friction_change = signal('friction-change', num_args=2)

    ###########################################################################
    #                       Propriedades físicas
    ###########################################################################
    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value):
        owns_prop = BodyFlags.owns_gravity
        old = self._gravity
        try:
            gravity = self._gravity = Vec2(*value)
        except TypeError:
            gravity = self._gravity = Vec2(0, -value)

        for obj in self._objects:
            if not obj.flags & owns_prop:
                obj._gravity = gravity
        self.trigger('gravity-change', old, self._gravity)

    @property
    def damping(self):
        return self._damping

    @damping.setter
    def damping(self, value):
        owns_prop = BodyFlags.owns_damping
        old = self._damping
        value = self._damping = float(value)

        for obj in self._objects:
            if not obj.flags & owns_prop:
                obj._damping = value
        self.trigger('damping-change', old, self._damping)

    @property
    def adamping(self):
        return self._adamping

    @adamping.setter
    def adamping(self, value):
        owns_prop = BodyFlags.owns_adamping
        old = self._adamping
        value = self._adamping = float(value)

        for obj in self._objects:
            if not obj.flags & owns_prop:
                obj._adamping = value
        self.trigger('adamping-change', old, self._damping)

    @property
    def restitution(self):
        return self._restitution

    @restitution.setter
    def restitution(self, value):
        owns_prop = BodyFlags.owns_restitution
        old = self._restitution
        value = self._restitution = float(value)

        for obj in self._objects:
            if not obj.flags & owns_prop:
                obj._restitution = value
        self.trigger('restitution-change', old, self._restitution)

    @property
    def friction(self):
        return self._friction

    @friction.setter
    def friction(self, value):
        owns_prop = BodyFlags.owns_friction
        old = self._friction
        value = self._friction = float(value)

        for obj in self._objects:
            if not obj.flags & owns_prop:
                obj._friction = value
        self.trigger('friction-change', old, self._friction)

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

        flags = BodyFlags

        if obj not in self._objects:
            self._objects.append(obj)
            obj._world = self

            oflags = obj.flags
            if not oflags & flags.owns_gravity:
                obj._gravity = self.gravity
            if not oflags & flags.owns_damping:
                obj._damping = self.damping
            if not oflags & flags.owns_adamping:
                obj._adamping = self.adamping
            if not oflags & flags.owns_restitution:
                obj._restitution = self.restitution
            if not oflags & flags.owns_friction:
                obj._friction = self.friction
            self.trigger('object-add', obj)

    def remove(self, obj):
        '''Remove um objeto da simulação. Produz um ValueError() caso o objeto
        não esteja presente na simulação.'''

        try:
            idx = self._objects.index(obj)
        except IndexError:
            raise ValueError('object not present')
        else:
            del self._objects[idx]
            self.trigger('object-remove', obj)
            obj.destroy()

    def discard(self, obj):
        '''Descarta um objeto da simulação.'''

        try:
            self.remove(obj)
        except ValueError:
            pass

    ###########################################################################
    #                     Simulação de Física
    ###########################################################################
    def update(self, dt):
        '''Rotina principal da simulação de física.'''

        self.trigger_frame_enter()
        self._dt = dt = float(dt)

        # Inicializa energia
        if self._kinetic0 is None:
            self._init_energy0()

        # Loop genérico
        self.accumulate_accelerations(dt)
        self.resolve_velocities(dt)
        self.resolve_constraints(dt)  # Colisão é um tipo de vínculo!
        self.resolve_positions(dt)

        # Incrementa tempo e contador
        self.time += dt
        self.num_steps += 1

        # Serviços esporáticos que não são realizados em todos os frames
        if self.num_steps % 2 == 0:
            self.find_out_of_bounds()
        elif self.num_steps % 2 == 1:
            self.enforce_max_speed()

    def accumulate_accelerations(self, dt):
        '''Atualiza o vetor interno que mede as acelerações lineares e
        angulares de cada objeto.

        Para tanto, usa informação tanto de forças globais quanto dos atributos
        *force* e *torque* de cada objeto.'''

        IS_SLEEP = BodyFlags.is_sleeping
        t = self.time

        # Acumula as forças e acelerações
        for obj in self._objects:
            if obj.flags & IS_SLEEP:
                continue

            if obj._invmass:
                obj.init_accel()
                if obj.force is not None:
                    obj._accel += obj.force(t) * obj._invmass

            # elif obj.flags & ACCEL_STATIC:
            #    obj.init_accel()
            #    obj.apply_accel(obj._accel, dt)

            if obj._invinertia:
                obj.init_alpha()
                if obj.torque is not None:
                    obj._alpha += obj.torque(t) * obj._invinertia

            # elif obj.flags & ALPHA_STATIC:
            #    obj.init_alpha()
            #    obj.apply_alpha(self._alpha, dt)

    def resolve_velocities(self, dt):
        '''Calcula as novas velocidades em função das acelerações acumuladas no
        passo accumulate_accelerations'''

        IS_SLEEP = BodyFlags.is_sleeping
        for obj in self._objects:
            if obj.flags & IS_SLEEP:
                continue

            if obj._invmass:
                obj.boost(obj._accel * dt)
            if obj._invinertia:
                obj.aboost(obj._alpha * dt)

            obj._e_vel = null2D
            obj._e_omega = 0.0

    def resolve_positions(self, dt):
        '''Resolve as posições a partir das velocidades'''

        IS_SLEEP = BodyFlags.is_sleeping
        for obj in self._objects:
            if obj.flags & IS_SLEEP:
                continue
            obj.move((obj.vel + obj._e_vel) * dt)
            obj.rotate((obj.omega + obj._e_omega) * dt)

    def resolve_constraints(self, dt):
        '''Resolve todos os vínculos utilizando o algoritmo de impulsos
        sequenciais'''

        broad_cols = self.broad_phase(self._objects)
        narrow_cols = self.narrow_phase(broad_cols)

        for col in narrow_cols:
            col.resolve()

        # Estabiliza contatos usando a estabilização de baumgarte
        #beta = self.beta
        # for col in narrow_cols:
        #    col.baumgarte_adjust(beta)

    def get_islands(self, contacts):
        '''Retorna a lista de grupos de colisão fechados no gráfico de
        colisões'''

        contacts = set(contacts)
        groups = defaultdict(list)
        while contacts:
            A, B = C = contacts.pop()
            gA = groups[A]
            gB = groups[B]
            if gA is not gB:
                gA.extend(gB)
                groups[B] = gA
            gA.append(C)
        return list(groups.values())

    def can_collide(self, A, B):
        '''Retorna True se A e B podem colidir'''

        flags = BodyFlags

        # Testa se os dois objetos são estáticos
        if ((not A._invmass or A.flags & flags.is_sleeping) and
                (not B._invmass or B.flags & flags.is_sleeping)):
            return False

        # Testa se estão na mesma camada de colisão
        elif ((A._col_layer_mask != B._col_layer_mask)
              and not (A._col_layer_mask & B._col_layer_mask)):
            return False

        # Testa se estão no mesmo grupo de colisão mesma camada de colisão
        elif A._col_group_mask & B._col_group_mask:
            return False

        return True

    #
    # Cálculo de parâmetros físicos
    #
    def energyK(self):
        '''Soma da energia cinética de todos os objetos do mundo'''

        return sum(obj.energyK() for obj in self._objects
                   if (obj._invmass or obj._invinertia))

    def energyU(self):
        '''Soma da energia potencial de todos os objetos do mundo devido à
        gravidade'''

        return sum(obj.energyU() for obj in self._objects if obj._invmass)

    def energy_interaction(self):
        '''Soma da energia de interação entre todos os pares de partículas
        (Não implementado)'''

        return 0.0

    def energyT(self):
        '''Energia total do sistema de partículas (possivelmente excluindo
        algumas interações entre partículas)'''

        return self.energyU() + self.energyK() + self.energy_interaction()

    def energy_ratio(self):
        '''Retorna a razão entre a energia total e a energia inicial calculada
        no início da simulação'''

        if self._kinetic0 is None:
            self._init_energy0()
            return 1.0
        sum_energies = self._kinetic0 + self._potential0 + self._interaction0
        return self.energyT() / sum_energies

    def _init_energy0(self):
        '''Chamada para inicializar _kinetic0 e amigos'''

        self._kinetic0 = self.energyK()
        self._potential0 = self.energyU()
        self._interaction0 = self.energy_interaction()

    #
    # Serviços esporáticos
    #
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


###############################################################################
#                              Funções auxiliares
###############################################################################
def normalize_broad_phase(broad_phase, world):
    '''Escolhe o parâmetro correto na inicialização do broad-phase'''

    if broad_phase is None:
        broad_phase = BroadPhaseCBB(world=world)
    elif isinstance(broad_phase, BroadPhase):
        if broad_phase.world not in [None, world]:
            raise ValueError('BroadPhase object has a world attatched')
        else:
            broad_phase.world = world
    elif isinstance(broad_phase, type) and issubclass(broad_phase, BroadPhase):
        broad_phase = broad_phase(world=world)
    else:
        raise TypeError('invalid broad phase object')
    return broad_phase

if __name__ == '__main__':
    import doctest
    doctest.testmod()
