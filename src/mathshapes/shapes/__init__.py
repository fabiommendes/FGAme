'''
==================
Geometrical shapes
==================

The mathshapes.shape module define classes for various geometric primitives
such as points, lines, circles, polygons, etc. All these objects define some
common mathematical operations such as containment and distance FGAme_tests,
projections, and superposition calculations via SAT.


Mutable vs immutable
====================

Most objects have both an immutable and a mutable implementation with a
similar API. Mutable objects should be used when the geometric object
represents some fixed identity (e.g., a circle in a scene that can move and
change is geometric properties). All other sittuations should use immutable
types, (e.g.: check if to circles of given radius and positions intercept or
not).
'''
from mathshapes import *
from mathshapes import *
from mathshapes import *
from mathshapes import *
from mathshapes import *
