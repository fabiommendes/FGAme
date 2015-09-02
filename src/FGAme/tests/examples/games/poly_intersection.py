# -*- coding: utf8 -*-
'''
Ilustra a interseção entre duas figuras geométricas
'''

from FGAme import *
from FGAme.mathtools import clip, convex_hull

world = World()
A = Rectangle(shape=(200, 100), mass='inf')
B = RegularPoly(3, 200, pos=(70, 50), color='blue', mass='inf')
D = Poly(clip(A.vertices, B.vertices), color='red', mass='inf')
C = Circle(5, color='red')
vertices = A.vertices + B.vertices + D.vertices
conv = convex_hull(vertices)
E = Poly(conv, mass='inf', color='green')

world.add(E, layer=-1)
world.add(A)
world.add(B)
world.add(C, layer=1)
world.add(D)

for v in vertices:
    c = Circle(4, color='blue', pos=v)
    world.add(c, layer=2)

for v in conv:
    c = Circle(2, color='black', pos=v)
    world.add(c, layer=2)


world.run()
