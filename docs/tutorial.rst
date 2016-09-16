==============
Quick tutorial
==============

FGAme is a physics oriented game engine oriented to ease to use and useful in
an educational setting. Hence, don't expect blazing fast simulation and cutting
edge graphics. For those simple 2D games, however, we can have a lot of fun!

In the dynamic spirit of Python, we can use FGAme both as a script or in
interactive mode. Of course, the interactive shell is only useful for quick
experimentation so don't expect to create complex games with it. You can also
use it for debugging, by initializing your game in the interactive mode so it
is possible to interact with any object created in game.

Pong
====

Let's create a functional Pong example with FGAme. Open an interactive shell
(such as IPython/Jupyter or Python itself). Just click in the shell icon or
type in the command line::

    $ ipython

 Now let's start programming!

The first step is to import all symbols used by FGAme. We start the interactive
mode calling the start() function.

>>> from FGAme import *
>>> start()                                                      #doctest: +SKIP

You will see that a blank window will open: this is already our game running. We
can add objects in the screen using the ``world`` object and its ``add```
attribute.

>>> ball = world.add.circle(20, pos=pos.middle, color='red')

The command above creates a circle which is immediately shown on screen. Notice
that we have defined a few parameters of the circle: the first argument is its
radius measured in pixels. ``pos`` controls its position and is a vector of
its coordinates, we used the pos.middle constant to choose the coordinates of
the middle of the screen. Finally, the color parameter controls the circle color
and can be either a name string, a tuple of RGB coordinates or even HTML hex
values (e.g.: ``'#FF0000'``).

Now lets make the ball move:

>>> ball.vel = (50, -20)

You will notice that it will start to slowly move downwards to the right.
Velocity is measured in pixels per second and we can control it by setting
either a vector value or controlling each coordinate.

>>> ball.vx = -50

As you read this, the ball may already had left the screen. Let us fence by
creating a margin around the screen that objects cannot pass:

>>> world.add.margin(10)                                     #doctest: +ELLIPSIS
(...)

You will see that a margin of 10px appeared around the screen.

Maybe it is necessary to put your ball back in sight, by placing it again in
the middle of the screen

>>> ball.pos = pos.middle

The next step is to create the paddles to interact with the ball. Let us call
them ``player1`` and ``player2``

>>> player1 = world.add.aabb(pos=(30, 300), shape=(20, 120))
>>> player2 = world.add.aabb(pos=(770, 300), shape=(20, 120))

The AABB stands for axis-aligned bounding box. It is a rectangle that aways
keeps its orientation aligned with the x and y axis. We created it by setting
the position of the center point and a ``shape`` tuple with its width and
height.

If you wait long enough, the ball will probably hit one of the paddles and you
will notice that it respond to collisions. Of course, it is not the way it
should work: the paddle is free to move in all directions.

We can fix this by giving a very large mass to each player as heavier objects
are least affected by collisions. Mass is measured with the same scale as area,
which in our world is pixel squared. Hence our 20x120 square has a mass of
2400. We can make it much larger

>>> player1.mass = player2.mass = 10000

If you wait a few collisions, you will notice that now the paddles move much
less after each collision. But they still move. We can fix this by setting the
mass to infinite, as an object with infinite mass is not affected at all by
finite forces

>>> player1.mass = player2.mass = 'inf'

Now that the mass is infinite, both objects pass through the walls! The reason
is that the margin is formed by objects with infinite mass. We cannot compute
the forces in this case because the collisions of two such objects creates
infinitely large forces that affect objects with infinitely large masses.
If we remember that accelerations are forces divided by mass, we get to
infinity divided by infinity. In mathematical terms: boom! FGAme simply ignore
collisions of such objects since there is no other sane thing to do.

Let us adjust the positions and velocities of both player objects and start
again

>>> player1.vel = player2.vel = (0, 0)
>>> player1.pos = (30, 300)
>>> player2.pos = (770, 300)

The next step is to add user interaction. The way it works in FGAme is by
creating functions that are executed when specific events occur. In our case,
we want a function that moves each player slightly up or down while the correct
keys are being pressed. We can do that by calling the ``.move()`` function of
each player:

>>> # this will move player1 50px up
>>> player1.move(0, 50)                                          #doctest: +SKIP

We can bind the move function to the event "key is being pressed" using the
``listen`` function. The event we want to try first "long-press" of the "w" key:
every frame that this event is triggered, we want to call the ``player1.move``
with the arguments (0, 4) to move it 4px up. This is done with this command:

>>> listen('long-press', 'w', function=player1.move, args=(0, 4))     #doctest: +ELLIPSIS
move(...)

We now adjust the same command for the other keys:

>>> listen('long-press', 's', function=player1.move, args=(0, -4))    #doctest: +ELLIPSIS
move(...)
>>> listen('long-press', 'up', function=player2.move, args=(0, 4))    #doctest: +ELLIPSIS
move(...)
>>> listen('long-press', 'down', function=player2.move, args=(0, -4)) #doctest: +ELLIPSIS
move(...)

Now we have a functional Pong game! Let us give a nice hit to the red ball
and start playing.

>>> ball.pos = pos.middle; ball.vel = vel.random()

Have fun!
