from FGAme import conf
from FGAme import draw

screen = conf.init_screen(800, 600)
assert screen is conf.get_screen()
screen.show()

circle = draw.Circle(100, color='red')
screen.draw(circle)
screen.flip()


c1 = draw.Circle(50, pos=(400, 300), color='black')
c2 = draw.Circle(30, pos=(400, 300), color='white')
with screen.painting():
    screen.draw(c1)
    screen.draw(c2)