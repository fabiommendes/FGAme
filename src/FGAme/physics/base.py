#-*- coding: utf8 -*-
'''

Modificando o estado físico do objeto
-------------------------------------

.. autoclass :: FGAme.Object
    :members:
    :member-order: bysource
    
.. autoclass :: FGAme.LinearObject

'''

from copy import copy
from FGAme.core import EventDispatcher, signal
from FGAme.draw import RectEcho, RenderTree, Color
from FGAme.mathutils import Vector, VectorM, asvector
from FGAme.util import lazy

PAUSE_SPEED = 5
PAUSE_W_SPEED = 0.05

#===============================================================================
# Objetos de colisão -- define a interface básica para a colisão entre 2 objetos
# Todos os outros objetos devem derivar de PhysicsObject. As colisões entre pares
# de objetos são implementadas por multidispatch a partir das funções
# get_collision, avoid_superposition e adjust_superposition no módulo collisions
#===============================================================================
class Object(EventDispatcher):
    '''Classe pai para todos os objetos físicos da FGAme.
    
    Attributes
    ----------

    :: 
        **Propriedades físicas do objeto**
    mass
        Massa do objeto. Por padrão é calculada como se a densidade fosse 1.
        Uma massa infinita transforma o objeto num objeto cinemático que não
        responde a forças lineares.
    inertia
        Momento de inércia do objeto com relação ao eixo z no centro de massa.
        Calculado automaticamente a partir da geometria e densidade do objeto.
        Caso seja infinito, o objeto não responderá a torques.
    ROG, ROG_sqr
        Raio de giração e o quadrado do raio de giração. Utilizado para calcular
        o momento de inércia: $I = M R^2$, onde I é o momento de inércia, M a 
        massa e R o raio de giração.
    density
        Densidade de massa: massa / área
    area
        Área que o objeto ocupa

    :: 
        **Variáveis dinâmicas**
    pos
        Posição do centro de massa do objeto
    vel
        Velocidade linear medida a partir do centro de massa
    theta
        Ângulo da rotação em torno do eixo saindo do centro de massa do objeto
    omega
        Velocidade angular de rotação
    
    :: 
        **Caixa de contorno**
    xmin, xmax, ymin, ymax 
        Limites da caixa de contorno alinhada aos eixos que envolve o objeto
    bbox
        Uma tupla com (xmin, xmax, ymin, ymax)
    shape
        Uma tupla (Lx, Ly) com a forma caixa de contorno nos eixos x e y.
    rect
        Uma tupla com (xmin, ymin, Lx, Ly)
        
    :: 
        **Forças globais**
    
    gravity
        Valor da aceleração da gravidade aplicada ao objeto
    damping, adamping
        Constantes de amortecimento linear e angulor para forças viscosas 
        aplicadas ao objeto
    owns_gravity, owns_damping, owns_adamping
        Se Falso (padrão) utiliza os valores de gravity, damping e adamping
        fornecidos pelo mundo 
    accel_static
        Caso verdadeiro, aplica as acelerações de gravidade, damping e adamping
        no objeto mesmo se ele for estático
    '''
    def __init__(self, pos=None, vel=None,
                       theta=None, omega=None,
                       mass=None, density=None, inertia=None,
                       color=None, name=None,
                       damping=None, adamping=None, gravity=None, accel_static=False,
                       world=None):

        # Variáveis dinâmicas
        self._pos = VectorM(*(pos or (0, 0)))
        self._vel = VectorM(*(vel or (0, 0)))
        self._accel = VectorM(0, 0)
        self._omega = float(omega or 0)
        self._theta = 0.0
        if theta is not None:
            self.rotate(theta)

        # Propriedades de inércia
        self._density = density or 1.0
        if mass is not None:
            self.mass = mass
        else:
            self.mass  # computa massa a partir da densidade 1.0
        if inertia is not None:
            self.inertia = inertia
        else:
            self.inertia  # computa inércia a partir da densidade 1.0

        # Forças globais
        self._damping = 0.0
        self._adamping = 0.0
        self._gravity = Vector(0, 0)
        if damping:
            self.owns_damping = True
            self._damping = damping
        if adamping:
            self.owns_adamping = True
            self._adamping = adamping
        if gravity:
            self.owns_gravity = True
            self._gravity = Vector(*gravity)
        self._frame_force = VectorM(0, 0)
        self._frame_accel = VectorM(0, 0)
        self._frame_tau = 0
        self._frame_alpha = 0
        self.accel_static = accel_static

        # Cor/desenho
        self._art_object = self.get_primitive_drawable(color=color) 
        self.drawable = RenderTree()
        self.drawable.add(self._art_object)

        # Adiciona ao mundo
        self.name = name
        if world is not None:
            world.add(self)
        self.world = world

        # Inicializa listeners
        super(Object, self).__init__()

    #===========================================================================
    #: Propriedades e constantes físicas
    #===========================================================================
    has_physics = True
    
    #---------------------------------------------------------------------------
    # Propriedades da caixa de contorno AABB

    @property
    def xmin(self): return self._xmin

    @property
    def xmax(self): return self._xmax

    @property
    def ymin(self): return self._ymin

    @property
    def ymax(self): return self._ymax

    @property
    def bbox(self):
        return (self._xmin, self._xmax, self._ymin, self._ymax)

    @property
    def shape(self):
        return (self._xmax - self._xmin, self._ymax - self._ymin)

    @property
    def rect(self):
        x, y = self._xmin, self._ymin
        return (x, y, self._xmax - x, self._ymax - y)

    #---------------------------------------------------------------------------
    # Parâmetros físicos
    @property
    def mass(self):
        try:
            return self._mass
        except AttributeError:
            self.mass = self._density * self.area
            return self._mass

    @mass.setter
    def mass(self, value):
        value = float(value)
        self._density = value / self.area
        self._mass = value
        self._invmass = 1.0 / value

    @property
    def inertia(self):
        try:
            return self._inertia
        except AttributeError:
            self.inertia = self._mass * self.ROG_sqr
            return self._inertia

    @inertia.setter
    def inertia(self, value):
        value = float(value)
        self._inertia = value
        self._invinertia = 1.0 / value

    @lazy
    def area(self):
        return (self._xmax - self._xmin) * (self._ymax - self._ymin)

    @lazy
    def ROG_sqr(self):
        a, b = self.shape
        return (a ** 2 + b ** 2) / 12

    @property
    def ROG(self):
        return sqrt(self.ROG_sqr)

    @property
    def density(self):
        return self._density

    #---------------------------------------------------------------------------
    # Variáveis de estado
    @property
    def pos(self):
        return Vector(*self._pos)

    @pos.setter
    def pos(self, value):
        self.set_pos(value)

    @property
    def vel(self):
        return Vector(*self._vel)

    @vel.setter
    def vel(self, value):
        self.set_vel(value)

    @property
    def theta(self):
        return self._theta

    @theta.setter
    def theta(self, value):
        self.set_theta(value)

    @property
    def omega(self):
        return self._omega

    @omega.setter
    def omega(self, value):
        self.set_omega(value)

    #---------------------------------------------------------------------------
    # Parâmetros físicos derivados
    @property
    def linearE(self):
        return self._mass * dot(self.vel, self.vel) / 2

    @property
    def angularE(self):
        return self._inertia * self.omega ** 2 / 2

    @property
    def kineticE(self):
        return self.linearE + self.angularE

    @property
    def momentumP(self):
        return self.mass * self.vel

    @property
    def momentumL(self):
        return self.inertia * self.omega

    #---------------------------------------------------------------------------
    # Parâmetros que modificam a resposta física de um objeto às forças externas
    # e colisões
    is_alive = is_internal = is_paused = False
    owns_gravity = owns_damping = owns_adamping = False

    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value):
        self._gravity = Vector(*value)
        self.owns_gravity = True

    @property
    def damping(self):
        return self._damping

    @damping.setter
    def damping(self, value):
        self._damping = float(value)
        self.owns_damping = True

    @property
    def adamping(self):
        return self._adamping

    @adamping.setter
    def adamping(self, value):
        self._adamping = float(value)
        self.owns_adamping = True

    @property
    def color(self):
        try:
            return self._art_object._color
        except AttributeError:
            return None

    @color.setter
    def color(self, value):
        self._art_object._color = Color(value)

    #===========================================================================
    # Deslocamentos
    #===========================================================================
    def set_pos(self, pos=None):
        '''Reposiciona o centro de massa do objeto nas coordenadas especificadas 
        ou na origem.'''

        if pos is None:
            self.move(-self._pos)
        else:
            self.move(asvector(pos) - self._pos)

    def set_vel(self, vel=None):
        '''Redefine a velocidade linear do centro de massa para o valor 
        especificado (ou para zero, em caso de omissão).'''

        if vel is None:
            self.boost(-self._vel)
        else:
            self.boost(vel - self._vel)

    def set_theta(self, theta=None):
        '''Reorienta o objeto para o ângulo fornecido ou para a orientação 
        inicial.'''

        if theta is None:
            self.rotate(-self._theta)
        else:
            self.rotate(theta - self._theta)

    def set_omega(self, omega=None):
        '''Redefine a velocidade angular do centro de massa para o valor 
        especificado (ou para zero, em caso de omissão).'''

        if omega is None:
            self.aboost(-self._omega)
        else:
            self.aboost(omega - self._omega)

    def move(self, delta):
        '''Move o objeto por vetor de deslocamento delta'''

        x, y = delta
        self._pos += delta
        self._xmin += x
        self._xmax += x
        self._ymin += y
        self._ymax += y

    def boost(self, delta):
        '''Adiciona um valor vetorial delta à velocidade linear'''

        self._vel += delta

    def rotate(self, theta):
        '''Rotaciona o objeto por um ângulo theta'''

        self._theta += theta

    def aboost(self, delta):
        '''Adiciona um valor delta à velocidade ângular'''

        self._omega += delta

    def vpoint(self, pos, relative=False):
        '''Retorna a velocidade linear de um ponto em pos preso rigidamente ao 
        objeto.
        
        Se o parâmetro `relative` for verdadeiro, o vetor `pos` é interpretado
        como a posição relativa ao centro de massa. O padrão é considerá-lo
        como a posição absoluta no centro de coordenadas do mundo.'''

        x, y = pos - self._pos
        return self._vel + self._omega * Vector(-y, x)

    #===========================================================================
    # Resposta a forças, impulsos e atualização da física
    #===========================================================================
    def global_force(self):
        return self._mass * (self._gravity - self._damping * self._vel)

    def global_torque(self):
        return -self._inertia * self._omega * self._adamping

    def global_accel(self):
        return self._gravity - self._damping * self._vel

    def global_alpha(self):
        return -self._omega * self._adamping

    def _init_frame_force(self):
        # Troca aceleração por força
        try:
            F = self._frame_force
            A = self._frame_accel
            self._frame_accel = F

            # Executa e multiplica pela massa
            self._init_frame_accel()
            F *= self._mass
        finally:
            # Reverte atributos
            self._frame_force = F
            self._frame_accel = A
        return self._frame_force

    def _init_frame_accel(self):
        F = self._frame_accel
        if self._damping:
            F.copy_from(self._vel)
            F *= -self._damping
            if self._gravity is not None:
                F += self._gravity
        elif self._gravity is not None:
            F.copy_from(self._gravity)
        else:
            F *= 0
        return self._frame_accel

    def _init_frame_tau(self):
        self._frame_tau = -self._inertia * self._omega * self._adamping

    def _init_frame_alpha(self):
        self._frame_alpha = -self._omega * self._adamping

    def external_force(self, t):
        '''Define uma força externa que depende do tempo t.
        
        Pode ser utilizado por sub-implementações para definir uma força externa
        aplicada aos objetos de uma sub-classe ou usando o recurso de "duck typing"
        do Python
        
        >>> c = Circle(10)
        >>> c.external_force = lambda t: -c.pos.x  
        '''

        return None

    def external_torque(self, t):
        '''Define uma torque externo análogo ao método .external_force()'''

        return None

    def apply_force(self, force, dt):
        '''Aplica uma força linear durante um intervalo de tempo dt'''

        self.apply_accel(force * self._invmass, dt)

    def apply_accel(self, a, dt):
        '''Aplica uma aceleração linear durante um intervalo de tempo dt.
        
        Tem efeito em objetos cinemáticos.
        
        Observations
        ------------
        
        Implementa a integração de Velocity-Verlet para o sistema. Este
        integrador é superior ao Euler por dois motivos: primeiro, trata-se de
        um integrador de ordem superior (O(dt^4) vs O(dt^2)). Além disto, ele possui a
        propriedade simplética, o que implica que o erro da energia não tende a
        divergir, mas sim oscilar ora positivamente ora negativamente em torno
        de zero. Isto é extremamente desejável para simulações de física que
        parecam realistas.
        
        A integração de Euler seria implementada como:
        
            x(t + dt) = x(t) + v(t) * dt + a(t) * dt**2 / 2
            v(t + dt) = v(t) + a(t) * dt
        
        Em código Python
        
        >>> self.move(self.vel * dt + a * (dt**2/2))
        >>> self.boost(a * dt)
        
        Este método simples e intuitivo sofre com o efeito da "deriva de
        energia". Devido aos erros de truncamento, o valor da energia da solução
        numérica flutua com relação ao valor exato. Na grande maioria dos
        sistemas, esssa flutuação ocorre com mais probabilidade para a região de
        maior energia e portanto a energia tende a crescer continuamente,
        estragando a credibilidade da simulação.
        
        Velocity-Verlet está numa classe de métodos numéricos que não sofrem com
        esse problema. A principal desvantagem, no entanto, é que devemos manter
        uma variável adicional com o último valor conhecido da aceleração. Esta
        pequena complicação é mais que compensada pelo ganho em precisão
        numérica. O algorítmo consiste em:
        
            x(t + dt) = x(t) + v(t) * dt + a(t) * dt**2 / 2
            v(t + dt) = v(t) + [(a(t) + a(t + dt)) / 2] * dt 

        O termo a(t + dt) normalemente só pode ser calculado se soubermos como
        obter as acelerações como função das posições x(t + dt). Na prática,
        cada iteração de .apply_accel() calcula o valor da posição em  x(t + dt)
        e da velocidade no passo anterior v(t). Calcular v(t + dt) requer uma
        avaliação de a(t + dt), que só estará disponível na iteração seguinte.
        A próxima iteração segue então para calcular v(t + dt) e x(t + 2*dt), e
        assim sucessivamente.
        
        A ordem de acurácia de cada passo do algoritmo Velocity-Verlet é de
        O(dt^4) para uma força que dependa exclusivamente da posição e tempo.
        Caso haja dependência na velocidade, a acurácia reduz e ficaríamos
        sujeitos aos efeitos da deriva de energia. Normalmente as forças físicas
        que dependem da velocidade são dissipativas e tendem a reduzir a energia
        total do sistema muito mais rapidamente que a deriva de energia tende a
        fornecer energia espúria ao sistema. Deste modo, a acurácia ficaria
        reduzida, mas a simulação ainda manteria alguma credibilidade.
        '''

        self._accel += a
        self._accel /= 2
        self.boost(self._accel * dt)
        self.move(self._vel * dt + a * (dt ** 2 / 2.))
        self._accel.copy_from(a)

    def apply_torque(self, torque, dt):
        '''Aplica um torque durante um intervalo de tempo dt.'''

        self.apply_alpha(torque * self._invinertia, dt)

    def apply_alpha(self, alpha, dt):
        '''Aplica uma aceleração angular durante um intervalo de tempo dt.
        
        Tem efeito em objetos cinemáticos.'''

        dt = dt / 2
        self.aboost(alpha * dt)
        self.rotate(self._omega * dt + alpha * dt ** 2 / 2.)

    def apply_impulse(self, impulse, pos=None, relative=False):
        '''Aplica um impulso linear ao objeto. Isto altera sua velocidade 
        linear com relação ao centro de massa.
        
        Se for chamado com dois agumentos aplica o impulso em um ponto específico
        e também resolve a dinâmica angular.
        '''

        self.boost(impulse / self.mass)

    def apply_aimpulse(self, itorque):
        '''Aplica um impulso angular ao objeto.'''

        self.aboost(itorque / self.inertia)

    def update(self, dt, time=0):
        '''Atualiza o estado do objeto.
        
        Essa função *não* é chamada pelo mundo, mas apenas define uma interface
        uniforme para que objetos isolados possam ser simulados.
        '''

        self.pre_update(dt)
        if self.is_dynamic_linear:
            self.apply_force(self.external_force(time), dt)
        if self.is_dynamic_angular:
            self.apply_torque(self.external_torque(time), dt)
        self.post_update(dt)

    def rescale(self, scale, update_physics=True):
        '''Modifica o tamanho do objeto pelo fator de escala fornecido. 
        O objeto se mantêm centrado no centro de massa após a operaçao de
        escala.'''

        xcm, ycm = self.pos
        deltax, deltay = self.shape
        deltax, deltay = scale * deltax / 2, scale * deltay / 2
        self.xmin = xcm - deltax
        self.xmax = xcm + deltax
        self.ymin = ycm - deltay
        self.ymax = ycm + deltay

        if update_physics:
            self.rescale_physics(scale)

    def rescale_physics(self, scale):
        '''Modifica o valor da massa e do momento de inércia de acordo com
        o fator de escala fornecido'''

        self.mass *= scale ** 2
        self.inertia *= scale ** 4

    #===========================================================================
    # Controle de estado dinâmico
    #===========================================================================
    def pause(self):
        '''Pausa a dinâmica do objeto'''

        if not self.is_paused:
            self.is_paused = True
            self.can_move_linear = False
            self.can_move_angular = False
            self.can_move = False

    def unpause(self):
        '''Retira a pausa de um objeto'''

        self.is_paused = False
        self.can_move_linear = self.is_dynamic_linear
        self.can_move_angular = self.is_dynamic_angular
        self.can_move = self.is_dynamic_linear or self.is_dynamic_angular

        try:
            self.color = self._old_color
        except AttributeError:
            pass

    def is_still(self):
        '''Retorna verdadeiro se o objeto estiver parado ou se movendo muito 
        lentamente'''

        if not self.can_move:
            return True
        else:
            return (self.vel.norm() < PAUSE_SPEED and
                    self.omega < PAUSE_W_SPEED)

    def is_dynamic(self, what=None):
        '''Retorna True se o objeto for dinâmico.
        
        Existem 4 assinaturas diferentes:
            obj.is_dynamic()
                Equivalente a `obj.is_dynamic('linear') or obj.is_dynamic('angular')`
            obj.is_dynamic('linear')
                Retorna o estado dinâmico das variáveis lineares.
            obj.is_dynamic('angular')
                Retorna o estado dinâmico das variáveis angulares.
            obj.is_dynamic('both')
                Equivalente a `obj.is_dynamic('linear') and obj.is_dynamic('angular')`
        '''

        if what is None:
            return bool(self._invmass) or bool(self._invinertia)
        elif what == 'linear':
            return bool(self._invmass)
        elif what == 'angular':
            return bool(self._invintertia)
        elif what == 'both':
            return bool(self._invmass and self._invinertia)
        else:
            raise ValueError('unknown mode: %r' % what)

    def is_kinematic(self, what=None):
        '''Retorna True se o objeto for cinemático em oposição a ser um objeto
        dinâmico.
        
        Existem 4 assinaturas diferentes:
            obj.is_kinematic()
                Equivalente a `obj.is_kinematic('linear') and obj.is_kinematic('angular')`
            obj.is_kinematic('linear')
                Retorna o estado cinemático das variáveis lineares.
            obj.is_kinematic('angular')
                Retorna o estado cinemático das variáveis angulares.
            obj.is_kinematic('any')
                Equivalente a `obj.is_kinematic('linear') or obj.is_kinematic('angular')`
        '''

        if what is None:
            return not (self._invmass or self._invinertia)
        elif what == 'linear':
            return not self._invmass
        elif what == 'angular':
            return not self._invintertia
        elif what == 'any':
            return not (self._invmass and self._invinertia)
        else:
            raise ValueError('unknown mode: %r' % what)

    def is_static(self, what=None):
        '''Retorna True se o objeto for estático.
        
        Existem 4 assinaturas diferentes:
            obj.is_static()
                Equivalente a `obj.is_static('linear') and obj.is_static('angular')`
            obj.is_static('linear')
                Retorna verdadeiro se o objeto for estático nas variáveis lineares.
            obj.is_kinematic('angular')
                Retorna verdadeiro se o objeto for estático nas variáveis angulare.
            obj.is_static('any')
                Equivalente a `obj.is_static('linear') or obj.is_static('angular')`
        '''

        if what == 'linear':
            return not bool(self._invmass) and not (self._vel.x or self.vel.y)
        elif what == 'angular':
            return not bool(self._invinertia) and not self._omega
        elif what is None:
            return self.is_static('linear') and self.is_static('angular')
        elif what == 'any':
            return self.is_static('linear') or self.is_static('angular')
        else:
            raise ValueError('unknown mode: %r' % what)

    def make_dynamic(self, what=None):
        '''Resgata a massa, inércia e velocidades anteriores de um objeto 
        paralizado pelo método `obj.make_static()` ou `obj.make_kinematic()`.
        
        Pode especificar as variáveis lineares ou angulares separadamente com o
        argumento opcional `what`.
        '''

        linear = angular = True
        if what == 'linear':
            angular = False
        elif what == 'angular':
            linear = False
        elif what is not None:
            raise ValueError('unknown mode: %r' % what)

        if linear:
            if not self._invmass: self.mass = self._oldmass
            if not self._vel.norm_sqr(): self.vel = self._oldvel
        if angular:
            if not self._invinertia: self.inertia = self._oldinertia
            if not self._omega: self.omega = self._oldomega

    def make_kinematic(self, what=None):
        '''Transforma o objeto em cinemático fazendo com que as massas e 
        momento de inércia se tornem infinitos.
        
        Pode especificar as variáveis lineares ou angulares separadamente com o
        argumento opcional `what`.
        '''
        linear = angular = True
        if what == 'linear':
            angular = False
        elif what == 'angular':
            linear = False
        elif what is not None:
            raise ValueError('unknown mode: %r' % what)

        if linear:
            if self._invmass:
                self._oldmass = self._mass
                self.mass = 'inf'
        if angular:
            if self._invinertia:
                self._oldinertia = self._inertia
                self.inertia = 'inf'

    def make_static(self, what=None):
        '''Transforma o objeto em estático fazendo com que as massas e 
        momento de inércia se tornem infinitos e as velocidades nulas.
        
        Pode especificar as variáveis lineares ou angulares separadamente com o
        argumento opcional `what`.
        '''

        linear = angular = True
        if what == 'linear':
            angular = False
        elif what == 'angular':
            linear = False
        elif what is not None:
            raise ValueError('unknown mode: %r' % what)

        self.make_kinematic(what)
        if linear:
            if self._vel.norm_sqr():
                self._oldvel = tuple(self._vel)
                self.vel = (0, 0)
        if angular:
            if self._omega:
                self._oldomega = self._omega
                self.omega *= 0

    #===========================================================================
    # Desenhando objeto
    #===========================================================================
    def get_drawable(self, color='black', lw=0, solid=True):
        '''Retorna um objeto que respeita a interface Drawable e pode ser 
        utilizado para a renderização do objeto físico.'''
    
        return self.drawable
    
    def get_primitive_drawable(self):
        
        raise NotImplementedError
    
    def get_aabb_drawable(self, color='black', lw=0, solid=True):
        '''Retorna um objeto que pode ser utilizado para desenhar a AABB do
        objeto físico considerado'''
        
        return RectEcho(self, color=color, lw=lw, solid=solid)
    
    #===========================================================================
    # Controle de eventos
    #===========================================================================
    # Delegações
    long_press = signal('long-press', 'key', delegate='input')
    key_up = signal('key-up', 'key', delegate='input')
    key_down = signal('key-down', 'key', delegate='input')
    mouse_motion = signal('mouse-motion', delegate='input')
    mouse_click = signal('mouse-click', 'button', delegate='input')
    
    # Eventos privados
    frame_enter = signal('frame-enter')
    collision = signal('collision', num_args=1)
    
    @lazy
    def input(self):
        self.input = self.world.simulation.input
        return self.input
    
    #===========================================================================
    # Interface Python
    #===========================================================================
    # Faz os objetos serem ordenados pelo valor da sua coordenada xmin. Isto
    # facilita a implementação do reordenamento de objetos, já que é possível
    # aplicar a função sort() diretamente na lista de objetos.
    def __gt__(self, other):
        return self._xmin > other._xmin

    def __lt__(self, other):
        return self._xmin < other._xmin

    # Define igualdade <==> identidade
    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)

    # Representação do objeto como string
    def __repr__(self):
        tname = type(self).__name__
        pos = ', '.join('%.1f' % x for x in self.pos)
        vel = ', '.join('%.1f' % x for x in self.vel)
        return '%s(pos=(%s), vel=(%s))' % (tname, pos, vel)

#===============================================================================
# Classes derivadas
#===============================================================================
class LinearObject(Object):
    '''Classe base para todos os objetos que não possuem dinâmica angular.'''

    def __init__(self, **kwds):
        if 'inertia' in kwds or 'omega' in kwds or 'theta' in kwds:
            raise TypeError('cannot set angular properties of linear objects')
        super(LinearObject, self).__init__(**kwds)
        self._invinertia = self._omega = self._theta = 0.0
        self._inertia = float('inf')

    @property
    def inertia(self):
        return float('inf')
    @inertia.setter
    def inertia(self, value):
        if 1 / value:
            raise ValueError('LinearObjects have infinite inertia')

    omega = copy(Object.omega)
    @omega.setter
    def omega(self, value):
        if value:
            raise ValueError('LinearObjects have null angular velocity')

    theta = copy(Object.theta)
    @omega.setter
    def theta(self, value):
        if value:
            raise ValueError('LinearObjects have fixed orientation')

if __name__ == '__main__':
    from FGAme import *
    import doctest
    doctest.testmod()

