from FGAme import *
from FGAme.actions import *

world = World(gravity=800, restitution=0.3, friction=0.8, damping=0.8)
mario = AABB(shape=(50, 100), pos=(325, 150), color='red')
turtle = AABB(shape=(50, 50), pos=(725, 125), color='green')
ground = AABB(shape=(1000, 100), pos=(400, 50), mass='inf')
world.add([mario, ground, turtle])

turtle.damping = 0
turtle.dfriction = 0
turtle.sfriction = 0

action = loop(
    set_velocity(-300, 0) >> delay(0.7)
    >> set_velocity(300, 0) >> delay(0.7)
)
action.start(turtle)


px = 350
jump_vy = 600


@on_key_down('space')
def jump():
    mario.vel += (0, jump_vy)


@on_long_press('left')
def left():
    mario.vel = (-px, mario.vel.y)


@on_long_press('right')
def right():
    mario.vel = (px, mario.vel.y)


@mario.listen('collision')
def on_collision(col):
    A, B = col

world.run()
