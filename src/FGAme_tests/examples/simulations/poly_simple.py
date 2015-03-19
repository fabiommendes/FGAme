#-*- coding: utf8 -*-
from FGAme import *

world = World()
A = Poly.regular(N=3, length=130, color='red',
                 pos=(200, 300), vel=(200, 0),
                 name='A', omega=0.6)
B = Poly.regular(N=5, length=100, theta=pi / 4,
                 pos=(600, 300), vel=(-100, -40),
                 name='B')

world.add([A, B])

@world.listen('key_down', 'space')
def pause_toggle():
    world.toggle_pause()

world.run()
