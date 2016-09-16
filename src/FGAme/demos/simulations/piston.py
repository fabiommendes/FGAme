from random import uniform

from FGAme import *


class Piston(World):
    """
    A piston in a gas of dissipative hard spheres.
    """

    def __init__(self,
                 gravity=200, friction=0.0, restitution=1.0,
                 num_balls=100, speed=200, radius=10,
                 color='random'):

        super(Piston, self).__init__(gravity=gravity, friction=friction)
        self.add.margin(10, 10, 10, -1000)

        # Create balls
        self.spheres = []
        for _ in range(num_balls):
            pos = Vec(uniform(20, 780), uniform(20, 400))
            vel = Vec(uniform(-speed, speed), uniform(-speed, speed))
            bola = self.add.circle(radius=radius, vel=vel, pos=pos, mass=1,
                                   color='random')
            self.spheres.append(bola)

        # Create piston
        self.piston = self.add.aabb(11, 789, 420, 470, color=(150, 0, 0),
                                    mass=num_balls / 2, damping=5)

    @listen('long-press', 'q')
    def energy_up(self):
        """
        Increase energy of all particles.
        """

        for bola in self.spheres:
            bola.vel += 1 * bola.vel.normalize()

    @listen('long-press', 'a')
    def energy_down(self):
        """
        Decrease energy of all particles.
        """

        for bola in self.spheres:
            bola.vel *= 0.98

    @listen('key-down', 'space')
    def toggle_pause(self):
        super(Piston, self).toggle_pause()

    @listen('long-press', 'up', vec=Vec(0, 9))
    @listen('long-press', 'down', vec=Vec(0, -2))
    @listen('long-press', 'left', vec=Vec(-4, 0))
    @listen('long-press', 'right', vec=Vec(4, 0))
    def boost(self, vec):
        for bola in self.spheres:
            bola.vel += vec
            bola.vel *= 0.99


if __name__ == '__main__':
    game = Piston()
    game.run()
