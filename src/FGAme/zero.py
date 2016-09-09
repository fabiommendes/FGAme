import inspect
import sys

from lazyutils import lazy

from FGAme import listen
from FGAme.configuration import conf
from FGAme.world.world import get_last_world_instance

__all__ = ['run', 'start']


def run():
    """
    Start FGAme simulation in the foreground.
    """

    runner = Runner.from_frame()
    runner.run()


def start():
    """
    Start FGAme simulation in the background.
    """

    runner = Runner.from_frame()
    runner.start()


class Runner:
    """
    Runner for FGAme zero.
    """

    @lazy
    def world(self):
        return get_last_world_instance()

    @classmethod
    def from_frame(cls, frame=None):
        """
        Initializes Runner from frame object.
        """

        if frame is None:
            frame = sys._getframe()
        frame_start = frame
        while frame:
            if frame.f_globals['__name__'] == '__main__':
                return cls(frame.f_globals)
            frame = frame.f_back
        raise RuntimeError('could not find __main__ module')

    def __init__(self, ns=None):
        self.namespace = dict(ns or {})

    def run(self):
        """
        Start mainloop.
        """

        self.prepare()
        self.world.run()

    def start(self):
        """
        Start mainloop in a separate thread.

        Do not block execution.
        """

        self.prepare()
        self.world.start()

    def prepare(self):
        """
        Prepare runner for execution.
        """

        self.register_conf_constants()
        self.register_update_function()
        self.register_callbacks()

    def register_conf_constants(self, data=None):
        """
        Introspect all configuration constants such as HEIGHT, WIDTH, etc and
        set the corresponding configuration setting.

        Supported constants:
            WIDTH, HEIGHT: screen resolution
            BACKEND: FGAme backend (pygame, kivy, etc)
        """

        data = self.namespace if data is None else self.namespace
        WIDTH = data.get('WIDTH')
        HEIGHT = data.get('HEIGHT')
        BACKEND = data.get('BACKEND')

        if WIDTH is not None and HEIGHT is not None:
            conf.set_resolution(WIDTH, HEIGHT)
        if BACKEND:
            conf.set_backend(BACKEND)

    def register_callbacks(self, data=None):
        """
        Find all functions with special name linked to events and connect them
        to their respective events.
        """

        data = self.namespace if data is None else self.namespace

        # def connect(name, signal):
        #     if name in data:
        #         signal.connect(data[name])
        #
        # # Generic signals
        # connect('on_frame_enter', signals.frame_enter_signal)
        # connect('on_frame_leave', signals.frame_leave_signal)

    def register_update_function(self, data=None):
        """
        Register update function.
        """

        data = self.namespace if data is None else self.namespace
        if 'update' in data:
            func = data['update']
            args = inspect.getargspec(func).args
            if args and args[0] == 'dt':
                callback = func
            else:
                callback = lambda dt: func()

            @listen('frame-enter')
            def update():
                dt = conf.get_frame_duration()
                callback(dt)
