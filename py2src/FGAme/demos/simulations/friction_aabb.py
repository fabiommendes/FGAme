# -*- coding: utf8 -*-
from FGAme import World, AABB, pos

world = World(friction=0.1, restitution=1, gravity=0)
world.add_bounds(width=10)
world.add(
    AABB(
        pos=pos.middle - (300, +150),
        vel=(270, 370), 
        shape=(50, 50), 
        color='random',
    )
)

world.register_energy_tracker()
world.run()
