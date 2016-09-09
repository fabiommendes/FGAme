from FGAme import draw, conf
from time import sleep

# Render tree with circles
p0 = (400, 300)
tree = draw.RenderTree()
tree.add(draw.Circle(150, p0, color='red'))
tree.add(draw.Circle(120, p0, color='white'))
tree.add(draw.Circle(100, p0, color='red'))
tree.add(draw.Circle(70, p0, color='white'))
tree.add(draw.Circle(50, p0, color='red', linecolor='black', linewidth=10))

# Start screen
canvas = conf.init_screen(800, 600)
canvas.show()

# Main loop
for i in range(50):
    canvas.clear_background('white')
    canvas.draw(tree)
    canvas.flip()
    sleep(0.01)
