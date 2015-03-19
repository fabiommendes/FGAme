#-*-coding: utf8 -*-
from FGAme import PyGameCanvas
from FGAme.draw import *
from time import sleep

# Cria a árvore de renderização com vários círculos
p0 = (400, 300)
tree = RenderTree()
tree.add(Circle(p0, 150, color='red'))
tree.add(RectangleAA((100, 100, 200, 200), color='blue'))
tree.add(Poly([(400, 200), (800, 200), (600, 500)], color='black'))

# Cria um objeto Canvas com a geometria da tela
canvas = PyGameCanvas(800, 600)

# Loop principal
for i in range(50):
    canvas.clear_background()
    canvas.draw_tree(tree)
    canvas.flip()
    sleep(0.01)