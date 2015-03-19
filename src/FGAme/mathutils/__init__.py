# Importa as funções rápidas caso a variável de ambiente PYGAME_SLOWMATH não
# seja definida 
import os as _os
if not _os.environ.get('PYGAME_SLOWMATH', False):
    try:
        from .linalg_fast import *
    except ImportError:
        from .linalg import *
else:
    from .linalg import *
    
from .util import *
from .vertices import *