'''Multiple argument dispatching.

This module was inspired on Aric Coady's multimethod module in pypi.

Introduction
------------

Multiple argument dispatch is a technique in which different implementations of 
a function can be used depending on the type and number of arguments. This module
provides the ``multifunction`` and ``multimethod`` classes that provides 
multiple argument dispatch to Python. Multiple dispatch functions can be easily
created by decorating an ordinary python function::

    @multifunction(*types)
    def func(*args):
        pass
|
*func* is now a ``multifunction`` which will delegate to the above implementation 
when called with arguments of the specified types. If an exact match can't 
be found, the next closest method is called (and cached). If there are 
multiple or no candidate methods, a DispatchError (which derives from TypeError) 
is raised.
        
Basic usage
-----------

The easiest way to create a new multifunction is to supplement an implementation 
with the ``multifunction(*types)`` decorator.

>>> @multifunction(int, int)
... def join(x, y):
...     "Join two objects, x and y"
...     return x + y

This creates a multiple dispatch function that only accepts two integer 
positional arguments.
 
>>> join(1, 1)
2

>>> join(1., 1.)
Traceback (most recent call last):
...
DispatchError: join(float, float): no methods found

An alternative way to create a ``multifunction`` object is to use the explicit 
``multifunction.new()`` constructor. 

>>> join = multifunction.new('join', doc="Join two objects, x and y")

After creating a ``multifunction`` instance, types can be mapped to their 
respective implementations functions by assigning keys to a dictionary.

>>> join[int, int] = lambda x, y: x + y
>>> join[float, float] = lambda x, y: x + y + 0.1 

The ``join`` multifunction now accepts (int, int) and (float, float) arguments

>>> join(1, 1) + join(1., 1.) # 2 + 2.1
4.1

The ``.dispatch()`` method is a more convenient way to add additional 
implementations to the `multifunction`.  

>>> @join.dispatch(list, list)
... def join(x, y):
...     return x + y
>>> join([1], [join(1, 1)])
[1, 2]

Multiple decorators are also accepted.

>>> @join.dispatch(float, int)
... @join.dispatch(int, float)
... def join_numbers(x, y):
...     return x + y

If the implementation function have a different name than the multifunction, 
both will live in the same namespace.

>>> join(1, 2.), join_numbers(1 + 2j, 2 + 1j)
(3.0, (3+3j))

A `multifunction` is a callable dictionary that maps tuples of types to 
functions. All methods of regular dictionaries are accepted.

>>> dict(join) # doctest: +ELLIPSIS
{(<...>, <...>): <function ... at 0x...>, ...}

We can remove an implementation by simply deleting it from the dictionary. 

>>> del join[list, list]
>>> join([1], [2])
Traceback (most recent call last):
...
DispatchError: join(list, list): no methods found

Use None to capture arbitrary types at a given position. The caller always tries
to find the most specialized implementation, and uses None only as a fallback.

>>> @join.dispatch(None, int)
... def join(x, y):
...     return x + y - 0.1
>>> join(1, 2), join(1 + 0j, 2)
(3, (2.9+0j))

One can also define a fallback function that is called with an arbitrary number 
of positional arguments. Just use the fallback decorator of a multifunction

>>> @join.fallback
... def join(*args):
...     return sum(args)
>>> join(1, 2, 3, 4)
10

Multi argument dispatch for class methods
-----------------------------------------

`multifunction`'s can be used inside class declarations as any regular function.  
It has a small inconvenient that the type of first argument `self` must be present
in the type signature. Since the class was not yet created, the type does not
exist and the fallback ``None`` must be used. 

>>> class Foo(object):
...     @multifunction(None, int)
...     def double(self, x):
...         print(2 * x)
... 
...     @double.dispatch(None, complex)
...     def double(self, x):
...         print("sorry, I don't like complex numbers")

The multiple argument dispatch works as before. 

>>> Foo().double(2)
4
>>> Foo().double(2j)
sorry, I don't like complex numbers

The ``multimethod`` class omits the type declaration for the first argument
of the function (usually the first argument is self). It is convenient for
using in the body of class declarations. 

>>> class Bar(object):
...     @multimethod(int)       # the type of self is not declared...
...     def double(self, x):    # ...but it appears on implementations as usual 
...         print(2 * x)
... 
...     @double.dispatch(complex)
...     def double(self, x):
...         print("sorry, I don't like complex numbers")

>>> Bar().double(2)
4
>>> Bar().double(2j)
sorry, I don't like complex numbers

``multifunction(None, ...)`` and ``multimethod(...)`` are equivalent. The 
second is just a small convenience that helps code look clean and tidy.
'''

