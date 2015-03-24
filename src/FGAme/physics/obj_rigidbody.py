# -*- coding: utf8 -*-

from FGAme.mathutils import Vector, sqrt
from FGAme.physics.obj_all import Dynamic

__all__ = ['RigidBody', 'LinearRigidBody']

INF = float('inf')


class RigidBody(Dynamic):

    '''Classe pai para todos os objetos físicos da FGAme.

    Attributes
    ----------

    ::
        **Propriedades físicas do objeto**
    inertia
        Momento de inércia do objeto com relação ao eixo z no centro de massa.
        Calculado automaticamente a partir da geometria e densidade do objeto.
        Caso seja infinito, o objeto não responderá a torques.
    ROG, ROG_sqr
        Raio de giração e o quadrado do raio de giração. Utilizado para
        calcular o momento de inércia: $I = M R^2$, onde I é o momento de
        inércia, M a massa e R o raio de giração.
    density
        Densidade de massa: massa / área
    area
        Área que o objeto ocupa

    ::
        **Variáveis dinâmicas**
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


    Example
    -------

    >>> b = RigidBody()
    '''

    __slots__ = ['_omega', '_theta', '_alpha', '_density', '_invinertia',
                 '_xmin', '_xmax', '_ymin', '_ymax']

    def __init__(self, xmin, xmax, ymin, ymax,
                 pos=(0, 0), vel=(0, 0), theta=0.0, omega=0.0,
                 mass=None, density=None, inertia=None):

        # Define a caixa de contorno
        self._xmin = float(xmin)
        self._xmax = float(xmax)
        self._ymin = float(ymin)
        self._ymax = float(ymax)
        if xmin >= xmax:
            raise ValueError('invalid bounding box: xmin >= xmax')
        if ymin >= ymax:
            raise ValueError('invalid bounding box: ymin >= ymax')

        # Harmoniza massa, inércia e densidade
        if density is not None:
            density = float(density)
            if mass is None:
                mass = density * self.area()
            if inertia is None:
                inertia = density * self.area() * self.ROG_sqr()

        elif mass is not None:
            density = float(mass) / self.area()
            if inertia is None:
                inertia = mass * self.ROG_sqr()

        elif inertia is not None:
            density = float(inertia) / (self.area() * self.ROG_sqr())
            if mass is None:
                mass = float(inertia) / self.ROG_sqr()

        else:
            density = 1.0
            mass = density * self.area()
            inertia = density * self.area() * self.ROG_sqr()

        self._invmass = 1.0 / mass
        self._invinertia = 1.0 / inertia
        self._density = float(density)

        # Inicializa as variáveis de estado
        super(RigidBody, self).__init__(pos, vel, mass)
        self._omega = float(omega or 0)
        self._theta = 0.0
        if theta is not None:
            self.rotate(theta)
        self._alpha = 0.0

    def _init_inertias(self, density, mass, inertia):
        pass

    ###########################################################################
    #                 Propriedades e constantes físicas
    ###########################################################################

    @property
    def mass(self):
        try:
            return 1.0 / self._invmass
        except ZeroDivisionError:
            return float('inf')

    @mass.setter
    def mass(self, value):
        value = float(value)

        if value <= 0:
            raise ValueError('mass cannot be null or negative')
        elif value != INF:
            self._density = value / self.area()
            if self._invinertia:
                inertia = value * self.ROG_sqr()
                self._invinertia = 1.0 / inertia
            self._invmass = 1.0 / value
        else:
            self._invmass = 0.0

    @property
    def inertia(self):
        try:
            return 1.0 / self._invinertia
        except ZeroDivisionError:
            return INF

    @inertia.setter
    def inertia(self, value):
        value = float(value)

        if value <= 0:
            raise ValueError('inertia cannot be null or negative')
        elif value != INF:
            self._density = value / (self.area() * self.ROG_sqr())
            if self._invmass:
                self._invmass = 1.0 / (self._density * self.area())
            self._invinertia = 1.0 / value
        else:
            self._invinertia = 0.0

    @property
    def density(self):
        return self._density

    @density.setter
    def density(self, value):
        rho = float(value)
        self._density = rho
        if self._invmass:
            self._invmass = 1.0 / (self.area() * rho)
        if self._invinertia:
            self._invinertia = 1.0 / (self.area() * rho * self.ROG_sqr())

    # Variáveis de estado #####################################################

    @property
    def theta(self):
        return self._theta

    @theta.setter
    def theta(self, value):
        self.rotate(value - self._theta)

    @property
    def omega(self):
        return self._omega

    @omega.setter
    def omega(self, value):
        self.aboost(value - self._omega)

    # Propriedades da caixa de contorno #######################################

    @property
    def xmin(self):
        return self._xmin

    @property
    def xmax(self):
        return self._xmax

    @property
    def ymin(self):
        return self._ymin

    @property
    def ymax(self):
        return self._ymax

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

    # Parâmetros físicos derivados ############################################

    def angularE(self):
        '''Retorna a contribuição angular para a energia cinética'''

        return self._inertia * self.omega ** 2 / 2

    def kineticE(self):
        '''Retorna a energia cinética total'''

        return self.linearE + self.angularE

    def momentumL(self):
        '''Retorna o vetor momentum linear'''

        return self.inertia * self.omega

    ###########################################################################
    #                         Propriedades geométricas
    ###########################################################################
    def area(self):
        '''Retorna a área do objeto'''

        raise NotImplementedError('must be implemented in child classes')

    def ROG_sqr(self):
        '''Retorna o raio de giração ao quadrado'''

        raise NotImplementedError('must be implemented in child classes')

    def ROG(self):
        '''Retorna o raio de giração'''

        return sqrt(self.ROG_sqr())

    ###########################################################################
    #                             Deslocamentos
    ###########################################################################

    def move(self, delta):
        x, y = delta
        self._pos += delta
        self._xmin += x
        self._xmax += x
        self._ymin += y
        self._ymax += y

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

    ###########################################################################
    #          Resposta a forças, impulsos e atualização da física
    ###########################################################################

    def external_torque(self, t):
        '''Define uma torque externo análogo ao método .external_force()'''

        return None

    def init_alpha(self):
        '''Reinicializa a aceleração angular com o valor nulo.'''

        self._alpha = 0

    def apply_torque(self, torque, dt):
        '''Aplica um torque durante um intervalo de tempo dt.'''

        self.apply_alpha(torque * self._invinertia, dt)

    def apply_alpha(self, alpha, dt):
        '''Aplica uma aceleração angular durante um intervalo de tempo dt.

        Tem efeito em objetos cinemáticos.'''

        dt = dt / 2
        self.aboost(alpha * dt)
        self.rotate(self._omega * dt + alpha * dt ** 2 / 2.)

    def apply_aimpulse(self, itorque):
        '''Aplica um impulso angular ao objeto.'''

        self.aboost(itorque / self.inertia)

    ###########################################################################
    #                       Controle de estado dinâmico
    ###########################################################################

    def is_dynamic_angular(self):
        return bool(self._invinertia)

    def is_kinematic_angular(self):
        return not bool(self._invinertia)

    # Faz os objetos serem ordenados pelo valor da sua coordenada xmin. Isto
    # facilita a implementação do reordenamento de objetos, já que é possível
    # aplicar a função sort() diretamente na lista de objetos.
    def __gt__(self, other):
        return self._xmin > other._xmin

    def __lt__(self, other):
        return self._xmin < other._xmin


class LinearRigidBody(RigidBody):

    '''
    Classe que implementa corpos rígidos sem dinâmica angular.
    '''

    def __init__(self, xmin, xmax, ymin, ymax,
                 pos=(0, 0), vel=(0, 0),
                 mass=None, density=None):

        super(LinearRigidBody, self).__init__(
            xmin, xmax, ymin, ymax, pos, vel,
            mass=mass, density=density
        )
        self._invinertia = 0.0

    @property
    def inertia(self):
        return INF

    @inertia.setter
    def inertia(self, value):
        if 1 / value:
            raise ValueError('LinearObjects have infinite inertia')

    @property
    def omega(self):
        return 0.0

    @omega.setter
    def omega(self, value):
        if value:
            raise ValueError('LinearObjects have null angular velocity')

    @property
    def theta(self):
        return 0.0

    @theta.setter
    def theta(self, value):
        if value:
            raise ValueError('LinearObjects have fixed orientation')

    def is_dynamic_angular(self):
        return False

    def is_kinematic_angular(self):
        return True

if __name__ == '__main__':
    import doctest
    doctest.testmod()
