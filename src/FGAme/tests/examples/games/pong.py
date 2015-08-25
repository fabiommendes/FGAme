# -*- coding: utf8 -*-
'''
Implementação do tradicional jogo Pong.
'''

from FGAme import *
from random import uniform, choice, random


class Pong(World):

    def __init__(self, **kwds):
        super(Pong, self).__init__()
        self.add_bounds(width=(-300, 10))

        # Linha central
        self.add(draw.AABB(shape=(15, 550), pos=(400, 300),
                           color=(200, 200, 200)))

        # Cria a bola com uma velocidade aleatória
        self.ball = Circle(30, color='red', world=self)
        self.ball.pos = (100, 300)
        self.ball.vel = (+700, choice([-1, 1]) * uniform(200, 400))

        # Cria a barras
        self.pong1 = AABB(shape=[20, 130], pos=(50, 300),
                          world=self, mass='inf')
        self.pong2 = AABB(shape=[20, 130], pos=(750, 300),
                          world=self, mass='inf')

        # Registra eventos
        self.listen('long-press', 'up', self.move_up, obj=self.pong2)
        self.listen('long-press', 'down', self.move_down, obj=self.pong2)
        self.listen('long-press', 'w', self.move_up, obj=self.pong1)
        self.listen('long-press', 's', self.move_down, obj=self.pong1)
        self.listen('key-down', 'space', self.toggle_pause)

    def move_up(self, obj):
        '''Move a raquete fornecida para cima'''

        if obj.ymax < 590:
            obj.move(Vec2(0, 10))

    def move_down(self, obj):
        '''Move a raquete fornecida para baixo'''

        if obj.ymin > 10:
            obj.move(Vec2(0, -10))

if __name__ == '__main__':
    Pong().run()
