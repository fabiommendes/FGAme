#-*-coding: utf8 -*-

from FGAme import draw, conf
from time import sleep

# Cria a árvore de renderização com vários círculos
p0 = (400, 300)
tree = draw.RenderTree()
tree.add(draw.Circle(150, p0, color='red'))
tree.add(draw.Circle(120, p0, color='white'))
tree.add(draw.Circle(100, p0, color='red'))
tree.add(draw.Circle(70, p0, color='white'))
tree.add(draw.Circle(50, p0, color='red', line_color='black', line_width=10))

# Cria um objeto Canvas com a geometria da tela
canvas = conf.init_screen(800, 600)
canvas.show()

# Loop principal
for i in range(50):
    canvas.clear_background('white')
    canvas.draw(tree)
    canvas.flip()
    sleep(0.01)