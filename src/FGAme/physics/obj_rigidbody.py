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

    '''

    __slots__ = []

    def __init__(self, pos=(0, 0), vel=(0, 0), theta=0.0, omega=0.0,
                 mass=None, density=None, inertia=None):

        super(RigidBody, self).__init__(pos, vel, theta, omega, inertia='inf')

        # Harmoniza massa, inércia e densidade
        if density is not None:
            density = float(density)
            if mass is None:
                mass = density * self.area()
            else:
                mass = float(mass)
            if inertia is None:
                inertia = density * self.area() * self.ROG_sqr()
            else:
                inertia = float(inertia)

        elif mass is not None:
            mass = float(mass)
            density = mass / self.area()
            if inertia is None:
                inertia = mass * self.ROG_sqr()
            else:
                inertia = float(inertia)

        else:
            density = 1.0
            mass = density * self.area()
            if inertia is None:
                inertia = density * self.area() * self.ROG_sqr()
            else:
                inertia = float(inertia)

        self._invmass = 1.0 / mass
        self._invinertia = 1.0 / inertia
        self._density = float(density)

        # Inicializa as variáveis de estado
        self._omega = float(omega or 0)
        self._theta = 0.0
        if theta is not None:
            self.rotate(theta)
        self._alpha = 0.0

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
        return (self.xmin, self.xmax, self.ymin, self.ymax)

    @property
    def shape(self):
        return (self.xmax - self.xmin, self.ymax - self.ymin)

    @property
    def rect(self):
        x, y = self.xmin, self.ymin
        return (x, y, self.xmax - x, self.ymax - y)


class LinearRigidBody(RigidBody):

    '''
    Classe que implementa corpos rígidos sem dinâmica angular.
    '''

    __slots__ = []

    def __init__(self, pos=(0, 0), vel=(0, 0),
                 mass=None, density=None):

        super(LinearRigidBody, self).__init__(pos, vel, 0.0, 0.0,
                                              mass=mass, density=density,
                                              inertia='inf')

    @property
    def inertia(self):
        return INF

    @inertia.setter
    def inertia(self, value):
        if float(value) != INF:
            raise ValueError('LinearObjects have infinite inertia, '
                             'got %r' % value)

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

if __name__ == '__main__':
    import doctest
    doctest.testmod()
