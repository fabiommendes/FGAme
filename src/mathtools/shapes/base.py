from mathtools import Vec2


class Curve(object):

    '''Base class for all shape objects'''

    # These must be fixed after the proper subclasses are defined using late
    # binding
    _Circle = None
    _Segment = None

    # Geometric operations ####################################################

    # Distance FGAme_tests ##########################################################
    def distance_point(self, point):
        '''Return the distance of object to the given point. Return 0.0 if
        they intercept'''

        raise NotImplementedError

    def distance_circle(self, circle):
        '''Return the distance to the given circle. Return 0.0 if both shapes
        intercept'''

        raise NotImplementedError

    def distance(self, other):
        '''Return the distance between two objects. Return 0.0 if they
        intercept'''

        if isinstance(other, (Vec2, tuple)):
            return self.distance_point(other)
        elif isinstance(other, self._Circle):
            return self.distance_circle(other)
        else:
            t1 = type(self).__name__
            t2 = type(other).__name__
            raise TypeError('invalid distance test: %s vs %s' % (t1, t2))


class Solid(Curve):

    '''Base class for all closed shape objects'''

    __slots__ = []

    # Containement FGAme_tests ######################################################
    def contains_point(self, point):
        '''Tests if the given point is completely contained by object'''

        raise NotImplementedError

    def contains_circle(self, circle):
        '''Tests if the given circle is completely contained by object'''

        raise NotImplementedError

    def contains_segment(self, segment):
        '''Tests if the given line segment is completely contained by object'''

        raise NotImplementedError

    def __contains__(self, other):
        if isinstance(other, (Vec2, tuple)):
            return self.contains_point(other)
        elif isinstance(other, self._Circle):
            return self.contains_circle(other)
        else:
            t1 = type(self).__name__
            t2 = type(other).__name__
            raise TypeError('invalid containement test: %s vs %s' % (t1, t2))


class Convex(Curve):

    '''Base class for all convex shaped objects'''

    # Generic containement FGAme_tests implementations that are valid for all convex
    # shapes

    def contains_segment(self, segment):
        pt_test = self.contains_point
        pt1, pt2 = segment
        return pt_test(pt1) and pt_test(pt2)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
