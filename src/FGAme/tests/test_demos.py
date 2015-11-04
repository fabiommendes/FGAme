import FGAme
from FGAme.tests import unittest
FGAme.conf.DEBUG = True


class DemoBase:
    path = None
    maxiter = 120
    check_final_condition = None
    get_initial_condition = None
    kwds = {}

    def get_world_object(self):
        '''Load world object from path.

        Prevents execution of the run() method when loading a module.'''

        old_run = FGAme.World.run
        FGAme.World.run = lambda self: None

        try:
            mod_path, _, clsname = self.path.rpartition('.')
            mod = __import__(mod_path, fromlist=(clsname,))
            cls = getattr(mod, clsname)
        finally:
            FGAme.World.run = old_run

        if isinstance(cls, type):
            return cls(**self.kwds)
        else:
            return cls

    def run_world(self, world):
        world.run(maxiter=self.maxiter, wait=False)

    def test_world_starts(self):
        self.get_world_object()

    def test_world_runs(self):
        world = self.get_world_object()
        self.run_world(world)

    def test_world_condition(self):
        if self.check_final_condition:
            world = self.get_world_object()
            ICs = self.get_initial_condition(world)
            self.run_world(world)
            self.check_final_condition(world, ICs)


class TestGravityTutorial(DemoBase, unittest.TestCase):
    path = 'FGAme.demos.tutorial_gravity.GravityWorld'


class TestSimpleGas(DemoBase, unittest.TestCase):
    maxiter = 60
    path = 'FGAme.demos.simulations.gas_simple.Gas'


class TestGasAABBs(DemoBase, unittest.TestCase):
    maxiter = 60
    path = 'FGAme.demos.simulations.gas_aabbs.world'


class TestGasPolys(DemoBase, unittest.TestCase):
    path = 'FGAme.demos.simulations.gas_polys.world'


class TestSimpleCircle(DemoBase, unittest.TestCase):
    path = 'FGAme.demos.simulations.simple_circle.world'


class TestSimpleAABB(DemoBase, unittest.TestCase):
    path = 'FGAme.demos.simulations.simple_aabb.world'


class TestSimplePoly(DemoBase, unittest.TestCase):
    path = 'FGAme.demos.simulations.simple_poly.world'


class TestSimpleMixed(DemoBase, unittest.TestCase):
    path = 'FGAme.demos.simulations.simple_mixed.world'


class TestTripleCircleCollision(DemoBase, unittest.TestCase):
    path = 'FGAme.demos.simulations.triple_circle.world'


class TestTriplePolyCollision(DemoBase, unittest.TestCase):
    path = 'FGAme.demos.simulations.triple_poly.world'

if __name__ == '__main__':
    unittest.main('FGAme.tests.demos')
