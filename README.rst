.. image:: https://travis-ci.org/fabiommendes/FGAme.svg?branch=master
    :target: https://travis-ci.org/fabiommendes/FGAme

.. image:: https://coveralls.io/repos/github/fabiommendes/FGAme/badge.svg?branch=master
    :target: https://coveralls.io/github/fabiommendes/FGAme?branch=master


FGAme is a physics-based game engine for Python 3. Its aims to avoid boilerplate
and to be so easy that even a child can play with it (and learn how to program
with it!). Check this pong implementation::

    from FGAme import *
    
    # A 10px margin to keep things on the screen
    world.add.margin(10)
    
    # Create a ball in the middle of the screen. We also add some random speed
    ball = world.add.circle(20, pos=pos.middle, color='red') 
    ball.vel = vel.random()
    
    # Create both players as AABBs (axis aligned bounding boxes). Infinite 
    # masses prevent them from moving when hit by the ball
    p1 = world.add.aabb(shape=(20, 120), pos=(30, 300), mass='inf')
    p2 = world.add.aabb(shape=(20, 120), pos=(30, 300), mass='inf')
    
    # Connect long press events with the correct functions
    on('long-press', 'w').do(p1.move, 0, 5)
    on('long-press', 's').do(p1.move, 0, -5)
    on('long-press', 'up').do(p2.move, 0, 5)
    on('long-press', 'down').do(p2.move, 0, -5)
    
    # Start main loop
    run()

FGAme currently requires Pygame to run. We have plans to make it backend 
agnostic and in the future it will support SDL2, Kivy, Qt and maybe others. 
