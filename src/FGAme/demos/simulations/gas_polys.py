# -*- coding: utf8 -*-
'''
Semelhante ao gas_aabbs.py, mas desta vez utiliza objetos da classe Poly.
'''
from FGAme import *
from random import uniform

# Constantes da simulação
SPEED = 300
SHAPE = (30, 30)
NUM_POLYS = 50

# Inicializa o mundo
world = World()
world.add_bounds(width=10)

# Preenche o mundo
for _ in range(NUM_POLYS):
    pos = Vec2(uniform(30, 770), uniform(30, 570))
    vel = Vec2(uniform(-SPEED, SPEED), uniform(-SPEED, SPEED))
    obj = Rectangle(shape=SHAPE, vel=vel, pos=pos, color=(200, 0, 0))
    world.add(obj)

# Inicia a simulação
world.register_energy_tracker()
world.run()
