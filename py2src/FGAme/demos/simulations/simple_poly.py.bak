# -*- coding: utf8 -*-
from FGAme import *


# Cria mundo e objetos
world = World(restitution=1)
world.add_bounds(width=10, use_poly=True)
obj1 = RegularPoly(N=3, length=130, pos=(200, 300),
                   vel=(200, 200), color='random', omega=2.2)
obj2 = RegularPoly(N=5, length=100, pos=(200, 450), theta=pi / 4,
                   color='random')
obj3 = RegularPoly(N=3, length=100, pos=(600, 300), theta=pi / 4,
                   color='random', mass='inf')

# Insere objetos e inicia rastreio de energia
world.register_energy_tracker()
world.add([obj1, obj2, obj3])
world.run()
