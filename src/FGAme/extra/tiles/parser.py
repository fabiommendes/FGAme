'''

Especificação de tilesets
=========================

...


::

    conf:
        origin: 0, 0
        shape: 50, 50
        background-color: #99f

    tile "brick":
        char: "x"
        color: red
        image: tiles/brick.png

    tile "coin":
        char: "o"
        shape: circle
        color: #ff0

    tile "spike":
        char: "i"
        image: tiles/spike.png

    data "main":
        |             oo
        |        oo     xxxxxxxxxxxxxxxxxx
        |           xxx
        |       xxx
        |                                        ii
        |xxxxxxxxxxxxxxxxxxxxxxxxxxxxx    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        |xxxxxxxxxxxxxxxxxxxxxxxxxxxxxiiiixxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

'''
