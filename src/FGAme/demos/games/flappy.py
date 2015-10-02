# -*- coding: utf8 -*-
'''
Flappy Triangle on 18/11/2014
'''

from FGAme import *
from random import uniform


class Flappy(Poly):

    def __init__(self, **kwds):
        super(Flappy, self).__init__(
            [(0, 0), (40, 0), (20, 80)], color='red', **kwds)
        self.pos = (200, 300)
        self.rotate(uniform(0, 2 * math.pi))
        self.inertia *= 10
        self.omega = uniform(-2, 2)
        self.receiving_input = True

    @listen('key-down', 'space')
    def flappy_up(self):
        '''Aumenta a velocidade vertical do flappy'''

        if self.receiving_input:
            self.boost((0, 150))

    @listen('key-down', 'left', delta=0.2)
    @listen('key-down', 'right', delta=-0.2)
    def change_omega(self, delta):
        '''Modifica a velocidade angular do flappy por um fator delta'''

        if self.receiving_input:
            self.omega += delta

    @listen('collision')
    def block_input(self, col=None):
        '''Bloqueia a entrada do usuário'''

        self.receiving_input = False


class Game(World):

    def __init__(self):
        super(Game, self).__init__(gravity=200)

        # Adiciona obstáculos
        self.N = N = 4
        self.obstacles = []
        for i in range(N):
            self.new_obstacle((850 / N) * (i + 1) + 400)

        # Adiciona o chão e teto
        self.floor = AABB(bbox=(0, 800, -300, 10), mass='inf', world=self)
        self.ceiling = AABB(bbox=(0, 800, 590, 800), mass='inf', world=self)

        # Adiciona o Flappy
        self.flappy = Flappy(world=self)

    def new_obstacle(self, pos_x):
        '''Cria um novo obstáculo na posição pos_x'''

        size = 50
        speed = 50
        middle = uniform(50 + size, 550 - size)
        lower = AABB(bbox=(pos_x, pos_x + 30, 0, middle - size),
                     mass='inf', vel=(-speed, 0), world=self)
        upper = AABB(bbox=(pos_x, pos_x + 30, middle + size, 600),
                     mass='inf', vel=(-speed, 0), world=self)
        self.obstacles.append([lower, upper])

    @listen('frame-enter')
    def detect_exit(self):
        '''Detecta se um obstáculo saiu da tela e insere um novo em caso
        afirmativo'''

        L = self.obstacles
        if L[0][0].xmax < 0:
            self.remove(L[0][0])
            self.remove(L[0][1])
            del L[0]
            new_x = L[-1][0].xmin + 850 / self.N
            self.new_obstacle(new_x)

        if self.flappy.xmax < -400:
            self.game_over()

    def game_over(self):
        '''Game over'''

        self.stop()


if __name__ == '__main__':
    game = Game()
    game.run()
