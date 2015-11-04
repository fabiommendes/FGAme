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

from .meta import __version__, __author__
from .draw import Color
from .logger import *
from .events import listen, signal, EventDispatcher
from .input import *
from .mainloop import *
from .mathtools import Vec, pi, asvector
from .physics import *
from .world import World
from .objects import *
from .app import *
from .extra.orientation_objects import *
from . import conf
from . import mathtools as math
from . import draw
from . import physics


if __name__ == '__main__':
    import doctest
    doctest.testmod()
