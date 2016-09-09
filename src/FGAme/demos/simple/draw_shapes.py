from FGAme import conf, pi
from FGAme.draw import *
from time import sleep

# Render tree
p0 = (400, 300)
tree = RenderTree()
tree.add(Circle(150, p0, color='red', linewidth=10.0, linecolor='blue'))
tree.add(Rectangle(rect=(100, 100, 200, 200), theta=pi / 3, color='blue'))
tree.add(Poly([(400, 200), (800, 200), (600, 500)], color='black'))
tree.add(Segment((0, 0), (800, 600), color='red', width=20))
tree.add(Path([(0, 0), (200, 300), (300, 50), (800, 600)],
              color='red', width=20))

# Canvas object
canvas = conf.init_screen(800, 600)
canvas.show()
white = Color('white')

# Main loop
for i in range(50):
    canvas.clear_background(white)
    canvas.draw(tree)
    canvas.flip()
    sleep(0.05)
