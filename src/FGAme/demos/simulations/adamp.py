from FGAme import World, RegularPoly

world = World()
p = RegularPoly(4, 100, pos=(400, 300), world=world, omega=2, adamping=0.1)
p.torque = lambda t: - p.inertia * p.theta
world.run()
