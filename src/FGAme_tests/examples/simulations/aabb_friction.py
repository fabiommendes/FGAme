#-*- coding: utf8 -*-_
'''
Este exemplo demonstra a resposta a colisões com atrito utilizando duas caixas 
AABB.
'''

from FGAme import World, AABB

# Cria mundo com coeficiente de atrito global não-nulo
world = World(dfriction=0.1)
world.set_bounds(width=10)

# Cria objetos
A = AABB(pos=(400, 100), shape=(50, 50), color='black')
B = AABB(pos=(250, 500), shape=(50, 50), vel=(200, -400), color='red')

# Inicia a simulação
world.add([A, B])
world.listen('key-down', 'p', world.toggle_pause)
world.run()
