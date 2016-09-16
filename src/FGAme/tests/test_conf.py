from FGAme.backends import get_backend_classes
from FGAme.backends import pygame_be


def test_find_correct_backend_classes():
    D = get_backend_classes('pygame')
    assert D == {
        'input': pygame_be.PyGameInput,
        'mainloop': pygame_be.PyGameMainLoop,
        'screen': pygame_be.PyGameCanvas
    }
