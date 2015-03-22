#-*- coding: utf8 -*-
from FGAme.mathutils import Vector, shadow_y
from FGAme.physics import get_collision, get_collision_aabb, CollisionError
from FGAme.core import EventDispatcher, signal, init
from FGAme.core import env

#=========================================================================
# Classe Mundo -- coordena todos os objetos com uma física definida e resolve a
# interação entre eles
#=========================================================================


class Simulation(EventDispatcher):

    '''Implementa a simulação de física.

    Os métodos principais são: add(obj) e remove(obj) para adicionar e remover
    objetos e update(dt) para atualizar o estado da simulação. Verifique a
    documentação do método update() para uma descrição detalhada sobre como
    a física é resolvida em cada etapa de simulação.
    '''

    def __init__(self, gravity=None, damping=0, adamping=0,
                 rest_coeff=1, sfriction=0, dfriction=0, stop_velocity=1e-6):

        self._objects = []

        # Inicia a gravidade e as constantes de força dissipativa
        self.gravity = gravity or (0, 0)
        self.damping = damping
        self.adamping = adamping

        # Colisão
        self.rest_coeff = float(rest_coeff)
        self.sfriction = float(sfriction)
        self.dfriction = float(dfriction)
        self.stop_velocity = float(stop_velocity)
        self.time = 0

        # Controle de callbacks
        init()
        self.input = env.input_object
        super(Simulation, self).__init__()

    #=========================================================================
    # Propriedades
    #=========================================================================

    #
    # Vetor com a aceleração da gravidade (em px/s^2)
    #
    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value):
        try:
            gravity = self._gravity = Vector(*value)
        except TypeError:
            gravity = self._gravity = Vector(0, -value)

        for obj in self._objects:
            if not obj.owns_gravity:
                obj._gravity = gravity

    #
    # Constante de amortecimento para a aceleração linear
    #
    @property
    def damping(self):
        return self._damping

    @damping.setter
    def damping(self, value):
        value = self._damping = float(value)

        for obj in self._objects:
            if not obj.owns_damping:
                obj._damping = value

    #
    # Constante de amortecimento para a aceleração angular
    #
    @property
    def adamping(self):
        return self._adamping

    @adamping.setter
    def adamping(self, value):
        value = self._adamping = float(value)

        for obj in self._objects:
            if not obj.owns_adamping:
                obj._adamping = value

    #=========================================================================
    # Gerenciamento de objetos
    #=========================================================================
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
            self._objects.sort()
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

    #=========================================================================
    # Controle de eventos
    #=========================================================================
    # Delegações
    long_press = signal('long-press', 'key', delegate='input')
    key_up = signal('key-up', 'key', delegate='input')
    key_down = signal('key-down', 'key', delegate='input')
    mouse_motion = signal('mouse-motion', delegate='input')
    mouse_click = signal('mouse-click', 'button', delegate='input')

    # Eventos privados
    frame_enter = signal('frame-enter')
    collision = signal('collision', num_args=1)
    # TODO: collision_pair = signal('collision-pair', 'obj1', 'obj2',
    # num_args=1)

    #=========================================================================
    # Simulação de Física
    #=========================================================================
    def update(self, dt):
        '''Rotina principal da simulação de física.'''

        self.trigger('frame-enter')
        self.resolve_forces(dt)
        self.pre_update(dt)
        collisions = self.detect_collisions(dt)
        self.resolve_collisions(collisions, dt)
        self.post_update(dt)
        self.time += dt
        return self.time

    def pre_update(self, dt):
        '''Executa a rotina de pré-atualização em todos os objetos.

        A fase de pré-atualização é executada no início de cada frame antes da
        atualização da física. Nesta fase objetos podem atualizar o estado
        interno ou realizar qualquer tipo de modificação antes do cálculo das
        forças e colisões.
        '''

        # Chama a pre-atualização de cada objeto
        t = self.time
        for obj in self._objects:
            # obj.pre_update(t, dt)
            # obj.is_colliding = False
            pass

    def post_update(self, dt):
        '''Executa a rotina de pós-atualização em todos os objetos.

        Este passo é executado em cada frame após resolver a dinâmica de
        forças e colisões.'''

        t = self.time
        for obj in self._objects:
            # obj.post_update(t, dt)
            pass

    def detect_collisions(self, dt):
        '''Retorna uma lista com todas as colisões atuais.

        Uma colisão é caracterizada por um objeto da classe Collision() ou
        subclasse.'''

        objects = sorted(self._objects)
        collisions = []
        objects.sort()

        # Os objetos estão ordenados. Este loop detecta as colisões AABB e,
        # caso elas aconteçam, delega a tarefa de detecção fina de colisão para
        # a função get_collision
        for i, A in enumerate(objects):
            xmax = A._xmax
            A_static = bool(A._invinertia == A._invmass)

            for j in range(i + 1, len(objects)):
                B = objects[j]

                # Procura na lista enquanto xmin de B for menor que xmax de A
                if B._xmin > xmax:
                    break

                # Não detecta colisão entre dois objetos estáticos/cinemáticos
                if A_static and (B._invmass == B._invinertia == 0):
                    continue

                # Somente testa as colisões positivas por AABB
                if shadow_y(A, B) < 0:
                    continue

                # Detecta colisões e atualiza as listas internas de colisões de
                # cada objeto
                col = self.get_collision(A, B)
                if col is not None:
                    col.world = self
                    collisions.append(col)
                    print('colliding')
                    # A.trigger('collision', col)
                    # B.trigger('collision', col)
        return collisions

    def resolve_collisions(self, collisions, dt):
        '''Resolve todas as colisões na lista collisions'''

        for col in collisions:
            col.resolve(dt)

    def resolve_forces(self, dt):
        '''Resolve a dinâmica de forças durante o intervalo dt'''

        t = self.time

        # Acumula as forças e acelerações
        for obj in self._objects:
            if obj._invmass:
                obj.init_accel()
                #F += obj.external_force(t) or (0, 0)
            elif obj.flag_accel_static:
                obj.init_accel()
                obj.apply_accel(obj._accel)

            if obj._invinertia:
                tau = obj.global_torque()
                tau += obj.external_torque(t) or 0
                self._frame_tau = tau
            elif obj.flag_accel_static:
                a = obj._init_frame_alpha()
                obj.apply_alpha(a)

        # Applica as forças e acelerações
        for obj in self._objects:
            if obj._invmass:
                obj.apply_accel(obj._accel, dt)
            elif obj._vel.x or obj._vel.y:
                obj.move(obj._vel * dt)

            if obj._invinertia:
                obj.apply_torque(obj._frame_tau, dt)
            elif obj._omega:
                obj.rotate(obj._omega * dt)

    def get_collision(self, A, B):
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
            get_collision[type(A), type(B)] = get_collision_aabb
            get_collision[type(B), type(A)] = get_collision_aabb
            return get_collision_aabb(A, B)
        else:
            def inverse(A, B):
                '''Automatically created collision for A, B from the supported
                collision B, A'''
                col = direct(B, A)
                if col is not None:
                    return col.swapped()

            direct = get_collision[type(B), type(A)]
            get_collision[type(A), type(B)] = inverse
            return col

    #=========================================================================
    # Cálculo de parâmetros físicos
    #=========================================================================
    def kinetic_energy(self):
        '''Retorna a soma da energia cinética de todos os objetos do mundo'''

        return sum(obj.kinetic() for obj in self.objects)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
