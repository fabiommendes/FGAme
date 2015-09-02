# -*- coding: utf8 -*-
'''
Define o objeto principal que guarda e altera as configurações da FGAme.
'''

from FGAme.core import log as _log
from FGAme import backends as _backend_module


# --------------------------------------------------------------------------- #
#                         Propriedades da simulação
# --------------------------------------------------------------------------- #
_has_init = False
_app_name = None
_conf_path = None

# --------------------------------------------------------------------------- #
#                                  Input
# --------------------------------------------------------------------------- #
_input_class = None
_input_object = None


def init_input():
    '''Inicializa o sistema de inputs de teclado e mouse.'''

    global _input_object, _input_class

    if _input_class is None:
        set_backend()
        _input_class = _backend_classes['input']

    _input_object = _input_class()
    _input_object.init()
    return _input_object


def get_input():
    '''Retorna o objeto screen inicializado'''

    return _input_object or init_input()


# --------------------------------------------------------------------------- #
#                              Resolução e tela
# --------------------------------------------------------------------------- #
_screen_class = None
_screen_object = None
_window_origin = (0, 0)
_window_shape = None


def get_resolution():
    '''Retorna uma tupla com a (largura, altura) da tela em pixels'''

    return _window_shape or (800, 600)


def set_resolution(*args):
    '''Configura a tela com a resolução dada.

    conf.set_resolution(800, 600)     --> define o formato em pixels
    conf.set_resolution('fullscreen') --> modo tela cheia'''

    global _window_shape

    if len(args) == 2:
        width, height = args
    elif args == ('fullscreen',):
        raise NotImplementedError
    elif len(args) == 1:
        width, height = args[0]
    else:
        raise TypeError('invalid arguments: %s' % args)

    if _window_shape is None or _window_shape == (width, height):
        _window_shape = (width, height)
    else:
        raise RuntimeError(
            'cannot change resolution after screen initialization')


def get_screen():
    '''Retorna o objeto screen inicializado'''

    return _screen_object or init_screen()


def init_screen(*args, **kwds):
    '''Inicializa a tela na resolução padrão de 800x600 ou na resolução
    especificada pelo usuário usando a função `set_resolution()`'''

    global _screen_class, _screen_object

    if _screen_object is not None:
        raise RuntimeError('trying to re-init screen object')

    if _screen_class is None:
        set_backend()
        _screen_class = _backend_classes['screen']

    if not args:
        shape = get_resolution()
        screen = _screen_class(shape=shape, **kwds)
    elif len(args) == 2:
        screen = _screen_class(shape=args, **kwds)
    elif args == ('fullscreen',):
        screen = _screen_class(shape=args, **kwds)

    # Save environment variables
    if _window_shape is None:
        set_resolution(screen.shape)
    _screen_object = screen
    screen.init()
    return screen


def show_screen():
    '''Mostra a tela principal.

    Inicia com os parâmetros definidos, caso a tela ainda não tenha sido
    criada'''

    (_screen_object or init_screen()).show()


# --------------------------------------------------------------------------- #
#                    Propriedades da simulação/Mainloop
# --------------------------------------------------------------------------- #
_physics_fps = 60
_physics_dt = 1 / 60.
_mainloop_class = None
_mainloop_object = None


def init_mainloop():
    '''Inicializa o loop principal.'''

    global _mainloop_class, _mainloop_object

    if _mainloop_class is None:
        set_backend()
        _mainloop_class = _backend_classes['mainloop']

    screen = get_screen()
    input_ = get_input()
    fps = get_framerate()
    _mainloop_object = _mainloop_class(screen, input_, fps)
    return _mainloop_object


def get_mainloop():
    '''Retorna o objeto screen inicializado'''

    return _mainloop_object or init_mainloop()


def get_framerate():
    '''Retorna a taxa de atualização global em frames por segundo'''

    return _physics_fps


def get_frame_duration():
    '''Retorna a duração de cada frame (inverso do framerate) em segundos'''

    return _physics_dt


def set_framerate(value):
    '''Configura o número de frames por segundo'''

    global _physics_dt, _physics_fps
    value = float(value)
    _physics_fps = value
    _physics_dt = 1.0 / value


def set_frame_duration(value):
    '''Configura a duração de um frame de simulação'''

    set_framerate(1.0 / value)


# --------------------------------------------------------------------------- #
#                         Propriedades do backend
# --------------------------------------------------------------------------- #
_backend = None
_backends = ['pygame', 'sdl2cffi', 'sdl2', 'pygamegfx', 'pygamegl']
_backend_classes = None


def set_backend(backend=None):
    '''Define o backend a ser utilizado pela FGAme.

    Se for chamada sem nenhum argumento, tenta carregar os backends na
    ordem dada por _backends. Se o argumento for uma lista, tenta
    carregar os backends na ordem especificada pela lista.'''

    global _backend, _backend_classes

    # Função chamada sem argumentos
    if backend is None:
        if _backend is None:
            backend = _backends
        else:
            return  # backend já configurado!

    # Previne modificar o backend
    if _backend is not None:
        if _backend != backend:
            raise RuntimeError(
                'already initialized to %s, cannot change the backend' %
                _backend)
        else:
            return

    # Carrega backend pelo nome
    if isinstance(backend, str):
        if not _backend_module.supports_backend(backend):
            raise ValueError(
                '%s backend is not supported in your system' %
                backend)

        _backend = backend
        _backend_classes = _backend_module.get_backend_classes(backend)
        _log.info('conf: Backend set to %s' % backend)

    # Carrega backend a partir de uma lista
    else:
        for be in backend:
            if _backend_module.supports_backend(be):
                set_backend(be)
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


###############################################################################
def init():
    '''Inicializa todas as classes relevantes do FGAme.

    Força a inicialização na primeira chamada. As chamadas subsequentes não
    produzem efeito.'''

    global _has_init

    # Previne a inicialização repetida
    if _has_init:
        return

    # Garante que exite um backend definido
    set_backend()

    # Inicializa o vídeo, input, mainloop, etc
    if _screen_object is None:
        init_screen()

    if _input_object is None:
        init_input()

    if _mainloop_object is None:
        init_mainloop()

    _has_init = True
