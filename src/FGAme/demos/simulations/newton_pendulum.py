# -*- coding: utf8 -*-_

'''
Este exemplo demonstra a resposta a colisões com atrito utilizando duas caixas
AABB.
'''

from FGAme import World, AABB, Circle, Rectangle

# Cria mundo com coeficiente de atrito global não-nulo
world = World()
world.add_bounds(width=10)

stacks = []
stacks.append('aabbs')
stacks.append('circles')
stacks.append('rects')


# Cria pilha de AABBs
H = 550
dH = 200
if 'aabbs' in stacks:
    world.add(AABB(pos=(50, H), shape=(40, 40), color='red', vel=(200, 0)))
    for i in range(10):
        world.add(AABB(pos=(150 + i * 50, H), shape=(40, 40)))
    world.add(AABB(pos=(150 + 10 * 50, H), shape=(40, 40), color='red'))
    world.add(AABB(pos=(50, H - 50),
                   shape=(40, 40), color='red', vel=(200, 0)))
    H -= dH

# Cria pilha de círculos
if 'circles' in stacks:
    world.add(Circle(20, pos=(50, H), color='red', vel=(200, 0)))
    for i in range(10):
        world.add(Circle(20, pos=(150 + i * 50, H)))
    world.add(Circle(20, pos=(150 + 10 * 50, H), color='red'))
    world.add(Circle(20, pos=(50, H - 50), color='red', vel=(200, 0)))
    H -= dH

# Cria pilha de retangulos
if 'rects' in stacks:
    world.add(Rectangle(pos=(50, H), shape=(40, 40), color='red',
                        vel=(200, 0)))
    for i in range(10):
        world.add(Rectangle(pos=(150 + i * 50, H), shape=(40, 40)))
    world.add(Rectangle(pos=(150 + 10 * 50, H), shape=(40, 40), color='red'))
    world.add(Rectangle(pos=(50, H - 50),
                        shape=(40, 40), color='red', vel=(200, 0)))


#world.add(Circle(10, pos=(30, 30), vel=(300, 400)))
#world.add(Circle(10, pos=(30, 30), vel=(400, 300)))

# Registra energias
world.register_energy_tracker()

# Inicia a simulação
world.run()
