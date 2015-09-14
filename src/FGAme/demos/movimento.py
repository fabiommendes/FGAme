from FGAme import World, Circle, AABB, pos, conf, on_key_down
import random
conf.set_framerate(60)


def random_color():
    return random.choice(['black', 'red', 'green', 'blue'])
    return [int(random.random() * 255) for _ in range(3)]

world = World()
circle_list = []
for _ in range(5):
    color = random_color()
    circle = Circle(50, pos=pos.middle, world=world, color=color)
    circle_list.append(circle)

o1 = AABB(pos=pos.middle, shape=(80, 71))
o2 = AABB(pos=pos.middle, shape=(80, 71), image='alien1')
world.add(o1)
world.add(o2, layer=2)


@world.listen('frame-enter')
def frame_enter_handler():
    for circle in circle_list:
        x = random.random() * 800
        y = random.random() * 600
        circle.pos = x, y


@on_key_down('space')
def space():
    world.toggle_pause()

world.run()
