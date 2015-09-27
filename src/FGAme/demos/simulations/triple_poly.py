# -*- coding: utf8 -*-
from FGAme import *

# Cria mundo e objetos
world = World()
world.add_bounds(width=10, use_poly=True)
p1 = RegularPoly(5, length=50, pos=(50, 300), vel=(800, 0))
p2 = RegularPoly(5, length=30, pos=(420, 320))
p3 = RegularPoly(5, length=30, pos=(420, 280))

# Insere objetos e inicia rastreio de energia
world.register_energy_tracker()
world.add([p1, p2, p3])
world.run()
