# -*- coding: utf8 -*-
__all__ = ['PublicProperty', 'HasPublic', 'auto_public']
import cython


class PublicProperty(object):

    '''Implementa uma propriedade privada com acesso publico somente para
    leitura.'''

    __slots__ = ['name', 'getter', 'setter']

    def __init__(self, name=None):
        self.name = name
        self.getter = None
        self.setter = None

    def __get__(self, obj, tt):
        if obj is None:
            return self
        else:
            return self.getter(obj, tt)

    def __set__(self, obj, value):
        name = self.name
        tname = type(obj).__name__
        raise ValueError('%s attribute of %s is read-only' % (name, tname))

    def slot_name(self):
        if not self.name.startswith('_'):
            return '_' + self.name
        else:
            return self.name

    def update_class(self, cls):
        setattr(cls, self.name, self)
        slot = getattr(cls, self.slot_name())
        self.update_slot(slot)

    def update_name(self, name):
        if self.name is None:
            self.name = name

    def update_slot(self, slot):
        self.getter = slot.__get__
        self.setter = slot.__set__


class HasPublic(type):

    '''Meta-classe para tipos que possuem propriedades do tipo PublicProperty().

    É possível criar automaticamente
    '''
    def __new__(cls, name, bases, ns):
        props = cls.extract_properties(ns)
        slots = list(ns.setdefault('__slots__', []))
        slots.extend([x.slot_name() for x in props.values()])
        ns['__slots__'] = slots
        new = type.__new__(cls, name, bases, ns)
        for prop in props.values():
            prop.update_class(new)
        return new

    @classmethod
    def extract_properties(cls, ns):
        '''Return all properties objects in the given namespace'''

        properties = {}
        for k, v in list(ns.items()):
            if isinstance(v, PublicProperty):
                v.update_name(k)
                properties[k] = v
                del ns[k]
        return properties


def auto_public(tt=None, slots=None):
    '''Cria um acesso público somente para leitura para todas as
    propriedades em __slots__ definidas como privadas (que iniciam com um
    underscore) e não possuam nenhuma interface pública definida.'''

    if tt is None:
        def decorator(tt):
            return auto_public(tt, slots)
        return decorator

    if cython.compiled:
        return tt

    if slots is None:
        slots = []
        for tt_i in tt.mro():
            slots.extend(getattr(tt_i, '__slots__', ()))

    for slot in slots:
        if slot.startswith('_'):
            name = slot[1:]
            if not hasattr(tt, name):
                prop = PublicProperty(name)
                prop.update_slot(getattr(tt, slot))
                prop.update_class(tt)
    return tt


###############################################################################
#                 Classes mãe para objetos geométricos
###############################################################################

class ShapeBase(object):

    def intercepts(self, obj):
        pass

    def distance(self, obj):
        pass

    def connect_segments(self, obj):
        pass

    def intercept_points(self, obj):
        pass


class ClosedShape(ShapeBase):

    def contains(self, other):
        pass

    def __contains__(self, other):
        if isinstance(other, ShapeBase):
            pass
        return self.contains(other)
