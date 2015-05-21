# -*- coding: utf8 -*-

from FGAme.mathutils import Vec2
from FGAme.physics.flags import BodyFlags
from FGAme.core import EventDispatcher, signal
from FGAme.physics.broadphase import BroadPhase, BroadPhaseCBB, NarrowPhase
from FGAme.draw import Color

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
                 restitution=1, sfriction=0, dfriction=0, max_speed=None,
                 bounds=None, broad_phase=None):

        super(Simulation, self).__init__()
        self._objects = []
        self._constraints = []
        self._contacts = []

        self.broad_phase = normalize_broad_phase(broad_phase)
        self.narrow_phase = NarrowPhase(world=self)
        self._kinetic0 = None
        self._potential0 = None
        self._interaction0 = None

        # Inicia a gravidade e as constantes de força dissipativa
        self.gravity = gravity or (0, 0)
        self.damping = damping
        self.adamping = adamping

        # Colisão
        self.restitution = float(restitution)
        self.sfriction = float(sfriction)
        self.dfriction = float(dfriction)
        self.max_speed = max_speed

        # Limita mundo
        self.bounds = bounds
        self._out_of_bounds = set()

        # Inicializa constantes de simulação
        self._dt = 0.0
        self.num_steps = 0
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
    object_add = signal('object-add', num_args=1)
    object_remove = signal('object-remove', num_args=1)
    gravity_change = signal('gravity-change', num_args=2)
    damping_change = signal('damping-change', num_args=2)
    adamping_change = signal('adamping-change', num_args=2)

    ###########################################################################
    #                             Propriedades
    ###########################################################################

    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value):
        old = getattr(self, '_gravity', Vec2(0, 0))
        try:
            gravity = self._gravity = Vec2(*value)
        except TypeError:
            gravity = self._gravity = Vec2(0, -value)

        for obj in self:
            if not obj.owns_gravity:
                obj._gravity = gravity
        self.trigger('gravity-change', old, self._gravity)

    @property
    def damping(self):
        return self._damping

    @damping.setter
    def damping(self, value):
        old = getattr(self, '_damping', 0)
        value = self._damping = float(value)

        for obj in self._objects:
            if not obj.owns_damping:
                obj._damping = value
        self.trigger('damping-change', old, self._damping)

    @property
    def adamping(self):
        return self._adamping

    @adamping.setter
    def adamping(self, value):
        old = getattr(self, '_damping', 0)
        value = self._adamping = float(value)

        for obj in self._objects:
            if not obj.owns_adamping:
                obj._adamping = value
        self.trigger('damping-change', old, self._damping)

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
        self._dt = float(dt)

        # Inicializa energia
        if self._kinetic0 is None:
            self._init_energy0()

        # Loop genérico
        self.accumulate_accelerations()
        self.resolve_velocities()
        self.resolve_constraints()  # Colisão é um tipo de vínculo!
        self.resolve_positions()

        # Incrementa tempo e contador
        self.time += self._dt
        self.num_steps += 1

        # Serviços esporáticos que não são realizados em todos os frames
        if self.num_steps % 2 == 0:
            self.find_out_of_bounds()
        elif self.num_steps % 2 == 1:
            self.enforce_max_speed()

    def accumulate_accelerations(self):
        '''Atualiza o vetor interno que mede as acelerações lineares e
        angulares de cada objeto.

        Para tanto, usa informação tanto de forças globais quanto dos atributos
        *force* e *torque* de cada objeto.'''

        t = self.time
        dt = self._dt

        # Acumula as forças e acelerações
        for obj in self._objects:
            if obj.is_sleep:
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

    def resolve_velocities(self):
        '''Calcula as novas velocidades em função das acelerações acumuladas no
        passo accumulate_accelerations'''

        dt = self._dt
        for obj in self._objects:
            if obj.is_sleep:
                continue
            if obj._invmass:
                obj.boost(obj.accel * dt)
            if obj._invinertia:
                obj.aboost(obj.alpha * dt)

            obj._e_vel = Vec2(0, 0)
            obj._e_omega = 0.0

    def resolve_positions(self):
        '''Resolve as posições a partir das velocidades'''

        dt = self._dt
        for obj in self._objects:
            if obj.is_sleep:
                continue
            obj.move((obj.vel + obj._e_vel) * dt)
            obj.rotate((obj.omega + obj._e_omega) * dt)

    def resolve_constraints(self):
        '''pass'''

        # Colisões
        broad_cols = self.broad_phase(self._objects)
        narrow_cols = self.narrow_phase(broad_cols)
        self.resolve_collisions(narrow_cols)
        objs = sorted(narrow_cols.objects(), key=lambda obj: obj.xmin)
        for _ in range(2):
            broad_cols = self.broad_phase(objs)
            narrow_cols = self.narrow_phase(broad_cols)
            self.resolve_collisions(narrow_cols)

    def resolve_collisions(self, collisions):
        '''Resolve as colisões'''

        for col in collisions:
            A, B = col.objects
            A.trigger('collision', col)
            B.trigger('collision', col)
            if col.is_active:
                col.resolve()

                continue
                A_static = A.is_static() or A.is_sleep
                B_static = B.is_static() or B.is_sleep

                if A_static or A_static:
                    if B_static and not A.is_static():
                        if (A.vel.norm() <= SLEEP_LINEAR_VELOCITY and
                                abs(A.omega) <= SLEEP_ANGULAR_VELOCITY):
                            A.is_sleep = True
                            A.vel *= 0
                        else:
                            A.is_sleep = False

                    if A_static and not B.is_static():
                        if (B.vel.norm() <= SLEEP_LINEAR_VELOCITY and
                                abs(B.omega) <= SLEEP_ANGULAR_VELOCITY):
                            B.vel *= 0
                            B.is_sleep = True
                        else:
                            B.is_sleep = False

    # Cálculo de parâmetros físicos ###########################################
    def kineticE(self):
        '''Soma da energia cinética de todos os objetos do mundo'''

        return sum(obj.kineticE() for obj in self._objects
                   if (obj._invmass or obj._invinertia))

    def potentialE(self):
        '''Soma da energia potencial de todos os objetos do mundo devido à
        gravidade'''

        return sum(obj.potentialE() for obj in self._objects if obj._invmass)

    def interactionE(self):
        '''Soma da energia de interação entre todos os pares de partículas
        (Não implementado)'''

        return 0.0

    def totalE(self):
        '''Energia total do sistema de partículas (possivelmente excluindo
        algumas interações entre partículas)'''

        return self.potentialE() + self.kineticE() + self.interactionE()

    def energy_ratio(self):
        '''Retorna a razão entre a energia total e a energia inicial calculada
        no início da simulação'''

        if self._kinetic0 is None:
            self._init_energy0()
            return 1.0
        sum_energies = self._kinetic0 + self._potential0 + self._interaction0
        return self.totalE() / sum_energies

    def _init_energy0(self):
        '''Chamada para inicializar _kinetic0 e amigos'''

        self._kinetic0 = self.kineticE()
        self._potential0 = self.potentialE()
        self._interaction0 = self.interactionE()

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


###############################################################################
#                              Funções auxiliares
###############################################################################
def normalize_broad_phase(broad_phase):
    '''Escolhe o parâmetro correto na inicialização do broad-phase'''

    if broad_phase is None:
        broad_phase = BroadPhaseCBB()
    elif isinstance(broad_phase, BroadPhase):
        pass
    elif isinstance(broad_phase, type) and issubclass(broad_phase, BroadPhase):
        broad_phase = broad_phase()
    else:
        raise TypeError('invalid broad phase')
    return broad_phase

if __name__ == '__main__':
    import doctest
    doctest.testmod()
