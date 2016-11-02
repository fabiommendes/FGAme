import functools
import types

__all__ = [
    'CachingProxy', 'caching_proxy_factory', 'autodoc', 'popattr', 'lru_cache',
    'console_here']


class CachingProxy:
    """
    A proxy object that caches all attribute access for faster
    re-evaluation.

    Delegate can be intialized by an object or by a factory.
    """

    def __init__(self, obj=None, factory=None):
        self.__data = obj
        self.__factory = factory

    def __getattr__(self, attr):
        if self.__data is None:
            self.__data = self.__factory()

        value = getattr(self.__data, attr)
        if isinstance(value, types.MethodType):
            setattr(self, attr, value)
        return value


def caching_proxy_factory(func):
    """
    Decorator that initializes a CachingProxy object by setting its factory
    function.
    """

    return CachingProxy(factory=func)


def autodoc(cls):
    """
    Decorador de classe que insere automaticamente as strings de
    documentação nos métodos não-documentados de uma classe utilizando a
    string da classe mãe
    """

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
    """Returns attribute `attr` from `obj` and delete it afterwards.
    If attribute does not exist, return `value`"""

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


    def lru_cache(func, maxsize=512):
        return _lru_cache(maxsize=maxsize)(func)

except ImportError:
    def lru_cache(func, maxsize=512):
        D = {}

        @functools.wraps(func)
        def decorated(*args):
            try:
                return D[args]
            except KeyError:
                result = func(*args)
                while len(D) > maxsize:
                    D.popitem()
                return result

        return decorated


#
# Easy interactive console for debugging
#
def console_here():
    """
    Start debug console.
    """

    import code
    import inspect

    frame = inspect.currentframe().f_back
    ns = dict(frame.f_globals)
    ns.update(frame.f_locals)
    console = code.InteractiveConsole(ns)
    console.interact()


def ipython_here():
    """
    Starts an ipython debug console.
    """

    import IPython.terminal.embed
    import inspect

    frame = inspect.currentframe().f_back

    shell = IPython.terminal.embed.InteractiveShellEmbed(
        argv=["-colors", "NoColor"],
        locals_ns=frame.f_locals,
        globals_ns=frame.f_globals,
    )
    shell()
