#-*- coding: utf8 -*-
from FGAme import *
from random import uniform
import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ListProperty
from kivy.uix.floatlayout import FloatLayout

#===============================================================================
# Cria o mundo
#===============================================================================
rv = lambda: (uniform(-400, 400), uniform(-400, 400))
rp = lambda: (uniform(-400, 400), uniform(-300, 300))
world = World(background=(0, 0, 0))
world.set_bounds(-400, 400, -300, 300)
c1 = Circle(30, vel=rv(), world=world, color='blue')
c2 = Circle(20, vel=rv(), pos=rp(), world=world, color='red')
c3 = Circle(50, vel=rv(), pos=rp(), world=world, color='white')
c4 = Circle(30, vel=rv(), pos=rp(), world=world, color=(0, 255, 0))
c5 = Circle(30, vel=rv(), pos=rp(), world=world, color=(255, 255, 0))
world.listen('key-down', 'space', world.stop)
#world.run()

#===============================================================================
# Cria a aplicação kivy
#===============================================================================
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


    def update_world(self, dt):
        world.update(dt)
        self.pos1 = list(c1.pos + [400 - 30, 300 - 30])
        self.pos2 = list(c2.pos + [400 - 20, 300 - 20])
        self.pos3 = list(c3.pos + [400 - 50, 300 - 50])
        self.pos4 = list(c4.pos + [400 - 30, 300 - 30])
        self.pos5 = list(c5.pos + [400 - 30, 300 - 30])

    def animate(self):
        Clock.schedule_interval(self.update_world, 1. / 60)

class RotationApp(App):
    def build(self):
        return WorldLayout()

if __name__ == '__main__':
    RotationApp().run()
