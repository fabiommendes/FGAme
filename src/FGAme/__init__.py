# -*- coding: utf8 -*-
'''
Módulos da FGAme
================

Configuração (FGAme.conf)
-------------------------

.. automodule:: FGAme.conf
    :members:
    :member-order: bysource

Objetos e mundo
---------------


Física e colisões
-----------------


Funções matemáticas
-------------------


Tópicos avançados
=================

Eventos
-------

.. automodule:: FGAme.events
    :members: EventDispatcher, signal, listen


Anatomia de uma colisão
-----------------------

Loop principal
--------------

'''

from FGAme.meta import __version__, __author__
from FGAme import conf
from FGAme import mathtools as math
from FGAme.input import *
from FGAme.mathtools import Vec, pi, asvector
from FGAme import draw
from FGAme.events import listen, signal, EventDispatcher
from FGAme.core import *
from FGAme import physics
from FGAme.physics import *
from FGAme.world import World
from FGAme.objects import *
from FGAme.app import *
from FGAme.extra.orientation_objects import *
from FGAme.mainloop import *
del MainLoop

if __name__ == '__main__':
    import doctest
    doctest.testmod()
