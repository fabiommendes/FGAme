from FGAme import *
from random import uniform

# Define constants
SPEED = 300
RADIUS = 15
PARTICLES = 50

# Fill world
world.add.margin(10)
for _ in range(PARTICLES):
    pos = Vec(uniform(30, 770), uniform(30, 570))
    vel = Vec(uniform(-SPEED, SPEED), uniform(-SPEED, SPEED))
    world.add.circle(RADIUS, vel=vel, pos=pos, color='random')

# Start simulation
world.track.energy()
run()
