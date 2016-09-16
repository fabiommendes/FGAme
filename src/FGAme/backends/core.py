import os
import importlib

__all__ = ['get_screen_class', 'get_input_class', 'get_mainloop_class',
           'get_backend_classes', 'supports_backend']
GLOBAL_INFO = None


def get_info():
    """
    Return a dictionary mapping each backend to a dictionary with the names
    of 'input', 'screen' and 'mainloop' classes.
    """

    global GLOBAL_INFO

    if GLOBAL_INFO is not None:
        return GLOBAL_INFO

    else:
        GLOBAL_INFO = out = {}
        path, _ = os.path.split(__file__)
        for path in os.listdir(path):
            if path.endswith('_conf.py'):
                name, _, _ = path.rpartition('_')
                conf = importlib.import_module('FGAme.backends.%s_conf' % name)
                out[name] = dict(
                    input=conf.input,
                    screen=conf.screen,
                    mainloop=conf.mainloop,
                    imports=conf.imports,
                )
        return out


def get_backend_classes(backend):
    """
    Dictionary mapping 'input', 'screen' and 'mainloop'  to their respective
    classes for a given backend.
    """

    get_info()[backend]
    classes = ('input', 'mainloop', 'screen')
    return {k: _get_class_worker(k, backend) for k in classes}


def _get_class_worker(cls, backend):
    D = get_info()[backend]
    module = importlib.import_module('FGAme.backends.%s_be' % backend)
    return getattr(module, D[cls])


def get_screen_class(backend):
    """
    Return the screen class for the selected backend.
    """

    return _get_class_worker('screen', backend)


def get_input_class(backend):
    """
    Return the input class for the selected backend.
    """

    return _get_class_worker('input', backend)


def get_mainloop_class(backend):
    """
    Return the mainloop class for the selected backend.
    """

    return _get_class_worker('mainloop', backend)


def supports_backend(backend):
    """
    Return True if backend is supported.
    """

    imports = get_info()[backend]['imports']
    try:
        for module in imports:
            importlib.import_module(module)
        else:
            return True
    except ImportError:
        return False
