import os

import pytest

from FGAme.asset import Asset


@pytest.fixture
def asset():
    return Asset('laser-blaster', 'sfx', extensions=['.wav', '.ogg'])


def test_can_find_sound_asset(asset):
    assert asset.file_type == 'sfx'
    assert asset.is_valid
    assert asset.name == 'laser-blaster'
    assert os.path.exists(asset.path)


def test_invalid_asset():
    asset = Asset('foo-bar', 'bad', extensions=['.bad'])
    assert not asset.is_valid
    assert asset.path is None


def test_asset_repr(asset):
    assert repr(asset) == "Asset('laser-blaster')"


def test_can_open_asset(asset):
    with asset as F:
        F.read()