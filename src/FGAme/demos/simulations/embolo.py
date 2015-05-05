# -*- coding: utf8 -*-
'''
Este exemplo mostra um gás de esferas rígidas em contato com um êmbulo sujeito a
uma força viscosa. A energia é dissipada no movimento do êmbolo e aos poucos
as partículas cessam o movimento.
'''

from FGAme import *
from random import uniform, randint


class Gas(World):

    def __init__(self,
                 gravity=50, friction=0.0,
                 num_balls=100, speed=200, radius=10,
                 color='random'):
        '''Cria uma simulação de um gás de partículas confinado por um êmbolo
        com `num_balls` esferas de raio `radius` com velocidades no intervalo
        de +/-`speed`.'''

        super(Gas, self).__init__(gravity=gravity, dfriction=friction)
        self.add_bounds(width=(10, 10, 10, -1000), delta=400)

        # Inicia bolas
        self.bolas = []
        for _ in range(num_balls):
            pos = Vec2(uniform(20, 780), uniform(20, 400))
            vel = Vec2(uniform(-speed, speed), uniform(-speed, speed))
            bola = Circle(radius=radius, vel=vel, pos=pos, mass=1)
            bola.color = self.get_color(color)
            self.bolas.append(bola)
            self.add(bola)

        # Inicia êmbolo
        embolo = AABB(bbox=(11, 789, 420, 470), color=(150, 0, 0),
                      mass=num_balls / 2, damping=5)
        self.add(embolo)

    def get_color(self, color):
        if color == 'random':
            return (randint(0, 255), randint(0, 255), randint(0, 255))
        else:
            return color

    @listen('long-press', 'up')
    def energy_up(self):
        '''Aumenta a energia de todas as partículas'''

        for bola in self.bolas:
            bola.vel *= 1.01

    @listen('long-press', 'down')
    def energy_down(self):
        '''Diminui a energia de todas as partículas'''

        for bola in self.bolas:
            bola.vel *= 0.99

    @listen('key-down', 'space')
    def toggle_pause(self):
        super(Gas, self).toggle_pause()

# Inicia a simulação
if __name__ == '__main__':
    game = Gas()

    import fasttrack
    with fasttrack.timeit('run'):
        game.run(maxiter=100, throttle=False)
