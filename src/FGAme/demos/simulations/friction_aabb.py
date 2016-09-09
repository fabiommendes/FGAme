from FGAme import *


pos = pos.middle - (300, 150)
world = World(friction=0.1, restitution=1, gravity=0)
world.add.margin(10)
world.add.aabb(pos=pos, vel=(270, 370), shape=(50, 50), color='random')
world.track.energy()
run()
