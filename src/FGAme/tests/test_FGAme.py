import pytest
import FGAme


def test_project_defines_author_and_version():
    assert hasattr(FGAme, '__author__')
    assert hasattr(FGAme, '__version__')
