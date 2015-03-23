class Ray(object):

    def __init__(self, point, direction):
        self.point = VectorM(point)
        self.direction = VectorM(direction).normalized()