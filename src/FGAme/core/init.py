# -*- coding: utf8 -*-
from FGAme.core import log
from FGAme.core import env
from FGAme import backends


class Control(object):

    '''Classe com funções de inicialização da FGAme'''

    def __init__(self):
        self.__dict__['_env'] = env

    # Mecanismo getter/setter para o ambiente: permite trancar a classe após
    # a inicialização para previnir modificações no ambiente
    def __getattr__(self, attr):
        if attr.startswith('_'):
            return getattr(self._env, attr[1:])
        else:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        if attr.startswith('_') and hasattr(self._env, attr[1:]):
            name = attr[1:]
            default = getattr(type(self._env), name)

            if getattr(self._env, name) == default:
                setattr(self._env, name, value)
            elif getattr(self._env, name) == value:
                pass
            elif self._env.has_init:
                msg = ('cannot change environment after initialization: '
                       '%s = %s --> %s' %
                       (name, getattr(self._env, name), value))
                raise RuntimeError(msg)
            else:
                raise RuntimeError('trying to reassign %s' % name)

        else:
            raise AttributeError(attr)

    ###########################################################################
    #         Set state functions -- can be executed only before init
    ###########################################################################

    def set_resolution(self, *args):
        '''Configura a tela com a resolução dada.

        conf.set_resolution(800, 600)     --> define o formato em pixels
        conf.set_resolution('fullcanvas') --> modo tela cheia
        '''

        if len(args) == 2:
            x, y = args
            self._window_shape = (int(x), int(y))

        elif args == ('fullcanvas',):
            self._window_shape = 'fullcanvas'

        else:
            raise TypeError('invalid arguments: %s' % args)

    def set_backend(self, backend=None):
        '''Define o backend a ser utilizado pela FGAme.

        Se for chamada sem nenhum argumento, tenta carregar os backends na
        ordem dada por self.backends. Se o argumento for uma lista, tenta
        carregar os backends na ordem especificada pela lista.'''

        # Função chamada sem argumentos
        if backend is None:
            if self._backend is None:
                backend = self._backends
            else:
                return  # backend já configurado!

        # Previne modificar o backend
        if self._backend is not None:
            if self._backend != backend:
                raise RuntimeError(
                    'already initialized to %s, cannot change the backend' %
                    self._backend)
            else:
                return

        # Carrega backend pelo nome
        if isinstance(backend, str):
            if not backends.supports_backend(backend):
                raise ValueError(
                    '%s backend is not supported in your system' %
                    backend)

            self._backend = backend
            self._backend_classes = backends.get_backend_classes(backend)
            log.info('conf: Backend set to %s' % backend)

        # Carrega backend a partir de uma lista
        else:
            for be in backend:
                if backends.supports_backend(be):
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

    ###########################################################################
    #             Query functions -- can be executed any time
    ###########################################################################

    def get_window_shape(self):
        '''Retorna uma tupla com a resolução da janela em pixels'''

        if self._window_shape is None:
            self._window_shape = (800, 600)
        return self._window_shape

    def get_canvas(self):
        '''Retorna o objeto canvas inicializado'''

        return self._canvas_object or self.init_canvas()

    def get_input(self):
        '''Retorna o objeto canvas inicializado'''

        return self._input_object or self.init_input()

    def get_mainloop(self):
        '''Retorna o objeto canvas inicializado'''

        return self._mainloop_object or self.init_mainloop()

    ###########################################################################
    # Init functions
    ###########################################################################

    def init(self):
        '''Inicializa todas as classes relevantes do FGAme'''

        # Previne a inicialização repetida
        if self._has_init:
            return

        # Garante que exite um backend definido
        self.set_backend()

        # Inicializa o vídeo, input, mainloop, etc
        if self._canvas_object is None:
            self._canvas_object = self.init_canvas()

        if self._input_object is None:
            self._input_object = self.init_input()

        if self._mainloop_object is None:
            self._mainloop_object = self.init_mainloop()

        self._has_init = True

    def init_canvas(self, *args, **kwds):
        '''Inicia a tela'''

        if self._canvas_class is None:
            self.set_backend()
            self._canvas_class = self._backend_classes['screen']

        if not args:
            canvas = self._canvas_class(
                shape=self._window_shape or (
                    800,
                    600),
                **kwds)
        elif len(args) == 2:
            canvas = self._canvas_class(shape=args, **kwds)
        elif args == ('fullscreen',):
            canvas = self._canvas_class(shape=args, **kwds)

        # Save environment variables
        self._window_shape = canvas.shape
        self._canvas_object = canvas
        canvas.init()
        return canvas

    def init_input(self):
        if self._input_class is None:
            self.set_backend()
            self._input_class = self._backend_classes['input']

        self._input_object = self._input_class()
        self._input_object.init()
        return self._input_object

    def init_mainloop(self):
        if self._mainloop_class is None:
            self.set_backend()
            self._mainloop_class = self._backend_classes['mainloop']

        self._mainloop_object = self._mainloop_class()
        self._mainloop_object.init()
        return self._mainloop_object
