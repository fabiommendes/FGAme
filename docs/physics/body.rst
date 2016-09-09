mass
    Object'Massa do objeto. Possui o valor padrão de 1. Uma massa infinita
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

::
     **Forças locais**

gravity
    Valor da aceleração da gravidade aplicada ao objeto
damping, adamping
    Constante de amortecimento linear/angular para forças viscosas
    aplicadas ao objeto
owns_gravity, owns_damping, owns_adamping
    Se Falso (padrão) utiliza os valores de gravity e damping/adamping
    fornecidos pelo mundo
accel_static
    Caso verdadeiro, aplica as acelerações de gravidade, damping/adamping
    no objeto mesmo se ele for estático

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

    **Flags de colisão**
col_group : int ou sequência
    Número inteiro positivoque representa o grupo a qual o objeto pertence.
    Objetos do mesmo grupo nunca colidem entre si. `col_group` pode ser uma
    sequência de valores caso o objeto pertença a vários grupos. O grupo
    zero (padrão) é tratado de forma especial e todos os objetos deste
    grupo colidem entre si.
col_layer : int ou sequência
    Número inteiro positivo representando a camdada à qual o objeto
    pertence. O valor padrão é zero. Apenas objetos que estão na mesma
    camada colidem entre si. `col_layer` pode ser uma sequência de valores
    caso o objeto participe de várias camadas.


Integration
===========

Observations
------------

This method implements the Velocity-Verlet integration. This method is
superior to the most traditional Euler integrator for two reasons:


A integração de Euler seria implementada como:

    x(t + dt) = x(t) + v(t) * dt
    v(t + dt) = v(t) + a(t) * dt

Em código Python,

>>> self.imove(self.vel * dt + a * (dt**2/2))           # doctest: +SKIP
>>> self.boost(a * dt)                                 # doctest: +SKIP

Este método simples e intuitivo sofre com o efeito da "deriva de
energia". Devido aos erros de aproximação, o valor da energia da
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
superior to the most traditional Euler integrator for two reasons:


A integração de Euler seria implementada como:

    x(t + dt) = x(t) + v(t) * dt
    v(t + dt) = v(t) + a(t) * dt

Em código Python,

>>> self.imove(self.vel * dt + a * (dt**2/2))           # doctest: +SKIP
>>> self.boost(a * dt)                                 # doctest: +SKIP

Este método simples e intuitivo sofre com o efeito da "deriva de
energia". Devido aos erros de aproximação, o valor da energia da
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
superior to the most traditional Euler integrator for two reasons:


A integração de Euler seria implementada como:

    x(t + dt) = x(t) + v(t) * dt
    v(t + dt) = v(t) + a(t) * dt

Em código Python,

>>> self.imove(self.vel * dt + a * (dt**2/2))           # doctest: +SKIP
>>> self.boost(a * dt)                                 # doctest: +SKIP

Este método simples e intuitivo sofre com o efeito da "deriva de
energia". Devido aos erros de aproximação, o valor da energia da
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



#################

Consider an object created at origin and another one in position (4, 3)

>>> b1 = Body(pos=(2, 0), mass=1)
>>> b2 = Body(pos=(-1, 0), mass=2)

Let us apply an impulse J to b1

>>> J = Vec2(0, 2)
>>> b1.apply_impulse(J)

Notice this affects its velocity according to the formula
$\delta v = J / m$:

>>> b1.vel
Vec(0, 2)

If we apply an oposite impulse to b2, the result should not alter the
total linear momentum, which remains null

>>> b2.apply_impulse(-J, pos=(0, 0)); b2.vel
Vec(0, -1)
>>> b1.momentumP() + b2.momentumP()
Vec(0, 0)

Now consider two bodies with moment of inertia and some arbitrary
initial velocities. The same conservation laws apply, and now we should
also check conservation of angular momentum.

>>> b1 = Body(pos=(0, 0), mass=1, inertia=1, vel=(2, 0), omega=1)
>>> b2 = Body(pos=(4, 3), mass=2, inertia=2, vel=(-1, 1))

Let us save the initial angular momentum

>>> P0 = b1.momentumP() + b2.momentumP()

Angular momentum requires a reference point. We shall use the system's
center of mass, however any fixed reference will do.

>>> from FGAme.physics import center_of_mass
>>> Rcm = center_of_mass(b1, b2)
>>> L0 = b1.momentumL(Rcm) + b2.momentumL(Rcm)

Let us apply opposite impulses such as Newton's third law tell us.
We have to be careful to apply the angular momentum in the same point,
which should represent the contact point where the collision takes
place.

>>> J = Vec2(0, 2)
>>> b1.apply_impulse(J, pos=(4, 0))
>>> b2.apply_impulse(-J, pos=(4, 0))

Now we verify that the initial and final linear and angular momenta are
indeed the same.

>>> b1.momentumP() + b2.momentumP() == P0
True
>>> b1.momentumL(Rcm) + b2.momentumL(Rcm) == L0
True