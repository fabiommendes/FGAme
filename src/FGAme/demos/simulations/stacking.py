# -*- coding: utf8 -*-_

'''
Este exemplo demonstra a resposta a colisões com atrito utilizando duas caixas
AABB.
'''

from FGAme import World, AABB, Circle, RegularPoly, Rectangle, pi

stacks = []
stacks.append('aabbs')
stacks.append('rects')
stacks.append('circles')
stacks.append('polys')


# Cria mundo com coeficiente de atrito global não-nulo
world = World(friction=0.5, gravity=500, restitution=0.7, adamping=0.1)
world.add_bounds(width=10)

# Cria pilha de AABBs
if 'aabbs' in stacks:
    A = AABB(pos=(100, 70), shape=(100, 50), color='red', mass='inf')
    B = AABB(pos=(125, 150), shape=(50, 50))
    C = AABB(pos=(125, 250), shape=(70, 50))
    D = AABB(pos=(125, 300), shape=(100, 20))
    aabbs = [B, C, D]
    world.add([A, B, C, D])

# Cria pilha de Retângulos
if 'rects' in stacks:
    A = Rectangle(pos=(100, 370), shape=(100, 50), color='red', mass='inf')
    B = Rectangle(pos=(125, 450), shape=(50, 50))
    C = Rectangle(pos=(125, 510), shape=(70, 50))
    D = Rectangle(pos=(125, 550), shape=(100, 20))
    world.add([A, B, C, D])


# Cria pilha de círculos
if 'circles' in stacks:
    A = Circle(50, (250, 100), mass='inf', color='red')
    B = Circle(25, (320, 70), mass='inf', color='red')
    C = Circle(25, (380, 70), mass='inf', color='red')
    D = Circle(50, (450, 100), mass='inf', color='red')
    world.add([A, B, C, D])
    for i in range(11):
        c1 = Circle(8, pos=(300 + i * 10, 500 - i * 10))
        c2 = Circle(8, pos=(300 + i * 10, 200 + i * 10))
        world.add([c1, c2])

# Cria pilha de triângulos
if 'polys' in stacks:
    A = RegularPoly(3, 150, pos=(550, 70), theta=-pi / 6, mass='inf',
                    color='red')
    B = RegularPoly(3, 150, pos=(700, 70), theta=-pi / 6, mass='inf',
                    color='red')
    world.add([A, B])
    for i in range(10):
        o1 = RegularPoly(3, 20, pos=(550 + i * 12, 550 - i * 15))
        o2 = Rectangle(shape=(12, 12), pos=(550 + i * 10, 200 + i * 10))
        world.add([o1, o2])


#@world.listen('frame-enter')
# def show_vels():
#    print('1) %7.1f, 2) %7.1f, 3) %7.1f' % tuple(obj.vel.y for obj in aabbs))


# Inicia a simulação
world.run()
