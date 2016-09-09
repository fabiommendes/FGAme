# -*- coding: utf8 -*-
import pytest
from FGAme.draw import Color


def test_color_compares_with_tuple():
    color = Color('red')
    assert color == (255, 0, 0, 255)
    assert color == (255, 0, 0) 


def test_init_color_from_string():
    assert Color('red') == (255, 0, 0)
    assert Color('lime') == (0, 255, 0)  # HTML name convention...
    assert Color('blue') == (0, 0, 255) 
    assert Color('#0F0') == (0, 255, 0)
    assert Color('#00FF00') == (0, 255, 0)
    assert Color('#00FF00', alpha=128) == (0, 255, 0, 128)


def test_init_color_from_color():
    black = Color('black')
    assert Color(black) == black
    

if __name__ == "__main__":
    from os import system
    system('py.test test_color.py -q')