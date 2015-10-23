from FGAme import World, Rectangle, pos
from random import uniform

world = World(friction=0.2, restitution=0.9, gravity=0)
world.add_bounds(width=10)
world.add(
    Rectangle(
        pos=pos.middle - (300, +150),
        vel=(270, 420 + uniform(0, 200)), 
        shape=(50, 50),
        theta=0.2, 
        color='random',
    )
)

world.listen('key-down', 'space', world.toggle_pause)
world.register_energy_tracker()
world.run()
