from FGAme.physics.simulation import Simulation
from FGAme.world.world import World

def test_simulation_enforce_max_speed():
    speed = 10.0
    w = World(max_speed = speed)
    p = w.add.poly(vertices=[(0,0), (1,1), (0,2)], vel=(200, 200), pos=(0,0))
    w._simulation.enforce_max_speed()
    assert p._vel.norm_sqr() > speed ** 2

def test_simulation_gravity():
    gravity = (0, -10.0)
    w = World(gravity=gravity)
    p = w.add.regular_poly(N=6, length=2.0, pos=(0,0), mass=1.0)
    w.update(0.1)
    assert p._acceleration == gravity

def test_simulation_discard_object():
    gravity = (0, -10.0)
    w = World(gravity=gravity)
    p = w.add.regular_poly(N=6, length=2.0, pos=(0,0), mass=1.0)
    w._simulation.discard(p)
    w.update(0.1)
    assert p._acceleration != gravity
