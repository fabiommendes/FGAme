from random import uniform

from FGAme import *
from FGAme.mathtools import *


class AngryTriangles(World):
    def init(self):
        # Triangle
        L = 40
        h = 10 * sqrt(12)
        self.tri = self.add.regular_poly(3, L, color=(200, 0, 0), density=50)
        self.tri.move((65, 250 + L))
        self.tri.boost((450, 350))
        self.tri.aboost(-5)

        # Floor
        floor = self.add.aabb((-10000, 10000, 0, 150), color=(68, 170, 0))
        floor.make_static()

        # Pole
        pole = self.add.aabb((50, 60, 150, 350), color=(158, 86, 38))
        pole.make_static()

        # Boxes
        height = 80
        width = 200
        pos = Vec2(650, 190)
        shape = (width, height)
        self.add.rectangle(pos=pos, shape=shape, color=(158, 86, 38))

        for _ in range(4):
            shapeX, shapeY = shape
            height *= 0.75
            width *= 2. / 3
            deltay = shapeY / 2. + height / 2. - 1
            deltax = uniform(-shapeX / 6., shapeX / 6.)
            pos = pos + (deltax, deltay)
            shape = (width, height)
            self.add.rectangle(pos=pos, shape=shape, color=(158, 86, 38))


if __name__ == '__main__':
    world = AngryTriangles(background=Color(0, 204, 255),
                           gravity=500,
                           friction=0.5,
                           adamping=0.1,
                           damping=0.1,
                           restitution=0.3)
    world.run()
