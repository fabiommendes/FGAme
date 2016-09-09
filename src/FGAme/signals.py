import inspect
from functools import partial
REGISTERED_SIGNALS = {}


def _ignoring_function_factory(function, required_args, ignores):
    """
    Return a version of the function which accepts the arguments defined in
    required_args list either as positional or keywords arguments plus arbitrary 
    args and kwargs. Parameters in the ignores list are not passed to the 
    decorated function.
    """
    # A slightly more efficient version for the common case when there is a
    # single filter defined for the object
    if len(required_args) == 1:
        arg_name = required_args[0]

        def filtered(*args, **kwargs):
            if arg_name in kwargs:
                del kwargs[arg_name]
            else:
                args = args[1:]
            return function(*args, **kwargs)

    # The generic version of the function for any number of filters and ignore
    # arguments
    else:
        def filtered(*args, **kwargs):
            for arg, name in zip(args, required_args):
                kwargs[name] = arg
            for filter in ignores:
                del kwargs[filter]
            return function(**kwargs)
    return filtered


class Handler:
    """
    A signal handler.
    """

    def __init__(self, handler, signal, filters, args=None, kwargs=None,
                 active=True, connected=False):
        self.handler = handler
        self.signal = signal
        self.connected = connected
        self.active = active
        self.args = tuple(args or ())
        self.kwargs = dict(kwargs or ())
        self.filters = dict(filters)
        if not filters and active:
            self._accept = True
        elif not active:
            self._accept = False
        else:
            self._accept = None

        # We now decide what is the optimal way of normalizing the callback
        # function. This function is saved on the .callback attribute
        if self.args or self.kwargs:
            handler = partial(handler, *self.args, **self.kwargs)

        # Simple cases: no filters
        if not filters:
            self.callback = handler
        else:
            self.callback = _ignoring_function_factory(handler, signal.filters,
                                                       set(self.filters))

    def __call__(self, *args, **kwargs):
        return self.callback(*args, **kwargs)

    def accept(self, *args, **kwargs):
        """
        Return true if the handle should accept to handle the given call.
        """

        accept = self._accept
        if accept is None:
            for arg, name in zip(args, self.signal.filters):
                kwargs[name] = arg
            for name, value in self.filters.items():
                if kwargs[name] != value:
                    return False
            return True
        else:
            return accept

    def disconnect(self):
        """
        Disconnects handler from signal.
        """

        self.signal.disconnect(self)

    def pause(self):
        """
        Temporarily disable handler in the signal.

        The handler can be resumed later in the same position in the calling
        queue by using the resume method.
        """

        self.active = False
        self._accept = False

    def resume(self):
        """
        Resume handler that was paused with the .pause() method.
        """

        self.active = True
        self._accept = True if not self.filters else None

    def reconnect_before(self):
        """
        Reconnect the handler in the beginning of the calling queue.

        There is no guarantee that the handler will be the first in the list
        since any handler can call this method, if they want.
        """

        self.signal.reconnect_before(self)

    def reconnect_after(self):
        """
        Reconnect the handler in the end of the calling queue.

        There is no guarantee that the handler will be the last in the list
        since any handler can call this method, if they want.
        """

        self.signal.reconnect_after(self)


