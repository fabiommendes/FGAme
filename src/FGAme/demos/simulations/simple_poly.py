from FGAme import *

world.add.margin(10)
world.add.regular_poly(N=3, length=130, pos=(200, 300),
                       vel=(200, 200), color='random', omega=2.2)
world.add.regular_poly(N=5, length=100, pos=(200, 450), theta=pi / 4,
                       color='random')
world.add.regular_poly(N=3, length=100, pos=(600, 300), theta=pi / 4,
                       color='random', mass='inf')
world.track.energy()
run()
