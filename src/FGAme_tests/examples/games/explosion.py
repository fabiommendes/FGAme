#-*- coding: utf8 -*-
from __future__ import print_function

from FGAme import *
from random import uniform, choice
from FGAme.effects import explode

print('Starting simulation...')
random_color = lambda: (255, 0, 0)
world = World()

obj1 = Poly.regular(N=8, length=100, pos=(-100, -100), vel=(100, 100),
                    omega=1, color=random_color())
obj1.mass = 100
world.add(obj1)

obj2 = Poly.regular(N=4, length=50, pos=(200, 200), vel=(-100, -100),
                    omega=-uniform(0, 4), color=random_color())
obj2.mass = 100
world.add(obj2)

aabb = AABB(bbox=(-100, 400, -300, -200), color='black', mass='inf')
world.add(aabb)

aabb2 = AABB(bbox=(300, 380, -150, 280), color='black', mass='inf')
world.add(aabb2)

obj3 = Poly.regular(N=5, length=150, pos=(-300, 200), vel=(-100, -100),
                   omega=-uniform(0, 4), color=random_color())
obj3.mass = 100
obj3.make_static()
world.add(obj3)

explode(obj1, world, energy=obj1.mass * 100 ** 2, prob_rec=1)

def pause():
    obj1.pause()
    obj2.pause()

def unpause():
    obj1.unpause()
    obj2.unpause()

# Inicia a simulação
world.run()
