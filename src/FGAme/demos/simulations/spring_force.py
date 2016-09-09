from FGAme import *
from FGAme.physics.forces import SpringTensorPair


class Gravity(World):
    def init(self):
        A = self.add.circle(20, pos=(500, 300), vel=(100, 300), color='red')
        B = self.add.circle(20, pos=(400, 300), vel=(-100, -300))

        # Let us define the interaction force between both objects
        F = SpringTensorPair(A, B, 1500)
        A.force, B.force = F.forces()

if __name__ == '__main__':
    Gravity().run()
