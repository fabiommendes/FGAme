from FGAme import *

world.add.margin(10)
obj1 = world.add.regular_poly(N=3, length=130, pos=(200, 300),
                              vel=(500, 500), color='random', omega=2.2)
obj2 = world.add.regular_poly(N=5, length=100, pos=(200, 450), theta=pi / 4,
                              color='random')
obj3 = world.add.regular_poly(N=3, length=100, pos=(600, 300), theta=pi / 4,
                              color='random', mass='inf')


# Remove object after collision between obj2 and obj3
@obj3.listen('pre-collision')
def on_collision(col):
    if obj2 in col:
        col.cancel()
        obj3.destroy()
run()
