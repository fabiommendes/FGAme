# -*- coding: utf8 -*-
from __future__ import print_function

from FGAme.mathutils import *
from FGAme import *
from random import uniform, choice


def random_color():
    return tuple(int(uniform(0, 255)) for i in range(3))


class Scenario:

    def floor(self):
        floor = AABB(bbox=(-10000, 10000, 0, 150), color=(68, 170, 0))
        floor.make_static()
        return floor

    def pole(self):
        pole = AABB(bbox=(50, 60, 150, 350), color=(158, 86, 38))
        pole.make_static()
        return pole

    def boxes(self):
        height = 80
        width = 200
        pos = Vec2(650, 190)
        shape = (width, height)
        p = Rectangle(pos=pos, shape=shape, color=(158, 86, 38))
        yield p

        for _ in range(4):
            shapeX, shapeY = shape
            height *= 0.75
            width *= 2. / 3
            deltay = shapeY / 2. + height / 2. - 1
            deltax = uniform(-shapeX / 6., shapeX / 6.)
            pos = pos + (deltax, deltay)
            shape = (width, height)
            yield Rectangle(pos=pos, shape=shape, color=(158, 86, 38))

    def get_objects(self):
        yield self.floor()
        yield self.pole()
        for box in self.boxes():
            yield box


# Inicializa o cenário
scene = Scenario()

# Cria triângulo
L = 40
h = 10 * sqrt(12)
tri = RegularPoly(3, L, color=(200, 0, 0), density=50)
tri.move((65, 250 + L))
tri.boost((350, 350))
tri.aboost(-5)
# tri.is_dynamic_angular = False

# Inicializa o mundo
world = World(background=(0, 204, 255),
              gravity=500,
              dfriction=0.3,
              sfriction=0.5,
              restitution=0.7)
for obj in scene.get_objects():
    world.add(obj)
world.add(tri)

# Inicia a simulação
world.run()
