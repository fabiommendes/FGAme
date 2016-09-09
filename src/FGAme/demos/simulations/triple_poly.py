from FGAme import *

world.add.margin(10)
world.add.regular_poly(5, length=50, pos=(50, 300), vel=(800, 0))
world.add.regular_poly(5, length=30, pos=(420, 320))
world.add.regular_poly(5, length=30, pos=(420, 280))
world.track.energy()
world.run()
