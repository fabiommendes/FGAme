# -*- coding: utf8 -*-_

'''
Este exemplo demonstra a resposta a colisões com atrito utilizando duas caixas
AABB.
'''

from FGAme import World, AABB


# Cria mundo com coeficiente de atrito global não-nulo
world = World(dfriction=0.1)
world.add_bounds(width=10)

# Cria objetos
A = AABB(pos=(400, 100), shape=(50, 50), color='black')
B = AABB(pos=(150, 500), shape=(50, 50), vel=(200, -400), color='red')
C = AABB(pos=(300, 500), shape=(50, 50), vel=(200, -400), color='red')
D = AABB(pos=(150, 100), shape=(50, 50), vel=(200, -400), color='red')


@world.listen('key-down', 'space')
def pause():
    print(B.bbox, '\n', A.bbox, '\n')
    world.toggle_pause()


@world.listen('long-press', 'right')
def right():
    A.vel += (10, 0)


@world.listen('long-press', 'left')
def left():
    A.vel += (-10, 0)


@world.listen('long-press', 'up')
def up():
    A.vel += (0, 10)


@world.listen('long-press', 'down')
def down():
    A.vel += (0, -10)


# Inicia a simulação
world.add([A, B, C, D])
world.run()
