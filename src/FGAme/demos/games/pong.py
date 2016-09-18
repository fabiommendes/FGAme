from FGAme import *

world.add.margin(-300, 10)
ball = world.add.circle(20, pos=pos.middle, vel=vel.random(), mass=0.1)
p1 = world.add.aabb(10, 30, 250, 350, damping=2)
p2 = world.add.aabb(770, 790, 250, 350, damping=2)


@listen('long-press', 'w', direction=1, player=p1)
@listen('long-press', 's', direction=-1, player=p1)
@listen('long-press', 'up', direction=1, player=p2)
@listen('long-press', 'down', direction=-1, player=p2)
def set_speed(player, direction):
    player.vy = direction * vel.speed_fair

run()

