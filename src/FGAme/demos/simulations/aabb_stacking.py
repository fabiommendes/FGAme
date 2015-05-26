# -*- coding: utf8 -*-_

'''
Este exemplo demonstra a resposta a colisões com atrito utilizando duas caixas
AABB.
'''

from FGAme import World, Circle

# Cria mundo com coeficiente de atrito global não-n'ulo
world = World(dfriction=0.5, gravity=300, restitution=0.0)
world.add_bounds(width=10)

N = 5
aabbs = []
for i in range(N):
    aabbs.append(Circle(25 + 5 * i,
                        pos=(400, 50 + i * 100), world=world, color='red'))
aabbs[0].make_static()
#aabbs[0].boost((0, 700))

#@world.listen('frame-enter')
# def print_vels():
#    meansqr = sum(x.vel.y ** 2 for x in aabbs) ** 0.5
# print('  vels: (%5.3f)' % meansqr +
#      '; '.join(['%5.3f' % x.vel.y for x in aabbs]))

# print('  pos: ' +
#      '; '.join(['%5.3f' % x.pos.y for x in aabbs]))

world.register_energy_tracker()
# Inicia a simulação
world.run()
