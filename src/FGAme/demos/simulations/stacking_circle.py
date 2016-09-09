from FGAme import *

world = World(friction=0.5, gravity=300, restitution=0.0)
world.add.margin(10)

objects = []
for i in range(5):
    pos = (400, 50 + i * 100)
    objects.append(world.add.circle(25 + 5 * i, pos=pos, color='red'))
objects[0].make_static()
world.track.energy()
world.run()
