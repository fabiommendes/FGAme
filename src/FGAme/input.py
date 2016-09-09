from FGAme.signals import global_signal as _signal

key_up_signal = _signal('key-up', ['key'])
key_down_signal = _signal('key-down', ['key'])
long_press_signal = _signal('long-press', ['key'])
mouse_motion_signal = _signal('mouse-motion', [], ['pos'])
mouse_button_up_signal = _signal('mouse-button-up', ['button'], ['pos'])
mouse_button_down_signal = _signal('mouse-button-down', ['button'], ['pos'])
mouse_long_press_signal = _signal('mouse-long-press', ['button'], ['pos'])


class Input:
    """
    Reads user input from keyboard, mouse, etc.
    """

    _instance = None

    def __init__(self):
        super(Input, self).__init__()
        self._longpress_keys = set()
        self._longpress_mouse_buttons = set()
        self._mouse_pos = (0, 0)

        if self._instance is None:
            Input._instance = self
        else:
            raise RuntimeError('Input() is a singleton')

    def process_key_down(self, key):
        """
        Execute all callbacks associated with the "key-down" event on the given
        key.
        """

        key_down_signal.trigger(key)
        self._longpress_keys.add(key)

    def process_key_up(self, key):
        """
        Execute all callbacks associated with the "key-up" event on the given
        key.
        """

        key_up_signal.trigger(key)
        self._longpress_keys.discard(key)

    def process_long_press(self):
        """
        Execute all callbacks associated with the "long-press" event on the given
        key.
        """

        trigger = long_press_signal.trigger
        for key in self._longpress_keys:
            trigger(key)

    def process_mouse_motion(self, pos):
        """
        Process callbacks associated with mouse motion.
        """

        mouse_motion_signal.trigger(pos)
        self._mouse_pos = pos

    def process_mouse_button_down(self, button, pos):
        """
        Process callbacks associated with mouse button click.
        """

        mouse_button_down_signal.trigger(button, pos)
        self._longpress_mouse_buttons.add(button)

    def process_mouse_button_up(self, button, pos):
        """
        Process callbacks associated with mouse button click (key up).
        """

        mouse_button_up_signal.trigger(button, pos)
        self._longpress_mouse_buttons.discard(button)

    def process_mouse_longpress(self):
        """
        Process callbacks associated with mouse button click (long press).
        """

        pos = self._mouse_pos
        trigger = mouse_long_press_signal.trigger
        for button in self._longpress_mouse_buttons:
            trigger(button, pos)

    def poll(self):
        """
        Polls for all user events.

        Must be implemented in a child class (backend-specific).
        """

        raise NotImplementedError

# TODO: implement on_event listeners
# def _on_key_down(self, key, func=None, *args, **kwds):
#     """
#     Register function to key (triggered when key is pressed).
#     """
#
#     return self.listen_key_down(key, func, *args, **kwds)
#
# def _on_key_up(self, key, func=None, *args, **kwds):
#     """
#     Register function to key (triggered when key is released).
#     """
#
#     return self.listen_key_up(key, func, *args, **kwds)
#
# def _on_long_press(self, key, func=None, *args, **kwds):
#     """
#     Register function to key (triggered on all frames in which key is
#     pressed).
#     """
#
#     return self.listen_long_press(key, func, *args, **kwds)
#
# def _on_mouse_motion(self, func=None, *args, **kwds):
#     """
#     Register function to mouse motion.
#
#     Calls function with mouse coordinates as first argument.
#     """
#
#     return self.listen_mouse_motion(func, *args, **kwds)
#
# def _on_mouse_button_down(self, button, func=None, *args, **kwds):
#     """
#     Similar to on_key_down(), but keeps track of mouse clicks.
#     """
#
#     return self.listen_mouse_button_down(func, *args, **kwds)
#
# def _on_mouse_button_up(self, button, func=None, *args, **kwds):
#     """
#     Similar to on_key_up(), but keeps track of mouse clicks.
#     """
#
#     return self.listen_mouse_button_up(func, *args, **kwds)
#
# def _on_mouse_long_press(self, button, func=None, *args, **kwds):
#     """
#     Similar to on_long_press(), but keeps track of mouse clicks.
#     """
#
#     return self.listen_mouse_button_long_press(func, *args, **kwds)
#
#
# # Global event register functions
# def _register(func_name):
#     input_method = getattr(Input, func_name)
#
#     def signal_handler_func(*args, **kwds):
#         try:
#             worker = getattr(Input._instance, func_name)
#         except AttributeError:
#             raise RuntimeError(
#                 'Input system has not started. '
#                 'Have you tried to execute conf.init() first?')
#         return worker(*args, **kwds)
#
#     signal_handler_func.__name__ = input_method.__name__
#     signal_handler_func.__doc__ = input_method.__doc__
#     return signal_handler_func
#
#
# on_key_down = _register('_on_key_down')
# on_key_up = _register('_on_key_up')
# on_long_press = _register('_on_long_press')
# on_mouse_motion = _register('_on_mouse_motion')
# on_mouse_button_down = _register('_on_mouse_button_down')
# on_mouse_button_up = _register('_on_mouse_button_up')
# on_mouse_long_press = _register('_on_mouse_long_press')
