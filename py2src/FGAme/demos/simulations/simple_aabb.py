# -*- coding: utf8 -*-
from FGAme import *


# Cria mundo e objetos
world = World()
world.add_bounds(width=10)
obj1 = AABB(shape=(120, 90), pos=(200, 330), vel=(300, 200), color='random')
obj2 = AABB(shape=(60, 60), pos=(200, 450), color='random')
obj3 = AABB(shape=(110, 140), pos=(600, 300), color='random', mass='inf')

# Insere objetos e inicia rastreio de energia
world.register_energy_tracker()
world.add([obj1, obj2, obj3])
world.run()
