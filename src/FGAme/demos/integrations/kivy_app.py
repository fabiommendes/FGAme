import random

from FGAme import *

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse, Rectangle


# Create FGAme world as usual
class TestWorld(World):
    """
    A simple simulation with many circles.
    """

    def __init__(self, N, **kwargs):
        super().__init__(gravity=300, **kwargs)
        self.circles = [
            self.add.circle(random.uniform(20, 35),
                            pos=pos.random(40),
                            vel=vel.random(),
                            color='random')
            for _ in range(N)
        ]
        self.add.margin()


class FGAmeWorld(FloatLayout):
    """
    Wraps an FGAme World built with circles.
    """

    def __init__(self, N):
        conf.set_backend('testing')
        self._circle_map = {}
        self.fgame_world = TestWorld(N)
        super().__init__()

        with self.canvas:
            Color(255, 255, 255)
            Rectangle(pos=(0, 0), size=(800, 600))

            for c in self.fgame_world.circles:
                d = 2 * c.radius
                Color(*c.color.rgbf)
                kcircle = Ellipse(pos=c.pos_sw, size=(d, d))
                self._circle_map[c] = kcircle

        Clock.schedule_interval(self.update_world, 1. / 60)

    def update_world(self, dt):
        self.fgame_world.update(dt)
        for fgame, kv in self._circle_map.items():
            kv.pos = fgame.pos_sw


class FGAmeApp(App):
    """
    Kivy App that runs FGAme simulation.
    """

    def __init__(self, size):
        self.size = size
        super().__init__()

    def build(self):
        return FGAmeWorld(self.size)


if __name__ == '__main__':
    FGAmeApp(50).run()
