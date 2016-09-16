import pytest
from FGAme.backends import get_backend_classes
from FGAme.backends import testing_be


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
