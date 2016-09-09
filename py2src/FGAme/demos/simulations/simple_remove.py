# -*- coding: utf8 -*-
from __future__ import division
from FGAme import *


# Create world and objects
world = World(restitution=1)
world.add_bounds(width=10, use_poly=True)
obj1 = RegularPoly(N=3, length=130, pos=(200, 300),
                   vel=(500, 500), color='random', omega=2.2)
obj2 = RegularPoly(N=5, length=100, pos=(200, 450), theta=pi / 4,
                   color='random')
obj3 = RegularPoly(N=3, length=100, pos=(600, 300), theta=pi / 4,
                   color='random', mass='inf')

# Remove object after collision between obj2 and obj3
@obj3.listen('pre-collision')
def on_collision(col):
    if obj2 in col:
        col.cancel()
        obj3.destroy()

# Insert objects
world.add([obj1, obj2, obj3])
world.run()
