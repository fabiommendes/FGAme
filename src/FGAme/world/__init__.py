from .state_objects import PosObject as _pos_class
from .state_objects import VelObject as _vel_class
from .world import World

world = World()
pos = _pos_class()
vel = _vel_class()
