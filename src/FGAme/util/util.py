import types
import functools
from smallvectors.tools import lazy

__all__ = ['lazy', 'delegate_to', 'autodoc', 'popattr', 'lru_cache', 
           'console_here']


class delegate_to(property):

    '''Sincroniza com um attributo de contido em um sub-attributo da classe.

    Exemplo
    -------

    >>> class Foo(object):
    ...     def __init__(self):
    ...         self._data = []
    ...
    ...     add = delegate_to('_data.append')

    Agora criamos um objeto

    >>> x = Foo()
    >>> x.add(1); x.add(2); x._data
    [1, 2]
    '''

    def __init__(self, delegate, read_only=False):
        self.delegate = delegate
        attrs = delegate.split('.')
        delegate = attrs.pop(0)

        if len(attrs) == 0:
            def fget(self):
                return getattr(self, delegate)

            def fset(self, value):
                setattr(self, delegate, value)

            def fdel(self):
                delattr(self, delegate)

        elif len(attrs) == 1:
            attr = attrs[0]

            def fget(self):
                delegate_obj = getattr(self, delegate)
                return getattr(delegate_obj, attr)

            def fset(self, value):
                delegate_obj = getattr(self, delegate)
                setattr(delegate_obj, attr, value)

            def fdel(self):
                delegate_obj = getattr(self, delegate)
                delattr(delegate_obj, attr)

        else:
            raise NotImplementedError('more than one dot')

        if read_only:
            super(delegate_to, self).__init__(fget)
        else:
            super(delegate_to, self).__init__(fget, fset, fdel)


def autodoc(cls):
    '''Decorador de classe que insere automaticamente as strings de
    documentação nos métodos não-documentados de uma classe utilizando a
    string da classe mãe'''

    func_t = types.FunctionType

    for attr, value in vars(cls).items():
        if isinstance(value, func_t) and not value.__doc__:
            for sub in cls.mro():
                try:
                    doc = getattr(sub, attr).__doc__
                except AttributeError:
                    doc = None
                    break
                if doc:
                    break

            value.__doc__ = doc

    return cls


def popattr(obj, attr, value=None):
    '''Returns attribute `attr` from `obj` and delete it afterwards.
    If attribute does not exist, return `value`'''

    try:
        result = getattr(obj, attr)
    except AttributeError:
        return value
    else:
        delattr(obj, attr)
        return result


#
# A least recently used cache with 512 entries
#
try:
    from functools import lru_cache as _lru_cache
    def lru_cache(func):
        '''A least recently used cache: keeps the 512 most recent results of
        function in cache'''
        return _lru_cache(maxsize=512)(func)
except ImportError:
    def lru_cache(func):
        '''A least recently used cache: keeps the 512 most recent results of
        function in cache'''
        D = {}

        @functools.wraps(func)
        def decorated(*args):
            try:
                return D[args]
            except KeyError:
                result = func(*args)
                while len(D) > 512:
                    D.popitem()
                return result
        return decorated


#
# Easy interactive console for debugging
#
def console_here():
    '''Cria um console local para debug'''
    
    import code
    import inspect
    
    frame = inspect.currentframe().f_back
    ns = dict(frame.f_globals)
    ns.update(frame.f_locals)
    console = code.InteractiveConsole(ns)
    console.interact()

def ipython_here():
    '''Cria um console local para debug usando IPython'''
    
    import IPython.terminal.embed
    import inspect
    
    frame = inspect.currentframe().f_back
    
    shell = IPython.terminal.embed.InteractiveShellEmbed(
        argv=["-colors", "NoColor"],
        locals_ns=frame.f_locals, 
        globals_ns=frame.f_globals,
    )
    shell()
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
    ipython_here()
