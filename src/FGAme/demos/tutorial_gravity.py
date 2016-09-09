from FGAme import *


class GravityWorld(World):
    def init(self):
        # Create two planets
        self.a = a = self.add.circle(20, pos=pos.from_middle(100, 0), vel=(100, 300), color='red')
        self.b = b = self.add.circle(20, pos=pos.from_middle(-100, 0), vel=(-100, -300))

        # Interaction force
        k = self.k = a.mass
        self.a.force = lambda t: -k * (a.pos - b.pos)
        self.b.force = lambda t: -k * (b.pos - a.pos)
        self.damping = 0.5

        # Bounds
        self.add.bounds(10)

    @listen('key-down', 'space')
    def toggle(self):
        self.toggle_pause()

    @listen('long-press', 'right')
    def move_right(self):
        self.a.move(5, 0)

    @listen('long-press', 'left')
    def move_left(self):
        self.a.move(-5, 0)

    @listen('long-press', 'up')
    def move_up(self):
        self.a.move(0, 5)

    @listen('long-press', 'down')
    def move_down(self):
        self.a.move(0, -5)

    @listen('mouse-button-down', 'left')
    def add_circle(self, pos):
        self.pause()
        self.circle = Circle(20, pos=pos, color='random')
        self.line = draw.Segment(pos, pos)
        self.add([self.circle, self.line])

    @listen('mouse-long-press', 'left')
    def set_circle_velocity(self, pos):
        self.line.end = pos

    @listen('mouse-button-up', 'left')
    def launch_circle(self, pos):
        self.resume()
        self.remove(self.line)
        self.circle.boost(4 * self.line.direction)


if __name__ == '__main__':
    world = GravityWorld()
    world.run()
