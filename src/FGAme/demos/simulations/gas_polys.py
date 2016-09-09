from FGAme import *
from random import uniform

SPEED = 300
SHAPE = (30, 30)
NUM_POLYS = 50

# Populate world
world.add.margin(10)
for _ in range(NUM_POLYS):
    density = uniform(0.8, 1)
    pos = Vec(uniform(30, 770), uniform(30, 570))
    vel = Vec(uniform(-SPEED, SPEED), uniform(-SPEED, SPEED))
    world.add.rectangle(
        shape=SHAPE, 
        vel=vel, 
        pos=pos,
        density=density,
        color=(255 * density**2, 0, 0)
    )

# Simulate!
world.track.energy()
run()
