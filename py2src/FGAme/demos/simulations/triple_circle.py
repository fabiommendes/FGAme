# -*- coding: utf8 -*-
from FGAme import *

# Cria mundo e objetos
world = World()
world.add_bounds(width=10)
c1 = Circle(50, pos=(50, 300), vel=(800, 0), color='random')
c2 = Circle(30, pos=(420, 320), color='random')
c3 = Circle(30, pos=(420, 280), color='random')

# Insere objetos e inicia rastreio de energia
world.register_energy_tracker()
world.add([c1, c2, c3])
world.run()
