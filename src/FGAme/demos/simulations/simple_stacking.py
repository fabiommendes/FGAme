# -*- coding: utf8 -*-_

'''
Este exemplo demonstra o empilhamento de círculos.
'''

from FGAme import World, Circle

# Cria mundo com coeficiente de atrito global não-n'ulo
world = World(friction=0.5, gravity=300, restitution=0.0)
world.add_bounds(width=10)

N = 5
aabbs = []
for i in range(N):
    aabbs.append(Circle(25 + 5 * i,
                        pos=(400, 50 + i * 100), world=world, color='red'))
aabbs[0].make_static()
world.register_energy_tracker()
world.run()
