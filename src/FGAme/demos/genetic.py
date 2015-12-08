from math import sqrt
from random import randint, randrange, normalvariate, choice, random
from FGAme import Circle, World, Vec, Color, listen, conf
from collections import Counter
import pympler.tracker
import gc
from pprint import pprint

conf.set_framerate(30)

RANDOM_ACCEL = 400
CELL_RADIUS = 20
CELL_COLOR = [Color('#348DBC99'), Color('#9f848099')]
CELL_BIND_COLOR = Color('#20673F99')
SPRING_CONSTANT = 100000
MIN_AGE = 30
COUPLING_DURATION = 10
gc.enable()


class Cell(Circle):
    def __init__(self, *args, gender=0, code=None, alleles=2, **kwds):
        super().__init__(*args, color=CELL_COLOR[gender], **kwds)
        self.gender = gender
        self.alleles = alleles
        if code is None:
            self.code = self.__random_code()
        else:
            self.code = code
        self.bind = None
        self.age = randrange(MIN_AGE)
        self.coupling_frames = 0

    def __random_code(self):
        """Return a random genetic code"""

        return [randrange(self.alleles), randrange(self.alleles)]

    def force(self, t):
        self.age += 1
        Fx = normalvariate(0, RANDOM_ACCEL) * self.mass
        Fy = normalvariate(0, RANDOM_ACCEL) * self.mass
        force = Vec(Fx, Fy)
        if self.bind is not None:
            self.coupling_frames += 1
            if self.coupling_frames >= COUPLING_DURATION:
                self.crossover(self.bind)
                self.bind.bind = None
                self.bind = None
                return Vec(0, 0)
            force *= 2
            force += SPRING_CONSTANT * (self.bind.pos - self.pos)

        return force

    @listen('pre-collision')
    def collision(self, col):
        other = col.other(self)
        if (isinstance(other, Cell) and self.age > MIN_AGE and
                    other.gender != self.gender):
            if self.bind is other:
                col.cancel()
            elif self.bind is None and other.bind is None:
                col.cancel()
                if abs(self.pos - other.pos) < self.radius * 0.75:
                    self.bind, other.bind = other, self
                    self.color = CELL_BIND_COLOR
                    other.color = CELL_BIND_COLOR

    def fitness(self):
        return {
            (0, 0): 0.1,
            (0, 1): 0.25,
            (1, 0): 0.25,
            (1, 1): 0.75
            }[tuple(self.code)]

    def crossover(self, other):
        fitness = sqrt(self.fitness() * other.fitness())
        if fitness > random():
            for obj in [self, other]:
                obj.gender = randint(0, 1)
                obj.color = CELL_COLOR[obj.gender]

            self.age = other.age = 0
            code1 = [choice(self.code), choice(other.code)]
            code2 = [choice(self.code), choice(other.code)]
            self.code, other.code = code1, code2
        else:
            self.age = other.age = MIN_AGE // 2
            self.color = CELL_COLOR[self.gender]
            other.color = CELL_COLOR[other.gender]
        self.coupling_frames = other.coupling_frames = 0


class GeneticWorld(World):
    def __init__(self, num_cells=50, cell_size=CELL_RADIUS):
        super().__init__(damping=0.7, adamping=1, restitution=1,
                         background='#A2B5BF')
        self.add_bounds(width=15, color='black', use_poly=True)

        def rpos():
            return Vec(randint(CELL_RADIUS, 800 - CELL_RADIUS),
                       randint(CELL_RADIUS, 600 - CELL_RADIUS))

        self.cells = [Cell(cell_size, pos=rpos(), gender=randrange(2))
                      for _ in range(num_cells)]
        self.add(self.cells)
        self.n_frames = 0
        self.tracker = pympler.tracker.SummaryTracker()

    def on_frame_enter(self):
        self.n_frames += 1
        if self.n_frames % 30 == 0:
            points = []
            [points.extend(cell.code) for cell in self.cells]
            counter = Counter(points)
            # print(counter)

            # if self.n_frames % 120 == 10:
            #    self.tracker.print_diff()


if __name__ == '__main__':
    world = GeneticWorld()
    world.run()
