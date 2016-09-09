from FGAme import *

world.add.margin(10)
world.add.regular_poly(N=3, length=130, pos=(200, 300),
                       vel=(500, -10), color='random', omega=2.2)
world.add.aabb(shape=(100, 80), pos=(200, 450), color='random')
world.add.circle(40, pos=(600, 300), color='random', mass='inf')
world.add.circle(40, pos=(450, 100), color='random')
world.track.energy()
run()
