# -*- coding: utf8 -*-


class Ray(object):

    def __init__(self, point, direction):
        self.point = mVec2(point)
        self.direction = mVec2(direction).normalize()
