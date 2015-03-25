from FGAme import physics
from FGAme.objects.mixins import ObjectMixin


class AABB(ObjectMixin, physics.AABB):
    _init_physics = physics.AABB.__init__


class Circle(ObjectMixin, physics.Circle):
    _init_physics = physics.Circle.__init__


class Ball(ObjectMixin, physics.Ball):
    _init_physics = physics.Ball.__init__


class Poly(ObjectMixin, physics.Poly):
    _init_physics = physics.Poly.__init__


class Rectangle(ObjectMixin, physics.Rectangle):
    _init_physics = physics.Rectangle.__init__


class RegularPoly(ObjectMixin, physics.RegularPoly):
    _init_physics = physics.RegularPoly.__init__

if __name__ == '__main__':
    x = AABB(shape=(100, 200), world=set())
    type(x)
    type(x).__bases__
    print(x.mass)
