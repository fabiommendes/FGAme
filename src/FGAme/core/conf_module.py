# -*- coding: utf8 -*-
'''
Define o objeto principal que guarda e altera as configurações da FGAme.
'''

from FGAme.core import log
from FGAme import backends


class Conf(object):

    '''Classe com funções de configuração e inicialização da FGAme.

    Ela '''

    # Propriedades relativas ao backend
    backend = None
    backends = ['pygame', 'sdl2cffi', 'sdl2', 'pygamegfx', 'pygamegl']
    backend_classes = None

    # Leitura de entradas do usuário
    input_class = None
    input_object = None

    # Propriedades da tela
    canvas_class = None
    canvas_object = None
    window_origin = (0, 0)
    window_shape = None

    @property
    def window_width(self):
        return self.window_shape[0]

    @property
    def window_height(self):
        return self.window_shape[1]

    @window_width.setter
    def window_width(self, value):
        self.canvas_shape = (value, self.window_shape[1])

    @window_height.setter
    def window_height(self, value):
        self.canvas_shape = (self.window_height[0], value)

    # Propriedades do loop principal
    mainloop_class = None
    mainloop_object = None

    # Controle de inicialização e configuração
    has_init = False
    app_name = None
    conf_path = None

    # Propriedades da simulação
    physics_fps = 60
    physics_dt = 1 / 60.
    screen_fps = 60
    screen_dt = 1 / 60.

    def __init__(self):
        self.__dict__['_data'] = {}

    # Mecanismo write-once: permite escrever as variáveis apenas uma vez
    def __setattr__(self, attr, value):
        data_dir = self._data

        if attr in data_dir and self.has_init:
            old = data_dir[attr]
            msg = ('cannot change environment after initialization: '
                   '%s = %r --> %r' %
                   (attr, old, value))
            raise RuntimeError(msg)
        else:
            super(Conf, self).__setattr__(attr, value)

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
            self.window_shape = (int(x), int(y))

        elif args == ('fullcanvas',):
            self.window_shape = 'fullcanvas'

        else:
            raise TypeError('invalid arguments: %s' % args)

    def set_backend(self, backend=None):
        '''Define o backend a ser utilizado pela FGAme.

        Se for chamada sem nenhum argumento, tenta carregar os backends na
        ordem dada por self.backends. Se o argumento for uma lista, tenta
        carregar os backends na ordem especificada pela lista.'''

        # Função chamada sem argumentos
        if backend is None:
            if self.backend is None:
                backend = self.backends
            else:
                return  # backend já configurado!

        # Previne modificar o backend
        if self.backend is not None:
            if self.backend != backend:
                raise RuntimeError(
                    'already initialized to %s, cannot change the backend' %
                    self.backend)
            else:
                return

        # Carrega backend pelo nome
        if isinstance(backend, str):
            if not backends.supports_backend(backend):
                raise ValueError(
                    '%s backend is not supported in your system' %
                    backend)

            self.backend = backend
            self.backend_classes = backends.get_backend_classes(backend)
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

        if self.window_shape is None:
            self.window_shape = (800, 600)
        return self.window_shape

    def get_canvas(self):
        '''Retorna o objeto canvas inicializado'''

        return self.canvas_object or self.init_canvas()

    def get_input(self):
        '''Retorna o objeto canvas inicializado'''

        return self.input_object or self.init_input()

    def get_mainloop(self):
        '''Retorna o objeto canvas inicializado'''

        return self.mainloop_object or self.init_mainloop()

    ###########################################################################
    # Init functions
    ###########################################################################

    def init(self):
        '''Inicializa todas as classes relevantes do FGAme'''

        # Previne a inicialização repetida
        if self.has_init:
            return

        # Garante que exite um backend definido
        self.set_backend()

        # Inicializa o vídeo, input, mainloop, etc
        if self.canvas_object is None:
            self.canvas_object = self.init_canvas()

        if self.input_object is None:
            self.input_object = self.init_input()

        if self.mainloop_object is None:
            self.mainloop_object = self.init_mainloop()

        self.has_init = True

    def init_canvas(self, *args, **kwds):
        '''Inicializa a tela na resolução padrão de 800x600 ou na resolução
        especificada pelo usuário usando o método conf.set_resolution()'''

        if self.canvas_class is None:
            self.set_backend()
            self.canvas_class = self.backend_classes['screen']

        if not args:
            shape = self.window_shape or (800, 600)
            canvas = self.canvas_class(shape=shape, **kwds)
        elif len(args) == 2:
            canvas = self.canvas_class(shape=args, **kwds)
        elif args == ('fullscreen',):
            canvas = self.canvas_class(shape=args, **kwds)

        # Save environment variables
        self.window_shape = canvas.shape
        self.canvas_object = canvas
        canvas.init()
        return canvas

    def init_input(self):
        '''Inicializa o sistema de inputs de teclado e mouse.'''

        if self.input_class is None:
            self.set_backend()
            self.input_class = self.backend_classes['input']

        self.input_object = self.input_class()
        self.input_object.init()
        return self.input_object

    def init_mainloop(self):
        '''Inicializa o loop principal ou um cronômetro para os backends que
        já implementam um loop principal próprio.'''

        if self.mainloop_class is None:
            self.set_backend()
            self.mainloop_class = self.backend_classes['mainloop']

        self.mainloop_object = self.mainloop_class()
        self.mainloop_object.init()
        return self.mainloop_object
