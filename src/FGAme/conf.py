# -*- coding: utf8 -*-
'''
A FGAme permite modificar os parâmetros de inicialização utilizando as funções
do módulo :mod:`FGAme.conf`. Nesta estão funções que controlam a inicialização
do motor de jogos e permitem recuperar o valor de alguns parâmetros globais.

Note que quase todas as funções que modificam o estado global contidas neste
módulo só podem ser executadas antes de iniciar o loop principal do jogo e de
definir eventos e callbacks para objetos. Modificar uma propriedade após a
inicialização quase sempre resultará em um erro.

A inicialização pode ser feita explicitamente invocando a função
:func:`FGAme.init()` ou implicitamente, quando executamos o loop principal. De
um modo geral, o programa deve ser organizado assim::

    from FGAme import *

    # Configurações
    conf.set_resolution(1024, 764)
    conf.set_backend('sdl2')
    ...
    init()

    # Cria objetos
    world = World()
    ...

    # Inicia mundo
    world.run()
'''

from FGAme.core import log as _log
from FGAme import backends as _backend_module

# --------------------------------------------------------------------------- #
#                       Variáveis globais para o módulo
# --------------------------------------------------------------------------- #
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
_backends = ['sdl2', 'pygamegfx', 'pygame', 'sdl2cffi']
_backend_classes = None


#
# Configuram parâmetros da simulação
#
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


def set_framerate(value):
    '''Configura o número de frames por segundo'''

    global _physics_dt, _physics_fps
    value = float(value)
    _physics_fps = value
    _physics_dt = 1.0 / value


def set_frame_duration(value):
    '''Configura a duração de um frame de simulação'''

    set_framerate(1.0 / value)


def set_backend(backend=None):
    '''Define o backend a ser utilizado pela FGAme.

    Se for chamada sem nenhum argumento, tenta carregar os backends na
    ordem padrão. Se o argumento for uma lista, tenta carregar os backends na
    ordem especificada pela lista. Retorna uma string descrevendo o backend
    carregado.'''

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
    return _backend


def get_backend(force=False):
    '''Retorna uma string com o backend incializado.

    Caso nenhum backend tenha sido inicializado, retorna None. Se o argumento
    `force` for verdadeiro, força a inicialização de algum backend.'''

    if force and _backend is None:
        return set_backend()
    return _backend

#
# Funções de inicialização
#


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


def init_mainloop(screen=None, input=None, fps=None):  # @ReservedAssignment
    '''Inicializa o objeto de loop principal.

    Note que esta função não executa o loop principal, mas apenas instancia o
    objeto que irá coordenar o loop principal quando uma função como
    :meth:`World.run` for chamada.
    '''

    global _mainloop_class, _mainloop_object

    if _mainloop_class is None:
        set_backend()
        _mainloop_class = _backend_classes['mainloop']

    _set_screen(screen)
    _set_input(screen)
    _set_fps(fps)
    screen = screen or get_screen()
    input_ = input or get_input()
    fps = fps or get_framerate()
    _mainloop_object = _mainloop_class(screen, input_, fps)
    return _mainloop_object


def init_input():
    '''Inicializa o sistema de inputs de teclado e mouse.'''

    global _input_object, _input_class

    if _input_class is None:
        set_backend()
        _input_class = _backend_classes['input']

    _input_object = _input_class()
    return _input_object


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


#
# Retornam objetos e estados de simulação
#
def get_mainloop():
    '''Retorna o objeto screen inicializado'''

    return _mainloop_object or init_mainloop()


def get_input():
    '''Retorna o objeto screen inicializado'''

    return _input_object or init_input()


def get_screen():
    '''Retorna o objeto screen inicializado'''

    return _screen_object or init_screen()


def get_resolution():
    '''Retorna uma tupla com a (largura, altura) da tela em pixels'''

    return _window_shape or (800, 600)


def get_framerate():
    '''Retorna a taxa de atualização global em frames por segundo'''

    return _physics_fps


def get_frame_duration():
    '''Retorna a duração de cada frame (inverso do framerate) em segundos'''

    return _physics_dt


#
# Outras funções
#
def show_screen():
    '''Mostra a tela principal.

    Inicia com os parâmetros definidos, caso a tela ainda não tenha sido
    criada'''

    (_screen_object or init_screen()).show()


#
# Funções privadas
#
def _set_var_worker(var, force=False):
    def func(value):
        G = globals()
        obj = G[var]
        if value is not None:
            if obj is None or obj is value or force:
                obj = value
            else:
                name = var.strip('_')
                if name.endswith('_object'):
                    name = name[:-7]
                name = name.replace('_', ' ')
                raise RuntimeError('reseting %s object' % name)
    return func

_set_screen = _set_var_worker('_screen_object')
_set_input = _set_var_worker('_input_object')
_set_mainloop = _set_var_worker('_mainloop_object')
_set_fps = _set_var_worker('_physics_fps', force=True)
