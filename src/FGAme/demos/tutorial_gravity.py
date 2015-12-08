from FGAme import *


class GravityWorld(World):

    def init(self):
        # criamos dois objetos
        a = Circle(20, pos=pos.from_middle(100, 0), vel=(100, 300),
                   color='red')
        b = Circle(20, pos=pos.from_middle(-100, 0), vel=(-100, -300))
        self.a, self.b = a, b
        self.add([a, b])

        # definimos a força de interação entre ambos
        k = self.k = a.mass
        self.a.force = lambda t: -k * (a.pos - b.pos)
        self.b.force = lambda t: -k * (b.pos - a.pos)

        def func(t):
            raise TypeError

        self.a.func = func
        self.b.func = func

        # redefinimos a constante de amortecimento
        self.damping = 0.5

        # definimos uma margem de 10px de espessura
        self.add_bounds(width=10)

    @listen('key-down', 'space')
    def toggle(self):
        self.toggle_pause()

    @listen('long-press', 'right')
    def move_right(self):
        self.A.move(5, 0)

    @listen('long-press', 'left')
    def move_left(self):
        self.A.move(-5, 0)

    @listen('long-press', 'up')
    def move_up(self):
        self.A.move(0, 5)

    @listen('long-press', 'down')
    def move_down(self):
        self.A.move(0, -5)

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
        self.unpause()
        self.remove(self.line)
        self.circle.boost(4 * self.line.direction)

if __name__ == '__main__':
    from FGAme import camera
    world = GravityWorld()
    world.run()
