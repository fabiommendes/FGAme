from random import uniform, choice

from FGAme import *


class Pong(World):
    def __init__(self, **kwds):
        super(Pong, self).__init__()
        self.add.margin(-300, 10)

        # Central line
        self.add(draw.AABB(shape=(15, 550), pos=(400, 300),
                           color=(200, 200, 200)))

        # Create ball with a random speed
        self.ball = self.add.circle(30, color='red')
        self.ball.pos = (100, 300)
        self.ball.vel = (+700, choice([-1, 1]) * uniform(200, 400))

        # Create bars
        self.pong0 = self.add.aabb(shape=[20, 130], pos=(750, 300), mass='inf')
        self.pong1 = self.add.aabb(shape=[20, 130], pos=(50, 300), mass='inf')
        self.objects = [self.pong0, self.pong1]

        # Register events
        self.listen('key-down', 'space', function=self.toggle_pause)

    @listen('long-press', 'up', obj=0)
    @listen('long-press', 'w', obj=1)
    def move_up(self, obj):
        obj = self.objects[obj]
        if obj.ymax < 590:
            obj.move(Vec(0, 10))

    @listen('long-press', 'down', obj=0)
    @listen('long-press', 's', obj=1)
    def move_down(self, obj):
        obj = self.objects[obj]
        if obj.ymin > 10:
            obj.move(Vec(0, -10))


if __name__ == '__main__':
    Pong().run()
