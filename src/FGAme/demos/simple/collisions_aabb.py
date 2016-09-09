from FGAme import *

world.add.margin(10)
world.add.aabb(shape=(120, 90), pos=(200, 330), vel=(300, 200), color='random')
world.add.aabb(shape=(60, 60), pos=(200, 450), color='random')
world.add.aabb(shape=(110, 140), pos=(600, 300), color='random', mass='inf')
world.track.energy()
run()
