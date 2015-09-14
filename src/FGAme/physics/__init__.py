# -*- coding: utf8 -*-
'''
Classes abstratas
-----------------

Todos os objetos físicos na FGAme herdam da classe Dynamic ou de uma das
subclasses derivadas aqui. Não é possível instanciar estas classes diretamente,
mas elas são a base para todos os tipos de objetos utilizados na FGAme.

.. automodule:: FGAme.objects2.base

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

from FGAme.physics.flags import *
from FGAme.physics.bodies import *
from FGAme.physics import flags
from FGAme.physics.collision import Collision, CBBContact, AABBContact
from FGAme.physics.collision_pairs import (get_collision,
                                           get_collision_generic,
                                           CollisionError)
from FGAme.physics import collision_pairs as collision
from FGAme.physics.forces import *
from FGAme.physics.simulation import *


__all__ = ['Collision', 'get_collision', 'Simulation']
