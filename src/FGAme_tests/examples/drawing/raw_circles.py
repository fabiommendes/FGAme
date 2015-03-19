#-*-coding: utf8 -*-
from FGAme import draw, PyGameCanvas
from time import sleep

# Cria a árvore de renderização com vários círculos
p0 = (400, 300)
tree = draw.RenderTree()
tree.add(draw.Circle(p0, 150, color='red'))
tree.add(draw.Circle(p0, 120, color='white'))
tree.add(draw.Circle(p0, 100, color='red'))
tree.add(draw.Circle(p0, 70, color='white'))
tree.add(draw.Circle(p0, 50, color='red'))

# Cria um objeto Canvas com a geometria da tela
canvas = PyGameCanvas(800, 600)

# Loop principal
for i in range(50):
    canvas.clear_background()
    canvas.draw_tree(tree)
    canvas.flip()
    sleep(0.01)