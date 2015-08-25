from FGAme import World, RegularPoly, draw

world = World()
p = RegularPoly(4, 100, pos=(400, 300), world=world, omega=2, adamping=0.1)
a = draw.Image('gaussiana.png', pos=(400, 300))
world.add(a, layer=-1)
p.torque = lambda t: - p.inertia * p.theta
world.run()
