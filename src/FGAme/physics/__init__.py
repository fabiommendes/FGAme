#-*- coding: utf8 -*-
'''
Classes abstratas
-----------------

Todos os objetos físicos na FGAme herdam da classe Object ou de uma das
subclasses derivadas aqui. Não é possível instanciar estas classes diretamente,
mas elas são a base para todos os tipos de objetos utilizados na FGAme.

.. automodule:: FGAme.objects.base

Classes derivadas
-----------------

#.. autoclass:: FGAme.AABB
#.. autoclass:: FGAme.Circle
#.. autoclass:: FGAme.Poly
#.. autoclass:: FGAme.Letter

Funções especiais para a criação de objetos
--------------------------------------------

#.. automodule :: FGAme.letters

'''

from .flags import *
from .obj_all import Dynamic, Particle, RigidBody, LinearRigidBody
from .obj_all import AABB, Circle, Ball
from .obj_all import Poly, RegularPoly, Rectangle
from .forces import *
from .collision_base import *
from .simulation import *
from . import collision_pairwise as col_pairs
from . import flags

__all__ = ['Collision', 'get_collision', 'Simulation']
