# One-liner pong: just because we can do it :)
from FGAme import *
world.add([AABB(15, 35, 240, 360, mass='inf'), AABB(765, 785, 240, 360, mass='inf'), Circle(20, pos=pos.middle, vel=(500, 300))]) or world.add.margin(-80, 10) and (on('long-press', 'w').do(lambda: world[0].move(0, 5)) and on('long-press', 's').do(lambda: world[0].move(0, -5)) and on('long-press', 'up').do(lambda: world[1].move(0, 5)) and on('long-press', 'down').do(lambda: world[1].move(0, -5))) and run()
