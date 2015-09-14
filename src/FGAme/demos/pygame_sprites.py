'''
Created on 18/06/2015

@author: chips
'''
from FGAme import *
conf.set_backend('pygame')
import pygame
import smallshapes as shapes
from random import random

world = World()
Circle(20, (500, 500), world=world)

# Cria a caixa e a imagem associada
imgs = [pygame.image.load('resources/alien%s.gif' % i) for i in range(1, 4)]
_x, _y, dx, dy = imgs[0].get_rect()
box = AABB(0, dx, 0, dy, color=None, world=world)

# Move o macaco de acordo com as setas
world.listen('long-press', 'left')(lambda: box.move((-2, 0)))
world.listen('long-press', 'right')(lambda: box.move((4, 0)))
world.listen('long-press', 'up')(lambda: box.move((0, 2)))
world.listen('long-press', 'down')(lambda: box.move((0, -2)))
idx = 0


@world.listen('pre-draw')
def draw_sprite(screen):
    '''Recebe um objeto do tipo Screen e realiza desenhos na tela'''

    global idx
    idx += 0.1

    dx, dy = box.shape
    screen.draw_circle(shapes.Circle(40, Vec2(400, 300)))

    # Recupera o Surface para utilizar manualmente as funções do pygame
    pg_screen = screen.get_pygame_screen()
    pg_screen.blit(imgs[int(idx % 3)], (box.xmin, 600 - box.ymax, dx, dy))


@world.listen('key-down', 'space')
def shoot():
    world.add(Circle(3, vel=(200, 200 * random() - 100), pos=box.pos_right))

world.run()
