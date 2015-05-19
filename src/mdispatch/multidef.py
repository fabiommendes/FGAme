from mdispatch.histdict import HistDict
from mdispatch.core import multifunction

MultiFunction = None


class MetaFunction(type):

    def __new__(cls, name, bases, ns):
        # Creates the base type
        if MultiFunction is None:
            return type.__new__(cls, name, bases, ns.asdict())

        ns = ns.remove_first(['__module__', '__qualname__'])
        new = multifunction.new()

        for func in ns.allvalues():
            if hasattr(func, '__meta__'):
                meta = func.__meta__
            else:
                meta = MetaFunc.inspecting(func)
            new.dispatch(func, *meta.argtypes)

        return new

    @classmethod
    def __prepare__(cls, name, bases):
        return HistDict()


class MultiFunction(object, metaclass=MetaFunction):
    pass


class MetaFunc(object):

    def __init__(self, func, args=None, kwargs=None):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def inspecting(cls, func):
        print(func)

    @property
    def argtypes(self):
        return [tt for (name, tt, default) in self.args]


class Union(type):

    '''Abstract class that represents a union between types.

    Example
    -------

    >>> num = Union(float, int)
    >>> isinstance(1.0, num)
    True
    >>> isinstance(1, num)
    True
    >>> isinstance(1 + 1j, num)
    False
    '''

    def __new__(self, *types):
        self.types = types


class Blob(object):
    num_bits = None
    abstract = True


class BinNumber(Blob):
    pass


class BinInt(BinNumber):
    pass


class BinFloat(BinNumber):
    pass


class Float64(BinFloat):
    num_bits = 64


class Int64(BinInt):
    num_bits = 64

import math


class sin(MultiFunction):

    def sin(x: int):
        return math.sin(math.pi / 180 * x)

    def sin(x: float):
        return math.sin(x)


'''

yield MultiFunction as sin:
    body
    
def ... with function:
    dsfdsf
        
def ... with function:
    dsfdsf
    

make dict as D:
    apsdasdas
    
begin dict as D:
    apsdasdas



yield function as sin:
    body
    
yield function:
    body

begin sin with function:
    pass

==> sin = function('sin', body_dict)
        

    
'''
if __name__ == '__main__':
    import doctest
    doctest.testmod()