import sys
from collections import MutableMapping
from types import MethodType
import itertools

__all__ = ['multifunction', 'multimethod', 'DispatchError']

class DispatchError(TypeError):
    pass

class multifunction(MutableMapping):
    '''Implements a multi argument dispatch function.'''

    __slots__ = ['_name', '_doc', '_dict', '_cache', '_last', '_data']
    _slots_set_ = set(__slots__)
    _FUNCTYPE = type(lambda:None)

    #===========================================================================
    # Multimethod instance creation
    #===========================================================================
    def __new__(cls, *types):
        '''Return a decorator which will add the function to the current
        multifunction.'''

        def decorator(func):
            if isinstance(func, cls):
                new, func = func, func._last
            else:
                new = cls.new(func.__name__)
            return new.dispatch(*types)(func)

        return decorator

    @classmethod
    def new(cls, name='', doc=None):
        '''Explicitly create a new multifunction.

        Assign to local name in order to use decorator.'''

        self = object.__new__(cls)
        self._data = {}
        self._cache = {}
        self._dict = {}
        self._name = name
        self._doc = doc
        return self

    def dispatch(self, *types):
        '''Returns a decorator that sets a function as an specific 
        implementation of some type signature. Multiple types for the same 
        argument position can be specified as tuples.
        
        Examples
        --------
        
        >>> add = multimethod.new('add')
        >>> @add.dispatch((int, float, complex), (int, float, complex))
        ... def add(x, y):
        ...     return x + y
        
        This method accepts int's, float's or complex's numbers as any of its 
        two arguments.
        '''

        def decorator(func):
            # compute all types signatures permutations
            for tsig in  itertools.product(*(
                    (t if isinstance(t, tuple) else [t])
                        for t in types)):
                self[tsig] = func

            self._last = func
            if self._name == func.__name__:
                return self
            else:
                return func

        return decorator

    def fallback(self, func):
        '''Sets the fallback function.

        May be called as a decorator.'''

        self._cache[None] = self._data[None] = func
        if func.__name__ == self._name:
            return self
        else:
            return func

    def get_function(self, *types):
        '''Returns the appropriate implementation function from the given types,
        considering inheritance.'''

        try:
            func = self._cache[types]
        except KeyError:
            parents = self.parents(*types)
            if len(parents) == 1:
                func = self._cache[parents.pop()]
            elif not parents:
                fmt_types = ', '.join(t.__name__ for t in types)
                raise DispatchError('{0}({1}): no methods found'
                                    .format(self._name, fmt_types))
            else:
                msg = ('more than one possible parent for {0}{1}: {2}'
                       .format(self._name, types, parents))
                raise DispatchError(msg)
            self._cache[types] = func
        return func

    #===========================================================================
    # Find parents
    #===========================================================================
    @staticmethod
    def is_parent(tuple1, tuple2):
        '''Return True if first argument is parent of second one.

        A tuple of types is parent of another tuple of types if they have the
        same length and all types of the second are subclasses of the
        corresponding types in the first.
        '''

        def subcompare(t1, t2):
            if t1 is None:
                return True
            elif t2 is None:
                return False
            else:
                return issubclass(t2, t1)

        if tuple1 == tuple2:
            return False
        elif tuple1 is None:
            return True
        elif tuple2 is None:
            return False
        elif len(tuple1) != len(tuple2):
            return False
        else:
            return all(map(subcompare, tuple1, tuple2))

    def parents(self, *types):
        '''Return a set with the direct parents of a tuple of types.'''

        is_parent = self.is_parent
        parents = set()
        for node in self._cache:
            if is_parent(node, types):
                parents.add(node)
                for p in list(parents):
                    if is_parent(node, p):
                        parents.discard(node)
                    elif is_parent(p, node):
                        parents.discard(p)

        return parents

    #===========================================================================
    # Dict magic methods
    #===========================================================================
    def __setitem__(self, types, func):
        if self.__doc__ is None:
            self.__doc__ = getattr(func, '__doc__', None)
        if not isinstance(types, tuple):
            types = (types,)

        self._data[types] = func
        if len(self._cache) == len(self._data) - 1:
            self._cache[types] = func  # Cache has the same items as self._data
        else:
            self._cache.clear()
            self._cache.update(self._data)

    def __getitem__(self, types):
        try:
            return self._data[types]
        except KeyError as ex:
            if isinstance(types, type):
                return self[(types,)]
            else:
                raise ex

    def __delitem__(self, types):
        del self._data[types]
        if len(self._cache) == len(self._data) + 1:
            del self._cache[types]  # Cache has the same items as self._data
        else:
            self._cache.clear()
            self._cache.update(self._data)

    def __len__(self):
        return len(self._data)

    def __contains__(self, key):
        return key in self._data

    def __iter__(self):
        return iter(self._data)

    def __call__(self, *args, **kwargs):
        "Resolve and dispatch to best method."

        func = self.get_function(*(type(x) for x in args))
        return func(*args, **kwargs)

    def __getattr__(self, attr):
        try:
            return self._dict[attr]
        except KeyError:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        cls = type(self)
        if attr in self._slots_set_:
            getattr(cls, attr).__set__(self, value)
        else:
            self._dict[attr] = value

    def __repr__(self):
        return '<{cls} {name} at 0x{id}>'.format(cls=type(self).__name__,
                                                 name=self._name,
                                                 id=id(self))

    def __get__(self, instance, cls=None):
        '''Makes it behave as a regular function in classes'''

        # python 2 return MethodType(self, MethodType, cls)
        return MethodType(self, MethodType)

    #===========================================================================
    # Function properties
    #===========================================================================
    @property
    def __annotations__(self):
        return {}

    @property
    def __closure__(self):
        return None

    @property
    def __code__(self):
        return None

    @property
    def __defaults__(self):
        return None

    @property
    def __globals__(self):
        return sys._getframe(1).f_locals

    @property
    def __name__(self):
        return self._name

    @__name__.setter
    def __name__(self, value):
        self._name = value

    @property
    def __doc__(self):
        return self._doc

    @__doc__.setter
    def __doc__(self, value):
        self._doc = value

    @property
    def __dict__(self):
        return self._dict

    # Backwards compatibility with python 2, if necessary
    if sys.version_info[0] == 2:
        func_closure = __closure__
        func_code = __code__
        func_defaults = __defaults__
        func_globals = __globals__
        func_name = __name__
        func_doc = __doc__

