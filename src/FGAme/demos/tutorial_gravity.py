from FGAme import *


class GravityWorld(World):

    def init(self):
        # Criamos dois objetos
        A = Circle(20, pos=pos.from_middle(100, 0), vel=(100, 300),
                   color='red')
        B = Circle(20, pos=pos.from_middle(-100, 0), vel=(-100, -300))
        self.A, self.B = A, B
        self.add([A, B])

        # Definimos a força de interação entre ambos
        K = self.K = A.mass
        self.A.force = lambda t: -K * (A.pos - B.pos)
        self.B.force = lambda t: -K * (B.pos - A.pos)

        # Redefinimos a constante de amortecimento
        self.damping = 0.5

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


if __name__ == '__main__':
    world = GravityWorld()
    world.run()
