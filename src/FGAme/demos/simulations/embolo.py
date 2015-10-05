# -*- coding: utf8 -*-
'''
Este exemplo mostra um gás de esferas rígidas em contato com um êmbulo sujeito
a uma força viscosa. A energia é dissipada no movimento do êmbolo e aos poucos
as partículas cessam o movimento.

É possível adicionar uma força às partículas utilizando as setas do teclado.
'''

from FGAme import *
from random import uniform, randint


class Gas(World):

    def __init__(self,
                 gravity=200, friction=0.0, restitution=1.0,
                 num_balls=100, speed=200, radius=10,
                 color='random'):
        '''Cria uma simulação de um gás de wpartículas confinado por um êmbolo
        com `num_balls` esferas de raio `radius` com velocidades no intervalo
        de +/-`speed`.'''

        super(Gas, self).__init__(gravity=gravity, friction=friction)
        self.add_bounds(width=(10, 10, 10, -1000), delta=400)

        # Inicia bolas
        self.bolas = []
        for _ in range(num_balls):
            pos = Vec2(uniform(20, 780), uniform(20, 400))
            vel = Vec2(uniform(-speed, speed), uniform(-speed, speed))
            bola = Circle(radius=radius, vel=vel, pos=pos, mass=1,
                          color='random')
            self.bolas.append(bola)
            self.add(bola)

        # Inicia êmbolo
        embolo = AABB(bbox=(11, 789, 420, 470), color=(150, 0, 0),
                      mass=num_balls / 2, damping=5)
        self.add(embolo)

    @listen('long-press', 'q')
    def energy_up(self):
        '''Aumenta a energia de todas as partículas'''

        for bola in self.bolas:
            bola.vel += 1 * bola.vel.normalized()

    @listen('long-press', 'a')
    def energy_down(self):
        '''Diminui a energia de todas as partículas'''

        for bola in self.bolas:
            bola.vel *= 0.98

    @listen('key-down', 'space')
    def toggle_pause(self):
        super(Gas, self).toggle_pause()

    @listen('long-press', 'up', Vec2(0, 9))
    @listen('long-press', 'down', Vec2(0, -2))
    @listen('long-press', 'left', Vec2(-4, 0))
    @listen('long-press', 'right', Vec2(4, 0))
    def boost(self, Vec):
        for bola in self.bolas:
            bola.vel += Vec
            bola.vel *= 0.99

# Inicia a simulação
if __name__ == '__main__':
    game = Gas()
    game.run()
