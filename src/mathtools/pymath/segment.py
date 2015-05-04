# -*- coding: utf8 -*-

from mathtools import mVec2, Vec2


class Segment(object):
    __slots__ = ['_point1', '_point2']

    def __init__(self, point1, point2):
        self._point1 = mVec2(point1)
        self._point2 = mVec2(point2)
