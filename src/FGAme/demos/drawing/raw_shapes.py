#-*-coding: utf8 -*-
from FGAme import conf, pi
from FGAme.draw import *
from time import sleep

# Cria a árvore de renderização com vários círculos
p0 = (400, 300)
tree = RenderTree()
tree.add(Circle(150, p0, color='red', line_width=10.0, line_color='blue'))
tree.add(Rectangle(rect=(100, 100, 200, 200), theta=pi / 3, color='blue'))
tree.add(Poly([(400, 200), (800, 200), (600, 500)], color='black'))
tree.add(Segment((0, 0), (800, 600), color='red', width=20))
tree.add(
    Path([(0, 0), (200, 300), (300, 50), (800, 600)], color='red', width=20))

# Cria um objeto Canvas com a geometria da tela
canvas = conf.init_screen(800, 600)
canvas.show()
white = Color('white')

# Loop principal
for i in range(50):
    canvas.clear_background(white)
    canvas.draw(tree)
    canvas.flip()
    sleep(0.05)
