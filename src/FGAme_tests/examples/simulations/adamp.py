from FGAme import World, Poly

world = World()
p = Poly.regular(4, 100, pos=(400, 300), world=world, omega=2, adamping=0.1)
p.external_torque = lambda t: - p.inertia * p.theta
world.run()
