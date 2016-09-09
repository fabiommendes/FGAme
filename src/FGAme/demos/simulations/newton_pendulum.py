from FGAme import *

world.add.margin(10)
stack_aabb = True
stack_circle = True
stack_rectangles = True

# Stack of AABBs
H = 550
dH = 200
if stack_aabb:
    world.add.aabb(pos=(50, H), shape=(40, 40), color='red', vel=(200, 0))
    for i in range(10):
        world.add.aabb(pos=(150 + i * 50, H), shape=(40, 40))
    world.add.aabb(pos=(150 + 10 * 50, H), shape=(40, 40), color='red')
    world.add.aabb(pos=(50, H - 70), shape=(40, 40), color='red', vel=(200, 0))
    H -= dH

# Stack of Circles
if stack_circle:
    world.add.circle(20, pos=(50, H), color='red', vel=(200, 0))
    for i in range(10):
        world.add.circle(20, pos=(150 + i * 50, H))
    world.add.circle(20, pos=(150 + 10 * 50, H), color='red')
    world.add.circle(20, pos=(50, H - 70), color='red', vel=(200, 0))
    H -= dH

# Stack of rectangles
if stack_rectangles:
    world.add.rectangle(pos=(50, H), shape=(40, 40), color='red', vel=(200, 0))
    for i in range(10):
        world.add.rectangle(pos=(150 + i * 50, H), shape=(40, 40))
    world.add.rectangle(pos=(150 + 10 * 50, H), shape=(40, 40), color='red')
    world.add.rectangle(pos=(50, H - 70), shape=(40, 40), color='red', vel=(200, 0))

# Track energy and run
world.track.energy()
run()
