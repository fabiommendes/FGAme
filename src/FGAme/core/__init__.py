from FGAme.core.env import env
from FGAme.core.logger import *
from FGAme.core.events import *
from FGAme.core.input import *
from FGAme.core.screen import *
from FGAme.core.mainloop import *

#===============================================================================
# Interface de inicialização
#===============================================================================
from FGAme.core.init import Control as _Control
conf = _Control()
init = conf._init
init_canvas = conf._init_canvas