class Signal:
    """
    Represents a signal.
    """

    def __init__(self, name, filters=(), extra_args=(), help_text=''):
        self.name = name
        self.filters = tuple(filters)
        self.extra_args = tuple(extra_args)
        self.handlers = []
        self.help_text = help_text

    def __hash__(self):
        # We want to put signals in a dictionary.
        return id(self)

    def __eq__(self, other):
        # Equality is identity.
        return self is other

    def connect(self, handler, *filters, args=None, kwargs=None,
                **filter_kwargs):
        """
        Connects handler to the signal.

        Args:
            handler:
                A function handler with the correct signature
            args:
                Any positional arguments that must be applied to the handler
                function.
            kwargs:
                Any keyword arguments that must be applied to the handler
                function.

        The remaining positional and keyword arguments must match the filters
        registered to the signal. If any filter is defined, the handler will be
        executed only when the signal is triggered with the corresponding
        arguments have the same values as the chosen filters.

        This function return a Handler instance that can be use to control
        how the function handler is connected to the signal.
        """

        # Merge positional and keyword arguments using information from
        # self.argnames
        num_args = len(self.filters)
        if len(filters) + len(filter_kwargs) > num_args:
            raise TypeError('signal binds to %s parameters at most' % num_args)

        for name, value in zip(self.filters, filters):
            if name in filter_kwargs:
                raise TypeError('duplicated argument: %r' % name)
            filter_kwargs[name] = value

        # Now we check if there is any invalid argument in kwargs
        for name in filter_kwargs:
            if name not in self.filters:
                raise TypeError('invalid argument: %r' % name)

        # Now we create a handler and attach to the list of handlers
        handler = Handler(
            handler,
            signal=self,
            filters=filter_kwargs,
            args=args,
            kwargs=kwargs,
            connected=True
        )
        self.handlers.append(handler)
        return handler

    def _split_handlers(self, handler, silent=False):
        if isinstance(handler, Handler):
            try:
                idx = self.handlers.index(handler)
            except ValueError:
                if silent:
                    return [], self.handlers
                raise
            return [handler], self.handlers[:idx] + self.handlers[idx + 1:]

        else:
            filter_in = [x for x in self.handlers if x.handler == handler]
            filter_out = [x for x in self.handlers if x.handler != handler]
            return filter_in, filter_out

    def reconnect_before(self, handler, silent=False):
        """
        Reconnect the handler in the beginning of the calling queue.

        There is no guarantee that the handler will be the first in the list
        since any handler can call this method, if they want.

        If silent is True, no error is raised if handler is not connected to the
        signal.
        """

        filtered, rest = self._split_handlers(handler, silent=silent)
        self.handlers[:] = filtered + rest

    def reconnect_after(self, handler, silent=False):
        """
        Reconnect the handler in the end of the calling queue.

        There is no guarantee that the handler will be the last in the list
        since any handler can call this method, if they want.

        If silent is True, no error is raised if handler is not connected to the
        signal.
        """

        filtered, rest = self._split_handlers(handler, silent=silent)
        self.handlers[:] = rest + filtered

    def trigger(self, *args, **kwargs):
        """
        Trigger the signal with the given arguments.

        It is the responsibility of the callee to call this function with a
        consistent set of arguments. The valid arguments should be well
        documented and must cover at least the values declared filter names in
        the creation of the signal instance.
        """
        for handler in self.handlers:
            if handler.accept(*args, **kwargs):
                handler.callback(*args, **kwargs)

    def disconnect(self, handler, silent=False):
        """
        Disconnect a handler from signal.

        If silent is True, no error is raised if handler is not connected to the
        signal.
        """

        filtered, rest = self._split_handlers(handler, silent=silent)
        self.handlers[:] = rest
        if isinstance(handler, Handler) and filtered:
            filtered[0].connected = False


def global_signal(name, *args, **kwargs):
    """
    Create signal and register in the REGISTERED_SIGNALS dictionary.
    """

    signal = Signal(name, *args, **kwargs)
    REGISTERED_SIGNALS[name] = signal
    return signal


def is_method(func):
    """
    Return True if function is a method and receives an implicit self argument.
    """

    args = inspect.getargspec(func).args
    return args and args[0] == 'self'


