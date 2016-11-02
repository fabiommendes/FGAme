from FGAme.asset import Asset
from FGAme.configuration import conf
from FGAme.signals import global_signal as _signal
from FGAme.utils import lru_cache

music_ended_signal = _signal('music-ended', ['sound'])
sfx_ended_signal = _signal('music-ended', ['sound'])


class Sound(Asset):
    """
    Common functionality for SFX and Music.
    """

    extensions = ['.wav', '.ogg', '.mp3']
    _has_init = False

    @property
    def volume(self):
        return self._get_volume()

    @volume.setter
    def volume(self, value):
        self._set_volume(value)

    @classmethod
    def init(cls):
        """
        Init sound subsystem.
        """

        if not cls._has_init:
            cls._init()

    @classmethod
    def close(cls):
        """
        Closes sound subsystem.
        """

        if cls._has_init:
            cls._close()

    @classmethod
    def has_init(cls):
        """
        Return True if sound subsystem has been initialized.
        """

        return cls._has_init

    def __init__(self, name):
        super().__init__(name)

        # Hardcoded pygame defaults :(
        self.is_stereo = True
        self.is_playing = False
        self.repeat = False
        self.frequency = 22050
        self.bitdepth = 16

    def play(self, repeat=False):
        """
        Play sound
        """

        if not self.is_playing:
            self.init()
            self._play()
            self.is_playing = True
        self.repeat = repeat

    def stop(self):
        """
        Stop mixer.
        """

        if self.is_playing:
            self._stop()
            self.is_playing = False

    def pause(self):
        """
        Pause execution. Execute .play() to resume.
        """

        if self.is_playing:
            self._pause()
            self.is_playing = False

    def resume(self):
        """
        Resume playback of a paused stream.
        """

        if not self.is_playing:
            self._resume()
            self.is_playing = True

    #
    # Pygame backend methods. Refactor this to make it backend agnostic.
    #
    @classmethod
    def _pygame(cls):
        import pygame
        return pygame

    @classmethod
    def _init(cls):
        cls._pygame().mixer.init(22050, 16, 2)

    @classmethod
    def _close(cls):
        cls._pygame().mixer.quit()

    def _get_sound(self):
        self.init()
        if not hasattr(self, '_sound'):
            self._sound = self._pygame().mixer.Sound(self.path)
        return self._sound

    def _play(self):
        self._get_sound().play()

    def _stop(self):
        self._get_sound().stop()

    def _pause(self):
        self._get_sound().stop()  # no pause for SFX

    def _resume(self):
        self._get_sound().play()

    def _get_volume(self):
        return self._get_sound().get_volume()

    def _set_volume(self, value):
        self._get_sound().set_volume(value)


class SFX(Sound):
    """
    Sound effect.
    """

    file_type = 'sfx'
    _active = set()
    _paused = set()

    @classmethod
    def stop_all(cls):
        """
        Stops playback of all SFX instances.
        """

        for sfx in cls._active:
            sfx.stop()

    @classmethod
    def resume_all(cls):
        """
        Resumes playback of all SFX instances.
        """

        for sfx in cls._paused:
            sfx.resume()

    @classmethod
    def pause_all(cls):
        """
        Pause playback of all active SFX instances.
        """

        for sfx in cls._active:
            sfx.pause()

    def play(self, repeat=False):
        super().play(repeat)
        self._active.add(self)


class Music(Sound):
    """
    For soundtrack.

    Music is a single stream system and cannot be mixed. Only a single music
    object can be active at a time.
    """

    file_type = 'music'
    _active = None
    _volume = 1

    @classmethod
    def active(cls):
        """
        Return the current active Music object or None if no stream is active.
        """

        return cls._active

    def play(self, repeat=True, force=True):
        if self._active not in (None, self):
            if not force:
                raise self._blocked_stream_error()
            self._active.stop()
        super().play(repeat=repeat)
        type(self)._active = self

    def stop(self):
        super().stop()
        if self._active is self:
            self._active = None

    def _music(self):
        return self._pygame().mixer.music

    def _play(self):
        music = self._music()
        music.load(self.path)
        music.set_volume(self.volume)
        music.play(-1)

    def _stop(self):
        self._music().stop()

    def _pause(self):
        self._music().pause()

    def _resume(self):
        self._music().unpause()

    def _blocked_stream_error(self):
        return RuntimeError('music stream is already blocked by %s' % self)

    def _get_volume(self):
        return self._volume

    def _set_volume(self, value):
        self._volume = value


@lru_cache
def get_sfx(name):
    """
    Return the SFX instance with the given name.
    """

    if isinstance(name, SFX):
        return name
    return conf.sfx_class(name)


@lru_cache
def get_music(name):
    """
    Return Music instance with the given name.
    """

    if isinstance(name, Music):
        return name
    return conf.music_class(name)


def play(name, volume=1, **kwargs):
    """
    Plays a sound file with the given name.

    Returns the corresponding SFX() object that can be used to pause, stop and
    control playback.

    Args:
        name:
            Name of the sound file without extensions. Sound assets must be
            at the assets/sfx/<filename>.ext path.
        volume:
            Playback volume (between 0 and 1).
    """

    sound = get_sfx(name)
    sound.volume = volume
    sound.play(**kwargs)
    return sound


def music(name, volume=1, **kwargs):
    """
    Like play(), but sets the background music. Differently from sound effects,
    a single music channel is allowed at any given time. This function will
    disable any music playback and replace by the given.

    This function accepts the same arguments as play().
    """

    sound = get_music(name)
    sound.volume = volume
    sound.play(**kwargs)
    return sound


def stop_sfx():
    """
    Stop all sound effects.
    """

    conf.sfx_class.stop_all()


def stop_music():
    """
    Stops all music playback.
    """

    if conf.music_class._active is not None:
        conf.music_class._active.stop()


def mute():
    """
    Disable all sound.
    """

    stop_music()
    stop_sfx()
