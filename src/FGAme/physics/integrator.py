from collections import UserList
from FGAme import *


class Integrator(UserList):

    '''Classe se comporta como uma lista de objetos cuja dinâmica é resolvida
    separadamente do loop principal da FGAme.
    Objetos podem ser adicionados a um grupo do tipo Integrator caso o
    algoritmo de Euler semi-implícito utilizado pela FGAme não possua a
    acurácia necessária para resolução de forças (ex.: sistemas
    autogravitantes)
    '''

    def __init__(self):
        self._data = []

    def add(self, obj):
        '''Adiciona um objeto à lista de objetos'''

        self.append(obj)

    @property
    def data(self):
        return self._data

    def update(self, dt):
        '''Atualiza as posições e velocidades'''


class GravityIntegrator(Integrator):

    def __init__(self, G=1, framerate=30):
        super(GravityIntegrator, self).__init__()
        self.G = G
        self.dt = 1 / framerate

    def update_accelerations(self):
        '''Retorna a lista de acelerações para cada objeto'''

        for i, current in enumerate(self):
            current.accel_prev = current.accel

            for other in self:
                if current != other:
                    #d  = r(b) - r(a)
                    distance = other.pos - current.pos
                    # a(a) = m(b) * d/|d|^3
                    current.accel = other.mass * \
                        distance / distance.norm() ** 3
            # a <= a*G
            current.accel *= self.G
            self[i] = current

    def update(self, iterations=1):
        '''Utiliza o método de Velocity Verlet para atualizar as posições e
        velocidades'''

        dt = self.dt / iterations
        for _ in range(iterations):
            self.update_accelerations()

            for i, p in enumerate(self):
                # r(k+1) = r(k) + dt*v(k) + a(k)*(dt**2) /2
                p.pos += dt * p.vel + p.accel_prev * (dt ** 2) / 2
                # v(k+1) = v(k) + dt * ( a(k)+a(k-1) )/2
                p.vel += + dt * (p.accel + p.accel_prev) / 2

                self[i] = p


#### TESTE UNITÁRIO ######
#'''
# Este exemplo simula um sitema solar com dois corpos, que possuem
# massas, posições e velociodades adequados para manter uma orbita.
class Universe(World):

    def __init__(self):
        super(Universe, self).__init__(background=(35, 0, 100))

        sun = Circle(radius=5, color=(255, 215, 0), mass=1e3,
                     pos=(400, 300), vel=(0, 0))
        earth = Circle(radius=3, color=(0, 200, 255), mass=1,
                       pos=(400 + 80, 300), vel=(0, (1e3 / 200) ** 0.5))
        self.orbit = GravityIntegrator()
        self.orbit.add(sun)
        self.orbit.add(earth)
        self.add((sun, earth))

    @listen('frame-enter')
    def resolve(self):
        for i in range(10):
            self.orbit.update()
if __name__ == '__main__':
    universe = Universe()
    universe.run()
#'''
