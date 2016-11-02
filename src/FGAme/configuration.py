import os

from FGAme import backends as fgame_backends
from FGAme.logger import log


def _setter_factory(attr, force=False):
    def func(self, value):
        obj = getattr(self, attr)
        if value is not None:
            if obj is None or obj is value or force:
                setattr(self, attr, obj)
            else:
                name = attr.strip('_')
                if name.endswith('_object'):
                    name = name[:-7]
                name = name.replace('_', ' ')
                raise RuntimeError('resetting %s object' % name)

    return func


class Configuration:
    """
    The global :object:`FGAme.conf` object provides tools to access and modify
    initialization parameters of the game engine. Most of these functions can
    only be executed before initializing any other FGAme object and before
    starting the mainloop.


    Initialization can be explicit, using :func:`FGAme.init`, or implicit, which
    is done when the mainloop is started. Configuration generally can only be
    modified in the very beginning of a program, such as in the example::

        from FGAme import *

        # Configurations
        conf.set_resolution(1024, 764)
        conf.set_backend('sdl2')
        ...
        init()

        # Make game objects and run
        world = World()
        ...
    """

    DEBUG = False
    _has_init = False
    _app_name = None
    _conf_path = None
    _input_class = None
    _input_object = None
    _physics_fps = 60
    _physics_dt = 1 / 60.
    _mainloop_class = None
    _mainloop_object = None
    _screen_class = None
    _screen_object = None
    _window_origin = (0, 0)
    _window_shape = None
    _backend = None
    _backends = ['pygame', 'pygamegfx', 'sdl2', 'sdl2cffi']
    _backend_classes = None
    _set_screen = _setter_factory('_screen_object')
    _set_input = _setter_factory('_input_object')
    _set_mainloop = _setter_factory('_mainloop_object')
    _set_fps = _setter_factory('_physics_fps', force=True)

    @property
    def sfx_class(self):
        from FGAme.sound import SFX
        return SFX

    @property
    def music_class(self):
        from FGAme.sound import Music
        return Music

    def set_resolution(self, *args):
        """
        Set screen resolution.

        The default resolution is 800x600.

        Examples:
            conf.set_resolution(800, 600):
                format in pixels
            conf.set_resolution('fullscreen'):
                for fullscreen mode.
        """

        if len(args) == 2:
            width, height = args
        elif args == ('fullscreen',):
            raise NotImplementedError
        elif len(args) == 1:
            width, height = args[0]
        else:
            raise TypeError('invalid arguments: %s' % args)

        if self._window_shape is None or self._window_shape == (width, height):
            self._window_shape = (width, height)
        else:
            raise RuntimeError(
                'cannot change resolution after screen initialization')

    def set_framerate(self, value):
        """
        Set the simulation frame rate.
        """

        value = float(value)
        self._physics_fps = value
        self._physics_dt = 1.0 / value

    def set_frame_duration(self, value):
        """
        Configure frame rate by choosing the duration of each frame.
        """

        self.set_framerate(1.0 / value)

    def set_backend(self, backend=None):
        """
        Define backend used by FGAme.

        If called with no arguments, try to load backends in the default order.
        If argument is a list, try to load backends in the specified order.
        This method return a string with the loaded backend.
        """

        if backend is None:
            if self._backend is None:
                if 'FGAME_BACKEND' in os.environ:
                    env_be = os.environ['FGAME_BACKEND']
                    backend = env_be.split(',')
                    log.info('using backend defined by environ: %s' % env_be)
                else:
                    backend = self._backends
            else:
                return  # backend is configured!

        # Prevent changes to a configured backend
        if self._backend is not None:
            if self._backend != backend:
                raise RuntimeError(
                    'already initialized to %s, cannot change the backend' %
                    self._backend
                )
            else:
                return

        # Load backend by name
        if isinstance(backend, str):
            if not fgame_backends.supports_backend(backend):
                raise ValueError(
                    '%s backend is not supported in your system' %
                    backend)

            self._backend = backend
            self._backend_classes = fgame_backends.get_backend_classes(backend)
            log.info('conf: Backend set to %s' % backend)

        # Load backend from list
        else:
            for be in backend:
                if fgame_backends.supports_backend(be):
                    self.set_backend(be)
                    break
            else:
                msg = 'none of the requested backends are available.'
                if 'pygame' in backend:
                    msg += (
                        '\nSupported backends are:'
                        '\n    * pygame'
                        '\n    * sdl2'
                        # '\n    * kivy'
                    )
                raise RuntimeError(msg)
        return self._backend

    def get_backend(self, force=False):
        """
        Return a string with the initialized backend.

        Return None if no backed was initialized. The argument ``force=True``
        forces the backend to initialize if it had not been so.
        """

        if force and self._backend is None:
            return self.set_backend()
        return self._backend

    # Initialization
    def init(self):
        """
        Initialize all FGAme sub-systems.

        This method should be called only once. Further calls are no-op.
        """

        if self._has_init:
            return

        self.set_backend()

        if self._screen_object is None:
            self.init_screen()

        if self._input_object is None:
            self.init_input()

        if self._mainloop_object is None:
            self.init_mainloop()

        self._has_init = True

    def init_mainloop(self, screen=None, input=None, fps=None):
        """
        Initialize the main loop object.

        This function do not execute the main loop. It only prepares an instance
        that can be later executed by calling either its .run() and .start()
        methods.
        """

        if self._mainloop_class is None:
            self.set_backend()
            self._mainloop_class = self._backend_classes['mainloop']

        self._set_screen(screen)
        self._set_input(screen)
        self._set_fps(fps)
        screen = screen or self.get_screen()
        input_ = input or self.get_input()
        fps = fps or self.get_framerate()
        self._mainloop_object = self._mainloop_class(screen, input_, fps)
        return self._mainloop_object

    def init_input(self):
        """
        Initializes the keyboard and mouse input systems.
        """

        if self._input_class is None:
            self.set_backend()
            self._input_class = self._backend_classes['input']

        self._input_object = self._input_class()
        return self._input_object

    def init_screen(self, *args, **kwds):
        """
        Initializes the screen system.
        """

        if self._screen_object is not None:
            raise RuntimeError('trying to re-init screen object')

        if self._screen_class is None:
            self.set_backend()
            self._screen_class = self._backend_classes['screen']

        if not args:
            shape = self.get_resolution()
            screen = self._screen_class(shape=shape, **kwds)
        elif len(args) == 2:
            screen = self._screen_class(shape=args, **kwds)
        elif args == ('fullscreen',):
            screen = self._screen_class(shape=args, **kwds)
        else:
            raise RuntimeError

        # Save environment variables
        if self._window_shape is None:
            self.set_resolution(screen.shape)
        self._screen_object = screen
        screen.init()
        return screen

    def get_mainloop(self):
        """
        Return an initialized main loop object.
        """

        return self._mainloop_object or self.init_mainloop()

    def get_input(self):
        """
        Return an initialized screen object.
        """

        return self._input_object or self.init_input()

    def get_screen(self):
        """
        Return an initialized screen object.
        """

        return self._screen_object or self.init_screen()

    def get_resolution(self):
        """
        Return a tuple of screen (width, height) in pixels.
        """

        return self._window_shape or (800, 600)

    def get_framerate(self):
        """
        Return the desired update rate in frames per second.
        """

        return self._physics_fps

    def get_frame_duration(self):
        """
        Return the duration of each frame in seconds.
        """

        return self._physics_dt

    def show_screen(self):
        """
        Display the main screen.
        """

        screen = self._screen_object or self.init_screen()
        if not screen.visible:
            screen.show()


# Global configuration object
conf = Configuration()
init = conf.init
