# -*- coding: utf8 -*-

from FGAme import *
from random import uniform

import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout

#=========================================================================
# Cria o mundo
#=========================================================================
rv = lambda: (uniform(-400, 400), uniform(-400, 400))
rp = lambda: (uniform(0, 800), uniform(0, 600))
world = World(background=(0, 0, 0))
world.add_bounds(0, 800, 0, 600)
c1 = Circle(30, vel=rv(), world=world, color='blue')
c2 = Circle(20, vel=rv(), pos=rp(), world=world, color='red')
c3 = Circle(50, vel=rv(), pos=rp(), world=world, color='white')
c4 = Circle(30, vel=rv(), pos=rp(), world=world, color=(0, 255, 0))
c5 = Circle(30, vel=rv(), pos=rp(), world=world, color=(255, 255, 0))
circles = [c1, c2, c3, c4, c5]
world.listen('key-down', 'space', world.stop)
# world.run()


from kivy.graphics import Color, Ellipse, Rectangle

#=========================================================================
# Cria a aplicação kivy
#=========================================================================
kv = '''
<WorldLayout>:
    FloatLayout:
        ToggleButton:
            text: 'Run'
            size_hint_y: 0.1
            size_hint_x: 0.1
            on_press: root.animate()
'''
Builder.load_string(kv)


class WorldLayout(FloatLayout):

    def __init__(self):
        self._instructions = {}
        super(WorldLayout, self).__init__()

        with self.canvas:
            Color(0, 0, 0)
            Rectangle(pos=(0, 0), size=(800, 600))

            for c in circles:
                r = 2 * c.radius
                Color(*c.color.f_rgb)
                kcircle = Ellipse(pos=c.pos_sw, size=(r, r))
                self._instructions[c] = kcircle

    def update_world(self, dt):
        world.update(dt)
        for c, kv in self._instructions.items():
            kv.pos = c.pos_sw

    def animate(self):
        Clock.schedule_interval(self.update_world, 1. / 60)


class RotationApp(App):

    def build(self):
        return WorldLayout()

if __name__ == '__main__':
    RotationApp().run()
