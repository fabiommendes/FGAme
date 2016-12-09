import pytest, os
from FGAme.world import World

def test_object_fail_to_set_image_with_wrong_path():
    w = World()
    with pytest.raises(RuntimeError):
        w.add.regular_poly(N=6, length=2.0, pos=(0,0), mass=1.0, image="no_such_image.png")

def test_object_set_image():
    w = World()
    w.add.regular_poly(N=6, length=2.0, pos=(0,0), mass=1.0, image=os.path.join(os.getcwd(), "src/FGAme/tests/fixtures/test.png"))
