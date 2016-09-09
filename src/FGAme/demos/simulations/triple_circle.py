from FGAme import *

world.add.margin(10)
world.add.circle(50, pos=(50, 300), vel=(800, 0), color='random')
world.add.circle(30, pos=(420, 320), color='random')
world.add.circle(30, pos=(420, 280), color='random')
world.track.energy()
run()
