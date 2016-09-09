from smallshapes.utils import accept_vec_args
from FGAme.mathtools import Vec2, asvector


def flag_property(flag):
    """
    Return a property object associated to the given flag.
    """

    def fget(self):
        return bool(self.flags & flag)

    def fset(self, value):
        if value:
            self.flags |= flag
        else:
            self.flags &= ~flag

    return property(fget, fset)


def vec_property(slot):
    """
    A property element that forces conversion to a Vec2 value.
    """

    getter = slot.__get__
    setter = slot.__set__

    class VecProperty(object):
        __slots__ = []

        def __set__(self, obj, value):
            if not isinstance(value, Vec2):
                value = asvector(value)
            setter(obj, value)

        def __get__(self, obj, cls):
            if obj is None:
                return self
            else:
                return getter(obj, cls)

    return VecProperty()
