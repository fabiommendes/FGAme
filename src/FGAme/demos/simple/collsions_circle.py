from FGAme import *

world.add.margin(10)
world.add.circle(50, pos=(200, 330), vel=(300, 0), color='random')
world.add.circle(60, pos=(200, 450), color='random')
world.add.circle(30, pos=(600, 300), color='random', mass='inf')
world.add.aabb(120, 220, 120, 220, color='random', mass='inf')
world.track.energy()
run()
