# -*- coding: utf8 -*-

from __future__ import division
from math import sin, cos
from random import uniform
import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from kivy.graphics import Color, Ellipse

kv = '''
<WorldLayout>:
    canvas:
        Color:
            rgba: 0, 0, 1, 1
        Ellipse:
            pos: self.pos_circle
            size: 60, 60

    FloatLayout:
        ToggleButton:
            text: 'Run'
            size_hint_y: 0.1
            size_hint_x: 0.1
            on_press: root.animate()
'''
Builder.load_string(kv)


class WorldLayout(FloatLayout):
    pos_circle = ListProperty([400 - 30, 300 - 30])
    state = ListProperty([0, 1, 1, 0])
    omega = 20

    def update_world(self, dt):
        x, vx, y, vy = self.state
        x += vx * dt
        vx -= self.omega * x * dt
        y += vy * dt
        vy -= self.omega * y * dt
        self.state = [x, vx, y, vy]
        self.pos_circle = [200 * x + 400, 300 + 200 * y]

    def animate(self):
        Clock.schedule_interval(self.update_world, 1. / 60)


class WorldLayout(FloatLayout):
    pos_circle = ListProperty([400 - 30, 300 - 30])
    state = ListProperty([0, 1, 1, 0])
    omega = 20

    def __init__(self):
        super(WorldLayout, self).__init__()
        with self.canvas:
            Color(0, 0, 1)
            self.circle = Ellipse(pos=(370, 270), size=(60, 60))

    def update_world(self, dt):
        x, vx, y, vy = self.state
        x += vx * dt
        vx -= self.omega * x * dt
        y += vy * dt
        vy -= self.omega * y * dt
        self.state = [x, vx, y, vy]
        anim = Animation(pos=(200 * x + 400, 300 + 200 * y), duration=dt)
        anim.start(self.circle)

    def animate(self):
        Clock.schedule_interval(self.update_world, 1. / 20)


class RotationApp(App):

    def build(self):
        return WorldLayout()

if __name__ == '__main__':
    RotationApp().run()
