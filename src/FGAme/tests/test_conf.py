import pytest
from FGAme.backends import get_backend_classes
from FGAme.backends import testing_be
from FGAme import conf


def test_find_correct_backend_classes():
    D = get_backend_classes('testing')
    assert D == {
        'input': testing_be.EmptyInput,
        'mainloop': testing_be.MainLoop,
        'screen': testing_be.EmptyCanvas,
    }


@pytest.mark.pygame
def test_find_pygame_backend():
    from FGAme.backends import pygame_be

    D = get_backend_classes('pygame')
    assert D == {
        'input': pygame_be.PyGameInput,
        'mainloop': pygame_be.PyGameMainLoop,
        'screen': pygame_be.PyGameCanvas,
    }

def test_show_screen():
    conf.show_screen()
    assert conf._screen_object

def test_set_resolution():
    conf.set_resolution(800,600)
    screen = conf.get_screen()
    assert screen.width == 800
    assert screen.height == 600

def test_set_resolution_fullscreen():
    with pytest.raises(Exception):
        conf.set_resolution('fullscreen')

def test_set_resolution_already_defined():
    with pytest.raises(Exception):
        conf.set_resolution(400,400)

def test_set_framerate():
    value = 30
    conf.set_framerate(value)
    assert conf._physics_fps == value
    assert conf._physics_dt == 1/value

def test_get_framerate():
    assert conf._physics_fps == 30

def test_set_frame_duration():
    value = 1
    conf.set_frame_duration(value)
    assert conf._physics_fps == value
    assert conf._physics_dt == 1/value

def test_get_frame_duration():
    assert conf._physics_dt == 1

def test_get_backend():
    backend = conf.get_backend()
    assert backend == 'testing'
