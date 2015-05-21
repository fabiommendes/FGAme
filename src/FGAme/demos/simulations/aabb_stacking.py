# -*- coding: utf8 -*-_

'''
Este exemplo demonstra a resposta a colisões com atrito utilizando duas caixas
AABB.
'''

from FGAme import World, AABB

# Cria mundo com coeficiente de atrito global não-nulo
world = World(dfriction=0.5, gravity=200, restitution=0.5)
world.add_bounds(width=10)

N = 5
for i in range(N):
    AABB(shape=(50 + 10 * i, 50), pos=(400, 50 + i * 60), world=world,
         color='red')

# Inicia a simulação
world.run()
