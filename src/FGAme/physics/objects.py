from FGAme.physics.elements import PhysCircle, PhysBall, PhysAABB
from FGAme.physics.elements.mixins import ObjectMixin


class AABB(ObjectMixin, PhysAABB):

    def __init__(self,
                 pos=None, vel=(0, 0),
                 mass=None, density=None,
                 xmin=None, xmax=None, ymin=None, ymax=None,
                 bbox=None, shape=None, **kwds):

        PhysAABB.__init__(self,
                          pos, vel, mass, density,
                          xmin, xmax, ymin, ymax,
                          bbox, shape)
        self._init_mixin(**kwds)


class Circle(ObjectMixin, PhysCircle):

    def __init__(self,
                 pos=(0, 0), vel=(0, 0),
                 mass=None, density=None,
                 radius=None, **kwds):

        PhysCircle.__init__(self, pos, vel, mass, density, radius)
        self._init_mixin(**kwds)


class Ball(ObjectMixin, PhysBall):

    def __init__(self,
                 pos=(0, 0), vel=(0, 0),
                 mass=None, density=None,
                 theta=0.0, omega=0.0, inertia=None,
                 radius=None, **kwds):

        PhysBall.__init__(self,
                          pos, vel, mass, density,
                          theta, omega, inertia,
                          radius)
        self._init_mixin(**kwds)


class Poly(ObjectMixin, PhysAABB):

    def __init__(self,
                 pos=None, vel=(0, 0),
                 mass=None, density=None,
                 xmin=None, xmax=None, ymin=None, ymax=None,
                 bbox=None, shape=None, **kwds):

        PhysAABB.__init__(self,
                          pos, vel, mass, density,
                          xmin, xmax, ymin, ymax,
                          bbox, shape)
        self._init_mixin(**kwds)


if __name__ == '__main__':
    x = AABB(shape=(100, 200))
    print(x)