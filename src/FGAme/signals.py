import inspect
import sys
from functools import partial
from types import FunctionType, MethodType
from weakref import WeakKeyDictionary

from lazyutils import lazy

REGISTERED_SIGNALS = {}
METHOD_LISTENERS = WeakKeyDictionary()
FUNCTION_LISTENERS = WeakKeyDictionary()


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

    def __init__(self, function, signal, filters, args=None, kwargs=None,
                 active=True, connected=False):
        self.function = function
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
            function = partial(function, *self.args, **self.kwargs)

        # Simple cases: no filters
        if not filters:
            self.callback = function
        else:
            self.callback = _ignoring_function_factory(function, signal.filters,
                                                       set(self.filters))

    def __call__(self, *args, **kwargs):
        return self.callback(*args, **kwargs)

    def __repr__(self):
        data = ', '.join('%s=%r' for x in self.filters.items())
        return '%s(%s)' % (self.function.__name__, data)

    def accept(self, *args, **kwargs):
        """
        Return true if the handler should accept to handle the given call.
        """

        accept = self._accept
        if accept is None:
            for arg, name in zip(args, self.signal.filters):
                kwargs[name] = arg
            for name, value in self.filters.items():
                if kwargs.get(name, value) != value:
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

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)

    def connect(self, function, *filters, args=None, kwargs=None, **extra_args):
        """
        Connects handler to the signal.

        Args:
            function:
                A function handler with the correct signature
            args (tuple):
                Any positional arguments that must be applied to the handler
                function.
            kwargs (dict):
                Any keyword arguments that must be applied to the handler
                function.

        The remaining positional and keyword arguments must match the filters
        registered to the signal. If any filter is defined, the handler will be
        executed only when the signal is triggered with the corresponding
        arguments have the same values as the chosen filters.

        This function return a Handler instance that can be use to control
        how the function handler is connected to the signal.
        """

        named_filters = {}
        for k, v in list(extra_args.items()):
            if k in self.filters:
                named_filters[k] = extra_args.pop(k)
        filters = normalize_filters(self, filters, named_filters)
        kwargs = dict(kwargs or {}, **extra_args)
        filters_map = {self.filters[i]: value for i, value in
                       enumerate(filters)}

        # Now we create a handler and attach to the list of handlers
        handler = Handler(
            function,
            signal=self,
            filters=filters_map,
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
                try:
                    handler.callback(*args, **kwargs)
                except Exception:
                    print(
                        'Error processing %r signal:' % self.name,
                        '    %s callback raised an exception' % handler,
                        '-' * 70,
                        sep='\n', file=sys.stderr
                    )
                    raise

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


class Listener:
    """
    Base class for objects that implement the listener interface.
    """

    __slots__ = ()

    @lazy
    def _connected_handlers(self):
        return []

    @lazy
    def _instance_signals(self):
        return {}

    def _as_signal(self, signal):
        if isinstance(signal, Signal):
            return signal
        try:
            return self._instance_signals[signal]
        except KeyError:
            return as_signal(signal)

    def autoconnect(self):
        """
        Auto-connect all signals to handlers.
        """

        cls = type(self)
        for attr in dir(cls):
            if attr.startswith('_'):
                continue
            cls_value = getattr(cls, attr)
            if isinstance(cls_value, FunctionType):
                value = getattr(self, attr)
            else:
                continue

            if attr.endswith('_event'):
                signal_name = attr[:-6].replace('_', '-')
                self.listen(signal_name, function=value)

            if cls_value in METHOD_LISTENERS:
                L = METHOD_LISTENERS[cls_value]
                for (signal, filters, args, kwargs, extra_args) in L:
                    self.listen(signal, *filters, args=args, kwargs=kwargs,
                                function=value, **extra_args)

    def new_signal(self, name, filters=(), extra_args=(), help_text=''):
        """
        Create a new signal bound to an specific instance.
        """

        signal = Signal(name, filters, extra_args, help_text)
        self._instance_signals[name] = signal
        return signal

    def signal_filters(self):
        """
        Return a dictionary mapping filter names with their corresponding
        values.
        """

        return {}

    def listen(self, signal, *filters, args=None, kwargs=None, function=None,
               **extra_args):
        """
        Connect function with the given signal.

        It is similar to the global listen() decorator, associate the filters
        with the current instance.
        """

        signal = self._as_signal(signal)
        named_filters = self.signal_filters()
        for k, v in list(extra_args.items()):
            if k in signal.filters:
                if k in named_filters:
                    raise TypeError('duplicated argument: %r' % k)
                named_filters[k] = extra_args.pop(k)
        filters = normalize_filters(signal, filters, named_filters)

        if function is not None:
            handler = listen(signal, *filters, args=args, kwargs=kwargs,
                             function=function, **extra_args)
            self._connected_handlers.append(function)
        else:
            def decorator(func):
                decorator = listen(signal, *filters, args=args, kwargs=kwargs,
                                   **extra_args)
                decorated = decorator(func)
                self._connected_handlers.append(decorated._signal_handlers[-1])
                return decorated

            return decorator

    def disconnect_signals(self):
        """
        Disconnect all signal handlers associated with the current object.
        """

        for handler in self._connected_handlers:
            handler.disconnect()

    def pause_signals(self):
        """
        Temporarily disable all signal handlers associated with the current
        object.
        """

        for handler in self._connected_handlers:
            handler.pause()

    def resume_signals(self):
        """
        Re-enable all paused signal handlers associated with the current object.
        """

        for handler in self._connected_handlers:
            handler.resume()


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

    if isinstance(func, MethodType):
        return False
    try:
        args = inspect.getargspec(func).args
        return args and args[0] == 'self'
    except TypeError:
        return False


def listen(signal, *filters,
           function=None, args=None, kwargs=None, **extra_kwargs):
    """
    Decorator function
    """

    def get_handler(signal, function):
        if not callable(function):
            raise TypeError('must be callable, got %r' % function)
        return signal.connect(function, *filters, args=args, kwargs=kwargs,
                              **extra_kwargs)

    if function is not None:
        signal = as_signal(signal)
        return get_handler(signal, function)
    signal_input = signal

    def decorator(func):
        if is_method(func):
            item = signal_input, filters, args, kwargs, extra_kwargs
            args_list = METHOD_LISTENERS.get(func, [])
            args_list.append(item)
            METHOD_LISTENERS[func] = args_list
            return func

        # Connect function
        signal = as_signal(signal_input)
        handler = get_handler(signal, func)

        # We register a few attributes to make the func.disconnect(),
        # func.pause(), etc functions work.
        signal_data = FUNCTION_LISTENERS.get(func, {})
        signals = signal_data.get('signals', set())
        signals.add(signal)
        handlers = signal_data.get('handlers', [])
        handlers.append(handler)

        def make_action(signal, action, *args, **kwargs):
            # Helper function
            affected = []
            handlers = FUNCTION_LISTENERS.get(func, {}).get('handlers', [])
            for idx, handler in enumerate(list(handlers)):
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
                signals = FUNCTION_LISTENERS.get(func, {}).get('signals', set())
                for signal in signals:
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
            handlers = FUNCTION_LISTENERS.get(func, {}).get('handlers', [])
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
            handlers = FUNCTION_LISTENERS.get(func, {}).get('handlers', [])
            for handler in handlers:
                handlers = data.setdefault(handler.signal, [])
                handlers.append(handler)
            return data

        # Now we save these functions as attributes for the decorated function
        try:
            func.disconnect = disconnect
            func.reconnect_before = reconnect_before
            func.reconnect_after = reconnect_after
            func.pause = pause
            func.resume = resume
            func.handler = handler
            func.handlers = handlers
        except AttributeError:
            pass
        return func

    return decorator


def trigger(signal, *args, **kwargs):
    """
    Triggers signal with the given positional and keyword arguments.
    """

    signal = as_signal(signal)
    signal.trigger(*args, **kwargs)


def as_signal(signal):
    """
    Return signal name as a signal instance.
    """

    if isinstance(signal, str):
        try:
            return REGISTERED_SIGNALS[signal]
        except KeyError:
            raise ValueError('invalid signal name: %s' % signal)
    elif isinstance(signal, Signal):
        return signal
    else:
        raise TypeError('not a signal')


def normalize_filters(signal, values, named_filters):
    """
    Return a list of filter values from filters passed by position and filters
    passed by name.
    """

    # Create an empty list of filter values
    empty = object()
    result = [empty] * len(signal.filters)

    # Save named values
    for name, value in named_filters.items():
        if name in signal.filters:
            idx = signal.filters.index(name)
            result[idx] = value

    # Save positional values
    values = list(reversed(values))
    idx = 0
    while values:
        value = result[idx]
        if value is empty:
            result[idx] = values.pop()
        elif idx == len(values) - 1:
            raise ValueError('too many filter arguments in %r signal!' %
                             signal.name)
        else:
            idx += 1

    # Remove trailing empty values
    while result and result[-1] is empty:
        result.pop()
    if empty in result:
        idx = result.index(empty)
        name = signal.filters[idx]
        raise TypeError('missing %s argument!' % name)
    return result


class OnObject:
    """
    Implements the on(signal, args).do(function, *args, **kwargs) syntax.
    """

    def __init__(self, signal, *filters):
        self.__signal = signal
        self.__filters = filters

    def __getattr__(self, attr):
        if self.__bound is None:
            raise AttributeError(attr)
        else:
            return getattr(self.__bound, attr)

    def do(self, function, *args, **kwargs):
        listener = listen(self.__signal, *self.__filters,
                          function=function, args=args, kwargs=kwargs)
        listener.do = self.do
        return listener


def on(signal, *filters):
    """
    Implements the on().do() syntax to register signal handlers.

    Example:
        This will print (an annoying) "hello frame!" message every frame.

        >>> on('frame-enter').do(print, "hello frame!")
    """

    return OnObject(signal, *filters)
