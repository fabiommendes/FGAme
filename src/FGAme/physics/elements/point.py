# -*- coding: utf8 -*-

from FGAme.physics.elements import (
    PHYS_HAS_MASS,
    PHYS_HAS_SPEED
)
from FGAme.physics.elements import PhysElement
from FGAme.mathutils import Vector, VectorM, asvector, dot

#==============================================================================
# Objetos que obedecem à interface de "partícula" de física. Este objetos
# possuem grandezas lineares e parâmetros físicos associados à elas definidos.
# Objetos mais complexos (e.g., corpos rígidos) podem herdar dessa classe e
# implementar outras interfaces e atributos adicionais.
# se
# Apenas as propriedades físicas são definidas aqui. Cores, texturas, resposta
# a eventos do usuário, etc devem ser implementadas em sub-classes.
#==============================================================================


class PhysPoint(PhysElement):

    '''Objeto físico com apenas propriedades lineares.

    Trata-se abstratamente de uma partícula pois lidamos apenas com grandezas
    pontuais como posição/velocidade/aceleração.

    Attributes
    ----------

    ::
        **Propriedades físicas do objeto**
    mass
        Massa do objeto. Possui o valor padrão de 1. Uma massa infinita
        transforma o objeto num objeto cinemático que não responde a forças
        lineares.

    ::
        **Variáveis dinâmicas**
    pos
        Posição do centro de massa do objeto
    vel
        Velocidade linear medida a partir do centro de massa
    accel
        Aceleração acumulada recalculada em cada frame


    Example
    -------

    Simula uma partícula em lançamento parabólico

    >>> p = PhysPoint(vel=(8, 8))
    >>> for i in range(8):
    ...     print('%4.1f, %4.1f' % tuple(p.pos))
    ...     p.apply_accel((0, -8), dt=0.25)
     0.0,  0.0
     2.0,  1.5
     4.0,  2.5
     6.0,  3.0
     8.0,  3.0
    10.0,  2.5
    12.0,  1.5
    14.0,  0.0
    '''

    __slots__ = ['_pos', '_vel', '_accel', '_invmass']

    def __init__(self, pos=(0, 0), vel=(0, 0), mass=1.0):
        super(PhysPoint, self).__init__(flags=PHYS_HAS_MASS | PHYS_HAS_SPEED)
        self._pos = VectorM(*pos)
        self._vel = VectorM(*vel)
        self._accel = VectorM(0, 0)
        self._invmass = 1.0
        self.mass = mass

    #==========================================================================
    # Propriedades
    #==========================================================================

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
        self._invmass = 1.0 / value

    # Variáveis de estado -----------------------------------------------------
    @property
    def pos(self):
        return Vector(*self._pos)

    @pos.setter
    def pos(self, value):
        self.move(value - self._pos)

    @property
    def vel(self):
        return Vector(*self._vel)

    @vel.setter
    def vel(self, value):
        self.boost(value - self._vel)

    @property
    def accel(self):
        return Vector(*self._accel)

    @accel.setter
    def accel(self, value):
        self._accel.copy_from(value)

    # Parâmetros físicos derivados --------------------------------------------
    @property
    def linearE(self):
        return self._mass * dot(self.vel, self.vel) / 2

    @property
    def kineticE(self):
        return self.linearE

    @property
    def momentumP(self):
        return self.mass * self.vel

    #=========================================================================
    # Deslocamentos
    #=========================================================================
    def move(self, delta):
        '''Move o objeto por vetor de deslocamento delta'''

        self._pos += delta

    def boost(self, delta):
        '''Adiciona um valor vetorial delta à velocidade linear'''

        self._vel += delta

    #=========================================================================
    # Resposta a forças, impulsos e atualização da física
    #=========================================================================
    def external_force(self, t):
        '''Define uma força externa que depende do tempo t.

        Pode ser utilizado por sub-implementações para definir uma força
        externa aplicada aos objetos de uma sub-classe ou usando o recurso de
        "monkey patching" do Python
        '''

    def init_accel(self):
        '''Inicializa o vetor de aceleração com o valor nulo'''

        self._accel *= 0

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
        um integrador de ordem superior (O(dt^4) vs O(dt^2)). Além disto, ele
        possui a propriedade simplética, o que implica que o erro da energia
        não tende a divergir, mas sim oscilar ora positivamente ora
        negativamente em torno de zero. Isto é extremamente desejável para
        simulações de física que parecam realistas.

        A integração de Euler seria implementada como:

            x(t + dt) = x(t) + v(t) * dt + a(t) * dt**2 / 2
            v(t + dt) = v(t) + a(t) * dt

        Em código Python

        >>> self.move(self.vel * dt + a * (dt**2/2))           # doctest: +SKIP
        >>> self.boost(a * dt)                                 # doctest: +SKIP

        Este método simples e intuitivo sofre com o efeito da "deriva de
        energia". Devido aos erros de truncamento, o valor da energia da
        solução numérica flutua com relação ao valor exato. Na grande maioria
        dos sistemas, esssa flutuação ocorre com mais probabilidade para a
        região de maior energia e portanto a energia tende a crescer
        continuamente, estragando a credibilidade da simulação.

        Velocity-Verlet está numa classe de métodos numéricos que não sofrem
        com esse problema. A principal desvantagem, no entanto, é que devemos
        manter uma variável adicional com o último valor conhecido da
        aceleração. Esta pequena complicação é mais que compensada pelo ganho
        em precisão numérica. O algorítmo consiste em:

            x(t + dt) = x(t) + v(t) * dt + a(t) * dt**2 / 2
            v(t + dt) = v(t) + [(a(t) + a(t + dt)) / 2] * dt

        O termo a(t + dt) normalemente só pode ser calculado se soubermos como
        obter as acelerações como função das posições x(t + dt). Na prática,
        cada iteração de .apply_accel() calcula o valor da posição em x(t + dt)
        e da velocidade no passo anterior v(t). Calcular v(t + dt) requer uma
        avaliação de a(t + dt), que só estará disponível na iteração seguinte.
        A próxima iteração segue então para calcular v(t + dt) e x(t + 2*dt), e
        assim sucessivamente.

        A ordem de acurácia de cada passo do algoritmo Velocity-Verlet é de
        O(dt^4) para uma força que dependa exclusivamente da posição e tempo.
        Caso haja dependência na velocidade, a acurácia reduz e ficaríamos
        sujeitos aos efeitos da deriva de energia. Normalmente as forças
        físicas que dependem da velocidade são dissipativas e tendem a reduzir
        a energia total do sistema muito mais rapidamente que a deriva de
        energia tende a fornecer energia espúria ao sistema. Deste modo, a
        acurácia ficaria reduzida, mas a simulação ainda manteria alguma
        credibilidade.
        '''

        a = asvector(a)
        self._accel += a
        self._accel /= 2
        self.boost(self._accel * dt)
        self.move(self._vel * dt + a * (dt ** 2 / 2.))
        self._accel.copy_from(a)

    def apply_impulse(self, impulse, pos=None, relative=False):
        '''Aplica um impulso linear ao objeto. Isto altera sua velocidade
        linear com relação ao centro de massa.

        Se for chamado com dois agumentos aplica o impulso em um ponto
        específico e também resolve a dinâmica angular.
        '''

        self.boost(impulse / self.mass)

    #=========================================================================
    # Controle de estado dinâmico
    #=========================================================================
    def is_dynamic_linear(self):
        # Implementação um pouco mais rápida
        return bool(self._invmass)

    def is_dynamic_angular(self):
        return False

    def is_kinematic_linear(self):
        # Implementação um pouco mais rápida
        return not bool(self._invmass)

    def is_kinematic_angular(self):
        return True

    #=========================================================================
    # Interface Python
    #=========================================================================
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

if __name__ == '__main__':
    import doctest
    doctest.testmod()
