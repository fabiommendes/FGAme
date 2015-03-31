# -*- coding: utf8 -*-
'''
Classes abstratas
-----------------

Todos os objetos físicos na FGAme herdam da classe Dynamic ou de uma das
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
from .dynamic_object import Dynamic
from .particle import Particle
from .rigidbody import RigidBody, LinearRigidBody
from .aabb import AABB
from .circle import Circle, Ball
from .poly import Poly, RegularPoly, Rectangle
from .forces import *
from .collision import Collision
from .collision_pairs import (get_collision, get_collision_generic,
                              CollisionError)
from .simulation import *
from . import collision_pairs as collision
from . import flags

__all__ = ['Collision', 'get_collision', 'Simulation']
