from FGAme import World, Circle, AABB, Vec, listen
from random import uniform


class Gas(World):
    """
    Simulation of a gas of hard spheres subject to the force of gravity.
    """

    def __init__(self,
                 gravity=100, friction=0.0, restitution=0.95,
                 num_balls=80, speed=200, radius=10,
                 color='random'):
        self.num_balls = num_balls
        self.radius = radius
        self.speed = speed

        super(Gas, self).__init__(gravity=gravity, friction=friction,
                                  restitution=restitution)

    def init(self):
        self.add.margin(10, 10, 10, -10000)
        speed = self.speed
        for _ in range(self.num_balls):
            self.add.circle(
                radius=self.radius,
                vel=Vec(uniform(-speed, speed), uniform(-speed, speed)),
                pos=Vec(uniform(50, 750), uniform(50, 400)),
                color='random',
            )

    @listen('key-down', 'space')
    def toggle_pause(self):
        super(Gas, self).toggle_pause()

# Start simulation
if __name__ == '__main__':
    w = Gas()
    w.run()