def listen(signal, *args, **kwargs):
    """
    Decorator function
    """

    signal_input = signal

    def decorator(func):
        if is_method(func):
            try:
                args_list = func.__method_signals__
            except AttributeError:
                args_list = func.__method_signals__ = []
            args_list.append((signal_input, args, kwargs))
            return func

        if isinstance(signal_input, str):
            try:
                signal = REGISTERED_SIGNALS[signal_input]
            except KeyError:
                raise ValueError('invalid signal name: %s' % signal_input)
        else:
            signal = signal_input

        # Connect function
        fargs = kwargs.pop('args', None)
        handler = signal.connect(func, *args, args=fargs, kwargs=kwargs)

        # We register a few attributes to make the func.disconnect(),
        # func.pause(), etc functions work.
        signals = getattr(func, '_connected_signals', set())
        signals.add(signal)
        func._connected_signals = signals

        handlers = getattr(func, '_signal_handlers', [])
        handlers.append(handler)
        func._signal_handlers = handlers

        def make_action(signal, action, *args, **kwargs):
            # Helper function
            affected = []
            for idx, handler in enumerate(list(func._signal_handlers)):
                if handler.signal is signal:
                    affected.append(idx)
                    getattr(handler, action)(*args, **kwargs)
            return affected

        def make_multi_action(signal, action, *args, **kwargs):
            if signal is None:
                affected = []
                for signal in func._connected_signals:
                    L = make_action(signal, action, *args, **kwargs)
                    affected.extend(L)
                return affected
            else:
                return make_action(signal, action, *args, **kwargs)

        def disconnect(signal=None):
            """
            Disconnect function from all signals.

            Can target a specific signal, if provided.
            """
            if signal is None:
                for signal in list(func._connected_signals):
                    disconnect(signal)
                return

            # Disconnect a single signal
            remove = make_action(signal, 'disconnect')
            for idx in reversed(remove):
                del func._signal_handlers[idx]
            func._connected_signals.remove(signal)

        def reconnect_after(signal=None):
            """
            Reconnect function in the end of the handler queue.

            Can target a specific signal, if provided.
            """

            make_multi_action(signal, 'reconnect_after')

        def reconnect_before(signal=None):
            """
            Reconnect function in the beginning of the handler queue.

            Can target a specific signal, if provided.
            """

            make_multi_action(signal, 'reconnect_before')

        def pause(signal=None):
            """
            Temporarily disable function handler. Connection can be resumed
            with the resume function.

            Can target a specific signal, if provided.
            """

            make_multi_action(signal, 'pause')

        def resume(signal=None):
            """
            Resume a function handler paused with the .pause() function.

            Can target a specific signal, if provided.
            """

            make_multi_action(signal, 'resume')

        def handler(signal=None):
            """
            Return the Handler instance associated with this function.

            If more than one handler is present, raise an error. May filter by
            some specific signal, if needed.
            """

            # Filter handlers, if necessary
            handlers = func._signal_handlers
            if signal:
                handlers = [x for x in handlers if x.signal is signal]

            # Return chosen handler
            if len(handlers) == 1:
                return handlers[0]
            elif len(handlers) == 0:
                raise ValueError('no handler found')
            else:
                raise ValueError('multiple handlers found')

        def handlers():
            """
            Return a dictionary mapping signals to the corresponding list of
            handlers associated with this function.
            """

            data = {}
            for handler in func._signal_handlers:
                handlers = data.setdefault(handler.signal, [])
                handlers.append(handler)
            return data

        # Now we save these functions as attributes for the decorated function
        func.disconnect = disconnect
        func.reconnect_before = reconnect_before
        func.reconnect_after = reconnect_after
        func.pause = pause
        func.resume = resume
        func.handler = handler
        func.handlers = handlers
        return func

    return decorator


def trigger(signal, *args, **kwargs):
    """
    Triggers signal with the given positional and keyword arguments.
    """

    if isinstance(signal, str):
        try:
            signal = REGISTERED_SIGNALS[signal]
        except KeyError:
            raise ValueError('invalid signal name: %s' % signal)

    signal.trigger(*args, **kwargs)


# Physics events
collision_pair_signal = global_signal('collision-pair', [], ['collision'])
collision_signal = global_signal('collision', ['object'], ['collision'])
detach_signal = global_signal('detach-signal', ['object'])
out_of_bounds_signal = global_signal('out-of-margin', ['object'])
max_speed_signal = global_signal('max-speed', ['object'])
sleep_signal = global_signal('sleep', ['object'])
