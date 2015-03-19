#-*- coding: utf8 -*-
import importlib
from FGAme.core import log
from FGAme.core import env

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
        if  attr.startswith('_') and hasattr(self._env, attr[1:]):
            name = attr[1:]
            default = getattr(type(self._env), name)
            
            if getattr(self._env, name) == default:
                setattr(self._env, name, value)
            elif getattr(self._env, name) == value:
                pass
            elif self._env.has_init:
                msg = ('cannot change environment after initialization: %s = %s --> %s' % 
                       (name, getattr(self._env, name), value))
                raise RuntimeError(msg)
            else:
                raise RuntimeError('trying to reassign %s' % name)
        
        else:
            raise AttributeError(attr)
    #===========================================================================
    # Set state functions -- can be executed only before init
    #===========================================================================
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
        
        Se for chamada sem nenhum argumento, tenta carregar os backends na ordem
        dada por self.backends. Se o argumento for uma lista, tenta carregar os
        backends na ordem especificada pela lista.'''
    
        # Função chamada sem argumentos
        if backend is None:
            if self._backend is None:
                backend = self._backends
            else:
                return # backend já configurado!
        
        # Previne modificar o backend
        if self._backend is not None:
            if self._backend != backend:
                raise RuntimeError('already initialized to %s, cannot change the backend' % self._backend)
            else:
                return
        
        # Carrega backend pelo nome
        if isinstance(backend, str):
            if not self.supports_backend(backend):
                raise ValueError('%s backend is not supported in your system' % backend)
            
            canvas, input_, mainloop = self._backends_conf[backend]
            core = importlib.import_module('FGAme.core')
            self._canvas_class = getattr(core, canvas)
            self._input_class = getattr(core, input_)
            self._mainloop_class = getattr(core, mainloop)
            self._backend = backend
            log.info('conf: Backend set to %s' % backend)
            
        # Carrega backend a partir de uma lista
        else:
            for be in backend:
                if self.supports_backend(be):
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

    #===========================================================================
    # Query functions -- can be executed any time
    #===========================================================================
    def supports_backend(self, backend):
        '''Retorna True caso o sistema suporte o backend selecionado'''
        
        if backend in ['pygame', 'pygamegfx', 'pygamegl']:
            try:
                import pygame  # @UnusedImport
                return True
            except ImportError:
                return False
        elif backend == 'sdl2':
            try:
                import sdl2  # @UnusedImport
                return True
            except ImportError:
                return False
        else:
            raise ValueError('invalid backend: %s' % backend)
        
    def get_window_shape(self):
        '''Retorna uma tupla com a resolução da janela em pixels'''
        
        if self._window_shape is None:
            self._window_shape = (800, 600)
        return self._window_shape
    
    def get_canvas(self):
        '''Retorna o objeto canvas inicializado'''
        
        canvas = self._canvas_object
        if canvas is None:
            raise RuntimeError('canvas is not yet defined')
        return canvas
        
    #===========================================================================
    # Init functions
    # Implementadas com um _ inicial pois são exportadas publicamente no módulo
    # FGAme.core e não como método do objeto conf.
    #===========================================================================
    def _init(self):
        '''Inicializa todas as classes relevantes do FGAme'''
        
        # Previne a inicialização repetida
        if self._has_init:
            return
    
        # Garante que exite um backend definido
        self.set_backend()
        
        # Inicializa o vídeo, input, mainloop, etc
        if self._canvas_object is None:
            self._canvas_object = self._init_canvas()
        
        if self._input_object is None:
            self._input_object = self._init_input()
            
        if self._mainloop_object is None:
            self._mainloop_object = self._init_mainloop()
            
        self._has_init = True
    
    def _init_canvas(self, *args, **kwds):
        '''Inicia a tela'''
        
        # Encontra uma classe apropriada
        #FIXME: refatorar a organização dos backends
        if self._canvas_class is None:
            from FGAme.core.screen import PyGameCanvas
            self._canvas_class = PyGameCanvas
            
        if not args:
            obj = self._canvas_class(shape=self._window_shape or (800, 600), **kwds)
        elif len(args) == 2:
            obj = self._canvas_class(shape=args, **kwds)
        elif args == ('fullscreen',):
            obj = self._canvas_class(shape=args, **kwds)
        
        obj.start()
        self._canvas_object = obj
        return obj
        
    def _init_input(self):
        # Encontra uma classe apropriada
        #FIXME: refatorar a organização dos backends
        if self._input_class is None:
            from FGAme.core.input import PyGameInput
            self._input_class = PyGameInput
        
        return self._input_class()
    
    def _init_mainloop(self):
        # Encontra uma classe apropriada
        #FIXME: refatorar a organização dos backends
        if self._mainloop_class is None:
            from FGAme.core.mainloop import MainLoop
            self._mainloop_class = MainLoop
        
        return self._mainloop_class()
        