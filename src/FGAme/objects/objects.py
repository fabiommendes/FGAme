from FGAme import physics
from FGAme.objects.mixins import ObjectMixin


class AABB(ObjectMixin, physics.AABB):
    pass


class Circle(ObjectMixin, physics.Circle):
    pass


class Ball(ObjectMixin, physics.Ball):
    pass


class Poly(ObjectMixin, physics.Poly):
    pass


class Rectangle(ObjectMixin, physics.Rectangle):
    pass


class RegularPoly(ObjectMixin, physics.RegularPoly):

    pass

if __name__ == '__main__':
    x = AABB(shape=(100, 200), world=set())
    type(x)
    type(x).__bases__
    print(x.mass)
