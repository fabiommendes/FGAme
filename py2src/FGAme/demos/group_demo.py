# -*- coding: utf8 -*-
from FGAme import *


w = World()
g = Group([Circle(10), Circle(10, pos=(10, 10), color='red')])
w.add(g)
w.run()