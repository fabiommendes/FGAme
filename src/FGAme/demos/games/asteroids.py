from FGAme import *
from FGAme.mathutils import convex_hull, pi
from random import normalvariate, uniform

###############################################################################
#                                 Tarefas
###############################################################################
#
# Nome/matrícula:
# Nome/matrícula:
#
# 1) Completar o reposicionamento dos asteróids nas quatro direções
#    dentro da função force_bounds()
# 2) Implementar o movimento da nave nas quatro direções dentro das funções
#    ship_left/right/front/back
# 3) Implementar parcialmente o tiro (apenas uma bolinha saindo da nave, sem
#    qualquer outro efeito). Modifique a função on_shot()

###############################################################################
#                           Constantes do jogo
###############################################################################
ASTEROIDS_COLOR = (200, 200, 200)
ASTEROIDS_SPEED = 50
ASTEROIDS_RADIUS = 20
WIDTH = 800
HEIGHT = 600

###############################################################################
#                             Implementação
###############################################################################


class Asteroids(World):

    '''Define uma fase do jogo Asteroids'''

    def __init__(self, num_asteroids=7):
        World.__init__(self, background='black')

        # Cria asteróides
        self.asteroids = [self.new_asteroid(ASTEROIDS_RADIUS, world=self)
                          for _ in range(num_asteroids)]

        # Cria a nave
        vertices = [(0, 0), (20, 0), (10, 30)]
        self.spaceship = Poly(vertices, color='red', pos=pos.middle)
        self.add(self.spaceship)
        self.spaceship.listen('collision', self.on_ship_collision)

    def new_asteroid(self,
                     radius,
                     mean_speed=ASTEROIDS_SPEED,
                     color=ASTEROIDS_COLOR, **kwds):
        '''Cria um novo asteróide'''

        # Sorteadores de números aleatórios
        g = normalvariate
        r = uniform

        # Sorteia vertices
        points = [(g(0, radius), g(0, radius)) for _ in range(20)]
        points = convex_hull(points)

        # Sorteia posições e velocidades
        pos = (r(0, WIDTH), r(0, HEIGHT))
        vel = (g(0, mean_speed), g(0, mean_speed))

        # Cria um polígono
        res = Poly(points, vel=vel, pos=pos, color=color, **kwds)
        res.is_asteroid = True
        return res

    @listen("frame-enter")
    def force_bounds(self):
        '''Executado a cada frame: testa todos os asteroids para ver se saíram
        da tela. Em caso positivo, eles são recolocados do lado oposto'''

        self.asteroids.append(self.spaceship)
        for asteroid in self.asteroids:
            # Parede de cima
            if asteroid.ymin > HEIGHT:
                asteroid.move((0, -HEIGHT - asteroid.height))

            # Parede de baixo
            elif asteroid.ymax < 0:
                asteroid.move((0, HEIGHT + asteroid.height))

            # Parede da direita
            elif asteroid.xmin > WIDTH:
                asteroid.move((-WIDTH - asteroid.width, 0))

            # Parede da esquerda
            elif asteroid.xmax < 0:
                asteroid.move((WIDTH + asteroid.width, 0))

        self.asteroids.pop()

        # Cria viscosidade para a nave
        ship = self.spaceship
        ship.aboost(-0.01 * ship.omega)
        ship.boost(-0.01 * ship.vel)

    @listen('long-press', 'right', -0.1)
    @listen('long-press', 'left', 0.1)
    def ship_rotate(self, dtheta):
        ship = self.spaceship
        ship.aboost(dtheta)

    @listen('long-press', 'down', -10)
    @listen('long-press', 'up', 20)
    def ship_front(self, desc):
        ship = self.spaceship
        u = (ship.vertices[2] - ship.pos).normalize()
        self.spaceship.boost(u * desc)

    @listen('key-down', 'space')
    def on_shot(self):
        ship = self.spaceship
        pos = ship.vertices[2]
        vel = 200 * (pos - ship.pos).normalize() + ship.vel
        Circle(2, pos=pos, vel=vel, color='white', world=self)

    @listen('collision')
    def on_ship_collision(self, col):
        other = col.other(self.spaceship)
        print(other)
        other.color = 'red'


if __name__ == '__main__':
    game = Asteroids()
    game.run()
