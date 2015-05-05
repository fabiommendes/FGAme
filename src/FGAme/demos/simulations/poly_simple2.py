# -*- coding: utf8 -*-

from FGAme import *
from random import uniform


def random_color():
    return tuple(int(uniform(0, 255)) for _ in range(3))

# Cria mundo e objetos
world = World()

obj1 = RegularPoly(N=3, length=130, pos=(200, 300),
                   vel=(300, 0), color=random_color(), omega=2.2)
obj2 = RegularPoly(N=5, length=100, pos=(200, 450), theta=pi / 4,
                   color=random_color())
obj3 = RegularPoly(N=3, length=100, pos=(600, 300), theta=pi / 4,
                   color=random_color())
obj3.make_static()

# Cria bordas e insere objetos no mundo antes de iniciar a simulação
world.register_energy_tracker()
world.add_bounds(width=10)
world.add([obj1, obj2, obj3])
world.run()
