#-*- coding: utf8 -*-
from math import trunc

class lazy(object):
    '''Implementa uma propriedade "preguiçosa": ela é calculada apenas durante o 
    primeiro uso e não durante a inicialização do objeto.'''

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        value = self.func(obj)
        setattr(obj, self.func.__name__, value)
        return value

