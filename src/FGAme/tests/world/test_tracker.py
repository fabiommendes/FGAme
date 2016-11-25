import pytest
from FGAme.world.tracker import Tracker
from FGAme.world.world import World

def test_tracker_energy_tracker_not_none():
    w = World()
    t = Tracker(w)
    assert t.energy()

def test_energy_tracker_method():
    w = World()
    w._simulation._kinetic0 = 1.0
    w._simulation._potential0 = 1.0
    w._simulation._interaction0 = 1.0
    t = Tracker(w)
    e1 = t.energy()
    e2 = w.track.energy()
    assert e1() == e2()

def test_energy_tracker_raises_division_by_zero():
    w = World()
    w._simulation._kinetic0 = 0
    w._simulation._potential0 = 0
    w._simulation._interaction0 = 0
    e1 = w.track.energy()
    with pytest.raises(ZeroDivisionError):
        e1()

def test_energy_tracker_default_kinetic_energy():
    w = World()
    w._simulation._kinetic0 = None
    w._simulation._potential0 = 0
    w._simulation._interaction0 = 0
    e1 = w.track.energy()
    assert e1() == None
