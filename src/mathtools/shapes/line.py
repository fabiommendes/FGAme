# -*- coding: utf8 -*-
from mathtools import dot

Inf = float('inf')


class Line(object):

    def __init__(self, *args):
        pass

    def directions(self, n):
        return [self.tangent(), self.normal()]

    def shadow(self, n):
        if abs(dot(self.tangent(), n)) < 1e-6:
            p = dot(self.p1, n)
            return p, p
        else:
            return [-Inf, Inf]
