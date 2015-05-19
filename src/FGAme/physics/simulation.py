# -*- coding: utf8 -*-

from FGAme.mathutils import Vec2
from FGAme.physics import get_collision, get_collision_generic, CollisionError
from FGAme.physics import flags
from FGAme.core import EventDispatcher, signal
from FGAme.physics.broadphase import BroadPhase, BroadPhaseCBB
from FGAme.draw import Color

###############################################################################
#                                Simulação
# ----------------------------------------------------------------------------
# Coordena todos os objetos com uma física definida e resolve a interação
# entre eles
###############################################################################
SLEEP_LINEAR_VELOCITY = 12
SLEEP_ANGULAR_VELOCITY = 0.1


class Simulation(EventDispatcher):

    '''Implementa a simulação de física.

    Os métodos principais são: add(obj) e remove(obj) para adicionar e remover
    objetos e update(dt) para atualizar o estado da simulação. Verifique a
    documentação do método update() para uma descrição detalhada sobre como
    a física é resolvida em cada etapa de simulação.
    '''

    def __init__(self, gravity=None, damping=0, adamping=0,
                 rest_coeff=1, sfriction=0, dfriction=0, max_speed=None,
                 bounds=None, broad_phase=None):

        super(Simulation, self).__init__()
        self._objects = []
        self._broad_phase = normalize_broad_phase(broad_phase)
        self._fine_collisions = []
        self._kinetic0 = None
        self._potential0 = None
        self._interaction0 = None

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

        self._broad_phase.update(self._objects)

    def fine_phase(self):
        '''Escaneia a lista de colisões grosseiras e detecta quais delas
        realmente aconteceram'''

        # Detecta colisões e atualiza as listas internas de colisões de
        # cada objeto
        self._fine_collisions[:] = []

        for A, B in self._broad_phase:
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
            if obj.is_sleep:
                continue

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
            if obj.is_sleep:
                continue

            if obj._invmass:
                obj.update_linear(dt)
            elif obj._vel.x or obj._vel.y:
                obj.move(obj._vel * dt)

            if obj._invinertia:
                obj.update_angular(dt)
            elif obj.omega:
                obj.rotate(obj.omega * dt)

    def resolve_collisions(self):
        '''Resolve as colisões'''

        for col in self._fine_collisions:
            A, B = col.objects
            A.trigger('collision', col)
            B.trigger('collision', col)
            if col.is_active:
                col.resolve()

                if (A.is_static() or B.is_static()):
                    if B.is_static():
                        if (A.vel.norm() <= SLEEP_LINEAR_VELOCITY and
                                abs(A.omega) <= SLEEP_ANGULAR_VELOCITY):
                            A.is_sleep = True
                            A._color = Color(100, 100, 100)
                        else:
                            A.is_sleep = False
                            A._color = Color(0, 0, 0)

                    if A.is_static():
                        if (B.vel.norm() <= SLEEP_LINEAR_VELOCITY and
                                abs(B.omega) <= SLEEP_ANGULAR_VELOCITY):
                            B.is_sleep = True
                            B._color = Color(100, 100, 100)
                        else:
                            B.is_sleep = False
                            B._color = Color(0, 0, 0)

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
