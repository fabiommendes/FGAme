import pytest

from FGAme.sound import play, music, mute, SFX, Music


@pytest.fixture
def sfx():
    return SFX('laser-blaster')


@pytest.fixture
def song():
    return Music('laser-blaster')


def test_can_play_sfx():
    sound = play('laser-blaster')
    assert sound.is_playing
    assert sound.volume == 1
    sound.stop()


def test_can_pause_sfx(sfx):
    sfx.play()
    assert sfx.is_playing
    sfx.pause()
    assert not sfx.is_playing
    sfx.resume()
    assert sfx.is_playing
    sfx.stop()
    assert not sfx.is_playing


def test_can_pause_music(song):
    song.play()
    assert song.is_playing
    song.pause()
    assert not song.is_playing
    song.resume()
    assert song.is_playing
    song.stop()
    assert not song.is_playing


def test_can_play_music():
    sound = music('laser-blaster')
    assert sound.is_playing
    assert sound.volume == 1
    sound.stop()


def test_mute_sounds():
    sfx = play('laser-blaster')
    song = music('laser-blaster')
    assert Music._active is song
    mute()
    assert not sfx.is_playing
    assert not song.is_playing
