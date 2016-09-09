from FGAme import *

p = world.add.regular_poly(4, 100, pos=(400, 300), omega=2, adamping=0.1)
p.torque = lambda t: - p.inertia * p.theta
world.run()
