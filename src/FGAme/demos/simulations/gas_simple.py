# -*- coding: utf8 -*-
'''
Este exemplo mostra um gás de esferas rígidas em um campo gravitacional.
'''

from FGAme import World, Circle, AABB, Vec2, listen
from random import uniform


class Gas(World):

    def __init__(self,
                 gravity=100, friction=0.0, restitution=0.95,
                 num_balls=80, speed=200, radius=10,
                 color='random'):
        '''Cria uma simulação de um gás de partículas sujeito à ação da
        gravidade aberto na parte de cima.

        O parâmetros `num_balls` controla o número esferas de raio ``radius``
        com velocidades no intervalo de +/-`speed`.'''

        self.num_balls = num_balls
        self.radius = radius
        self.speed = speed

        super(Gas, self).__init__(gravity=gravity, friction=friction,
                                  restitution=restitution)

    def init(self):
        # Inicia paredes
        AABB(0, 30, 30, 800, world=self, mass='inf')
        AABB(770, 800, 30, 800, world=self, mass='inf')
        AABB(0, 800, 0, 30, world=self, mass='inf')

        # Cria lista de bolas
        speed = self.speed
        for _ in range(self.num_balls):
            Circle(
                radius=self.radius,
                vel=Vec2(uniform(-speed, speed), uniform(-speed, speed)),
                pos=Vec2(uniform(50, 750), uniform(50, 400)),
                color='random',
                world=self,
            )

    @listen('key-down', 'space')
    def toggle_pause(self):
        super(Gas, self).toggle_pause()

# Inicia a simulação
if __name__ == '__main__':
    w = Gas()
    w.run()