class multimethod(multifunction):
    '''Multi argument dispatch for functions that are used as methods inside a
    class declaration.
    '''

    __slots__ = multifunction.__slots__

    def __call__(self, other, *args, **kwds):
        method = self.get_function(*tuple(type(x) for x in args), **kwds)
        return method(other, *args, **kwds)

# # class pattern(MutableSequence):
# # # TODO: review implementation
# #     def __init__(self):
# #         pass
# #
# #
# # @pattern
# # def fat(x):
# #     return x * fat(x - 1)
# #
# # @fat.pattern(0)
# # def fat(x):
# #     return 1
#
# class vmultifunction(multifunction):
#     '''Dispatch according to type or value.
#
#     Examples
#     --------
#
#     Define a function with various implementations
#
#     >>> @vmultifunction(int, str)
#     ... def myfunc(x, y):
#     ...     return str(x * float(y))
#
#     >>> @vmultifunction(int, str, 'concat')
#     ... def myfunc(x, y):
#     ...     return y * x
#
#     >>> @vmultifunction(object, object)
#     ... def myfunc(x, y):
#     ...     return 'x: %s, y: %s' % (x, y)
#
#
#     The computation is dispatched to each implementation automatically
#
#     >>> myfunc(1, 2)
#     'x: 1, y: 2'
#     >>> myfunc(2, '2')
#     '4.0'
#     >>> myfunc(2, '2', 'concat')
#     '22'
#
#     And fails if no implementation is available
#
#     >>> myfunc(2, '2', 'foo')
#     Traceback (most recent call last):
#     ...
#     DispatchError: myfunc(<type 'int'>, <type 'str'>, <type 'str'>): no methods found
#     '''
#
#     def __setitem__(self, args, func):
#         # Separate types from values
#         types = []
#         values = []
#         for idx, arg in enumerate(args):
#             if isinstance(arg, type):
#                 types.append(arg)
#             else:
#                 values = tuple(args[idx:])
#                 break
#         types = tuple(types)
#
#         # Set function
#         try:
#             curr_func = self[types]
#         except KeyError:
#             if values:
#                 dispatcher = ValueDispatcher(self, len(types))
#                 dispatcher[values] = func
#                 func = dispatcher
#         else:
#             if isinstance(curr_func, ValueDispatcher):
#                 curr_func[values] = func
#                 func = curr_func
#             else:
#                 dispatcher = ValueDispatcher(self, len(types))
#                 dispatcher[()] = curr_func
#                 dispatcher[values] = func
#                 func = dispatcher
#
#         super(vmultifunction, self).__setitem__(types, func)

if __name__ == '__main__':
    import doctest
    doctest.testmod()