import os
import importlib

GLOBAL_INFO = None

def get_info():
    '''Retorna um dicionário mapeando cada backend com um dicionário que
    mapeia 'input', 'screen' e 'mainloop' nos nomes das respectivas classes'''
    
    global GLOBAL_INFO
    
    if GLOBAL_INFO is not None:
        return GLOBAL_INFO
    
    else:
        GLOBAL_INFO = out = {}
        path, _ = os.path.split(__file__)
        for path in os.listdir(path):
            if path.endswith('_conf.py'):
                name, _, _ = path.rpartition('_')
                conf = importlib.import_module('FGAme.backends.%s_conf' % name)
                out[name] = dict(
                    input=conf.input,
                    screen=conf.screen,
                    mainloop=conf.mainloop,
                )
        return out 

def get_classes(backend):
    '''Retorna um dicionário mapeando 'input', 'screen' e 'mainloop' nas 
    respectivas classes para o backend selecionado.
    
    Exemplos
    --------
    
    >>> from FGAme.backends import pygame as pygame_be
    >>> D = get_classes('pygame')
    >>> D == {'input':    pygame_be.PyGameInput, 
    ...       'mainloop': pygame_be.PyGameMainLoop,
    ...       'screen':   pygame_be.PyGameCanvas}
    True
    '''
    
    D = get_info()[backend]
    return {k: _get_class_worker(k, backend) for k in D}

def _get_class_worker(cls, backend):
    '''Implementa as funções get_screen, get_input, get_mainloop, etc'''
    
    D = get_info()[backend]
    module = importlib.import_module('FGAme.backends.%s' % backend)
    return getattr(module, D[cls])

def get_screen_class(backend):
    '''Retorna a classe de screen para o backend selecionado'''
    
    return _get_class_worker('screen', backend)

def get_input_class(backend):
    '''Retorna a classe de input para o backend selecionado'''
    
    return _get_class_worker('input', backend)

def get_mainloop_class(backend):
    '''Retorna a classe de mainloop para o backend selecionado'''
    
    return _get_class_worker('mainloop', backend)

if __name__ == '__main__':
    import doctest
    doctest.testmod()