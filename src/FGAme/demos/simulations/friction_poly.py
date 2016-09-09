from FGAme import World, listen, pos
from random import uniform

world = World(friction=0.2, restitution=0.9, gravity=0)
world.add.margin(10)
world.add.rectangle(
    pos=pos.middle - (300, +150),
    vel=(270, 420 + uniform(0, 200)),
    shape=(50, 50),
    theta=0.2,
    color='random',
)

listen('key-down', 'space', world.toggle_pause)
world.track.energy()
world.run()
