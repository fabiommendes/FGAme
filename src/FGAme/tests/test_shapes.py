import pytest
from FGAme.draw import *


@pytest.fixture
def shape(cls_args):
    '''Inicializa objetos'''
    
    cls, args, kwargs = cls_args
    return cls(*args, **kwargs)


@pytest.fixture(params=[
    [Segment, [(0, 0), (1, 1)], {}],
    [Path, [(0, 0), (1, 1), (1, 0)], {}],
    [AABB, (), dict(shape=(10, 20), pos=(5, 3))], 
    [Circle, (10,), {}],
    [Circuit, [(0, 0), (1, 1), (1, 0)], {}],
    [Poly, [(0, 0), (1, 1), (1, 0)], {}],
    [RegularPoly, [3, 10], {}],
    [Rectangle, (), dict(shape=(10, 20), pos=(5, 3))],
    [Triangle, [(0, 0), (1, 1), (1, 0)], {}],
])
def cls_args(request):
    '''Exemplos de classes com argumentos de inicialização'''
    return request.param


def test_shape_moves(shape):
    pos = shape.pos
    pos += (1, 1)
    shape.pos += (1, 1)
    assert abs(shape.pos - pos) < 1e-6


def test_shape_can_change_color(shape):
    shape.color
    shape.color = 'red'
    assert shape.color == (255, 0, 0)
    
    
def test_shape_can_change_linewidth(shape):
    shape.linewidth
    shape.linewidth = 2
    assert shape.linewidth == 2


def test_shape_can_define_color(cls_args):
    cls, args, kwds = cls_args
    shape = cls(*args, color='red', **kwds)
    assert shape.color == (255, 0, 0) 



if __name__ == "__main__":
    from os import system
    system('py.test test_shapes.py -q')