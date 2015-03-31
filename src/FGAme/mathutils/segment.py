from FGAme.mathutils import VectorM, Vector


class Segment(object):
    __slots__ = ['_point1', '_point2']

    def __init__(self, point1, point2):
        self._point1 = VectorM(point1)
        self._point2 = VectorM(point2)
