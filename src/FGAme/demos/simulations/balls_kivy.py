# -*- coding: utf8 -*-
'''
Este exemplo mostra um gás de esferas rígidas em contato com um êmbulo sujeito a
uma força viscosa. A energia é dissipada no movimento do êmbolo e aos poucos
as partículas cessam o movimento.
'''

from FGAme import *
from random import uniform, randint

# Inicializa o mundo


class Gas(World):

    def __init__(self,
                 gravity=800, friction=0.0, restitution=0.95,
                 num_balls=80, speed=400, radius=10,
                 color='random'):
        '''Cria uma simulação de um gás de partículas confinado por um êmbolo
        com `num_balls` esferas de raio `radius` com velocidades no intervalo
        de +/-`speed`.'''

        super(Gas, self).__init__(gravity=gravity, dfriction=friction,
                                  restitution=restitution)
        AABB(0, 30, 30, 800, world=self, mass='inf')
        AABB(770, 800, 30, 800, world=self, mass='inf')
        AABB(0, 800, 0, 30, world=self, mass='inf')

        # Inicia bolas
        self.bolas = []
        for _ in range(num_balls):
            pos = Vec2(uniform(20, 780), uniform(20, 400))
            vel = Vec2(uniform(-speed, speed), uniform(-speed, speed))
            bola = Circle(radius=radius, vel=vel, pos=pos, mass=1)
            bola.color = self.get_color(color)
            self.bolas.append(bola)
            self.add(bola)

    def get_color(self, color):
        if color == 'random':
            return (randint(0, 255), randint(0, 255), randint(0, 255))
        else:
            return color

    @listen('key-down', 'space')
    def toggle_pause(self):
        super(Gas, self).toggle_pause()

# Inicia a simulação
if __name__ == '__main__':
    Gas().run()
