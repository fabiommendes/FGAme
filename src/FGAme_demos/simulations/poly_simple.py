# -*- coding: utf8 -*-

from FGAme import *

world = World()
A = RegularPoly(N=3, length=130, color='red',
                pos=(200, 300), vel=(0, 0), omega=0.2,)
# FIXME:                name='A')
B = RegularPoly(N=5, length=100, theta=math.pi / 4,
                pos=(600, 300), vel=(20, 0),)
# FIXME:                name='B')

world.add([A, B])


@world.listen('key_down', 'space')
def pause_toggle():
    world.toggle_pause()

world.run()
