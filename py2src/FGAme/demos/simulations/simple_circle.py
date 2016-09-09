# -*- coding: utf8 -*-
from FGAme import *


# Cria mundo e objetos
world = World()
world.add_bounds(width=10)
obj1 = Circle(50, pos=(200, 330), vel=(300, 0), color='random')
obj2 = Circle(60, pos=(200, 450), color='random')
obj3 = Circle(30, pos=(600, 300), color='random', mass='inf')

# Insere objetos e inicia rastreio de energia
world.register_energy_tracker()
world.add([obj1, obj2, obj3])
world.run()
