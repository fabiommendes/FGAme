# -*- coding: utf8 -*-

'''
Created on 26/03/2015

@author: chips
'''

from abc import ABC
import six


def getname(obj, name=None):
    # Try __name__
    try:
        return obj.__name__
    except AttributeError:
        pass

    # The same thing for classmethods/staticmethods and friends
    try:
        return obj.__func__.__name__
    except AttributeError:
        pass

    return name


def use(ns, name=None):
    def decorator(obj):
        ns[name or getname(obj)] = obj
    return decorator


class DefinitionMeta(type):

    '''Light metaclass wrapper that is used redirect the "class" definition
    syntax sugar to calls to the Definition class.'''

    def __new__(cls, name, bases, namespace):
        if Definition is None:
            return type.__new__(cls, name, bases, namespace)

        # Correct the name
        if not name.endswith('Definition'):
            raise ValueError('Definition classes must be named as '
                             'FooDefinition, got %s' % name)
        name = name[:-10]

        # Remove Definitino from bases
        bases = list(bases)
        del bases[bases.index(Definition)]
        bases = tuple(bases)
        if not bases:
            bases = (object,)

        # Get keyword arguments for the Definition class from the "meta"
        # variable
        meta = namespace.pop('meta', None)
        if not meta:
            kwds = {}
        else:
            kwds = meta.__dict__().items()
            kwds = {k: v for (k, v) in kwds if not k.startswith('__')}

        # Remove Python automatically insertyed cruft from namespace
        garbage = ['__module__', '__qualname__']
        for key in garbage:
            if key in namespace:
                del namespace[key]

        return Definition(name, bases, namespace, **kwds)


Definition = None


@six.add_metaclass(DefinitionMeta)
class Definition(object):

    '''
    Implements an abstract definition of a class. From this definition it is
    possible to generate many classes with slightly different properties.

    Currently, this class implements recepies to generate the mutable,
    immutable and abstract class for mathematical elements.
    '''

    def __init__(self, name, bases, namespace):
        self.name = name
        self.bases = bases
        self.namespace = namespace

        # Default names
        self.abc_name = name + 'Like'
        self.immutable_name = name
        self.mutable_name = 'm' + name

    def make_mutable(self):
        pass

    def make_immutable(self):
        pass

    def make_abc_class(self, name=None):

        D = self._filter_istagged()
        D = self._filter_tag(D, whitelist='abc_required')
        D_attr = self._filter_isattribute(D)
        required_attrs = tuple(D_attr.keys())

        ns = {k: None for k in required_attrs}

        @use(ns)
        @classmethod
        def __subclasshook__(cls, tt):
            # Check all required attributes
            for attr in required_attrs:
                try:
                    attr = getattr(tt, attr)
                except AttributeError:
                    return False

                if not callable(attr) or hasattr(attr, '__get__'):
                    continue
                else:
                    return False

            return True

        return type(name or self.abc_name, (ABC,), ns)

    def _filter_istagged(self, D=None, reverse=False):
        if D is None:
            D = self.namespace
        return {k: v for (k, v) in D.items() if hasattr(v, 'tags') | reverse}

    def _filter_isattribute(self, D=None, reverse=False):
        if D is None:
            D = self.namespace
        return {k: v for (k, v) in D.items()
                if isinstance(v, Attribute) | reverse}

    def _filter_tag(self, D=None, blacklist=None, whitelist=None):
        if D is None:
            D = self.namespace

        if ((blacklist and whitelist)
                or ((not blacklist) and (not whitelist))):
            raise ValueError('exactly one of out or in must be defined')

        tags = blacklist or whitelist
        if isinstance(tags, (list, tuple)):
            raise NotImplementedError
        else:
            tag = tags

        # Filter objects
        out = {}
        blacklist = bool(blacklist)
        for name, obj in D.items():
            hastag = tag in getattr(obj, 'tag', ())
            if not(blacklist | hastag):
                out[name] = obj

        return out

# Metaclasse para fazer implementações simultâneas de uma classe mutável e
# imutável com fallback para implementações em C


class Attribute(object):

    def __init__(self, name,
                 f_in=None, f_out=None,
                 type=None, type_coerce=None,
                 slot=None,
                 read_only=False, write_once=False, abc_required=None):

        self._name = name
        self._f_in = f_in
        self._f_out = f_out
        if abc_required is None:
            abc_required = not name.startswith('_')
        self.abc_required = abc_required

    def __get__(self, obj, cls=None):
        pass

    def __call__(self, name):
        pass

    @property
    def tags(self):
        return {'abc_required': self.abc_required, }


import Box2


if __name__ == '__main__':
    from FGAme import Vec2

    class CircleDefinition(Definition):
        radius = Attribute('radius', type=float)
        pos = Attribute('pos', type=Vec2)

        def __init__(self, radius, pos=(0, 0)):
            self.radius = radius
            self.pos = pos

    Circle = CircleDefinition.make_immutable()
    mCircle = CircleDefinition.make_mutable()
    CircleLike = CircleDefinition.make_abc_class()

    print(issubclass(CircleLike, CircleLike))
