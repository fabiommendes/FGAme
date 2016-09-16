from FGAme import *

world.add.margin(-50, 10)
ball = world.add.circle(20, pos=pos.middle, vel=vel.random(), mass=10, color='red')
p1 = world.add.aabb(10, 30, 250, 350, damping=2, mass=40)
p2 = world.add.aabb(770, 790, 250, 350, damping=2, mass=40)

for _ in range(20):
    world.add.circle(10, pos=pos.random(), color='grey', mass=5, damping=0.1)


@listen('long-press', 'w', direction=1, player=p1)
@listen('long-press', 's', direction=-1, player=p1)
@listen('long-press', 'up', direction=1, player=p2)
@listen('long-press', 'down', direction=-1, player=p2)
def set_speed(player, direction):
    player.vy = direction * vel.speed_fair


def update():
    if ball.speed < 400:
        ball.speed += 5
    p1.vx = p2.vy = 0
    p1.x = 20
    p2.x = 780

run()
