# -*- coding: utf8 -*-

from FGAme.core.env import env
from FGAme.core.logger import *
from FGAme.core.screen import *
from FGAme.core.image import *

###############################################################################
#                     Interface de inicialização
###############################################################################

from FGAme.core.init import Control as _Control
conf = _Control()
init = conf.init
init_canvas = conf.init_canvas
init_input = conf.init_input
