from FGAme import *

world = World(friction=0.5, gravity=500, restitution=0.7, adamping=0.1)
world.add.margin(10)

# Which classes of objects do you want to simulate?
stack_aabbs = True
stack_circles = True
stack_rectangles = False
stack_triangles = False

# Stack of AABBs
if stack_aabbs:
    world.add.aabb(pos=(100, 70), shape=(100, 50), color='red', mass='inf')
    world.add.aabb(pos=(125, 150), shape=(50, 50))
    world.add.aabb(pos=(125, 250), shape=(70, 50))
    world.add.aabb(pos=(125, 300), shape=(100, 20))

# Stack of rectangles
if stack_rectangles:
    world.add.rectangle(pos=(100, 370), shape=(100, 50), color='red', mass='inf')
    world.add.rectangle(pos=(125, 450), shape=(50, 50))
    world.add.rectangle(pos=(125, 510), shape=(70, 50))
    world.add.rectangle(pos=(125, 550), shape=(100, 20))

# Stack of circles
if stack_circles:
    world.add.circle(50, (250, 100), mass='inf', color='red')
    world.add.circle(25, (320, 70), mass='inf', color='red')
    world.add.circle(25, (380, 70), mass='inf', color='red')
    world.add.circle(50, (450, 100), mass='inf', color='red')
    for i in range(11):
        world.add.circle(8, pos=(300 + i * 10, 500 - i * 10))
        world.add.circle(8, pos=(300 + i * 10, 200 + i * 10))

# Stack of triangles
if stack_triangles:
    world.add.regular_poly(3, 150, pos=(550, 70), theta=-pi / 6, mass='inf', color='red')
    world.add.regular_poly(3, 150, pos=(700, 70), theta=-pi / 6, mass='inf', color='red')
    for i in range(10):
        world.add.regular_poly(3, 20, pos=(550 + i * 12, 550 - i * 15))
        world.add.rectangle(shape=(12, 12), pos=(550 + i * 10, 200 + i * 10))

# Start simulation
world.run()
