#-*- coding: utf8 -*-

from smallvectors import Vec2, Vec3, Vec4, VecND
from smallvectors import Direction2, Direction3, Direction4, DirectionND
from smallvectors import Point2, Point3, Point4, PointND


###############################################################################
#                         Propriedades vetoriais
###############################################################################
class VecSlot(object):

    '''A slot-like property that holds a vector object'''

    __slots__ = ['getter', 'setter']

    def __init__(self, slot):
        self.setter = slot.__set__
        self.getter = slot.__get__

    def __get__(self, obj, tt):
        return self.getter(obj, tt)

    def __set__(self, obj, value):
        if not isinstance(value, Vec2):
            value = Vec2.from_seq(value)
        self.setter(obj, value)

    def update_class(self, tt=None, *args):
        '''Update all enumerated slots/descriptors in class to be VecSlots'''

        if tt is None:

            def decorator(tt):
                self.update_class(tt, *args)
                return tt
            return decorator

        for sname in args:
            slot = getattr(tt, sname)
            setattr(tt, sname, VecSlot(slot))


###############################################################################
# Late binding
###############################################################################
VecND._dim2 = Vec2
VecND._dim3 = Vec3
VecND._dim4 = Vec4
DirectionND._dim2 = Direction2
DirectionND._dim3 = Direction3
DirectionND._dim4 = Direction4
PointND._dim2 = Point2
PointND._dim3 = Point3
PointND._dim4 = Point4
