import pytest

from smallshapes.tests import abstract as base
from FGAme import draw


class TestDrawable:
    pass


class TestShape(base.DisableMutabilityTests, TestDrawable, base.TestShape):
    @pytest.fixture
    def mutable(self, obj):
        return obj

    def test_default_line_color_is_black(self, obj):
        assert isinstance(obj.linecolor, draw.Color)
        assert isinstance(obj.color, draw.Color)
        assert obj.linecolor == draw.Color('black')
        assert obj.color == draw.Color('black')

    def test_can_define_line_color(self, cls, args):
        obj = cls(*args, linecolor='red')
        assert obj.linecolor == (255, 0, 0)

    def test_can_define_line_width(self, cls, args):
        obj = cls(*args, linewidth=2)
        assert obj.linewidth == 2


class TestSolid(TestShape, base.TestSolid):
    def test_default_fill_color_is_black(self, obj):
        assert isinstance(obj.fillcolor, draw.Color)
        assert isinstance(obj.color, draw.Color)
        assert obj.fillcolor == draw.Color('black')
        assert obj.color == draw.Color('black')

    def test_can_define_fill_color(self, cls, args):
        obj = cls(*args, fillcolor='red')
        assert obj.fillcolor == (255, 0, 0)

