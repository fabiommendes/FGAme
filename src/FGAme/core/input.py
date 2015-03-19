#-*- coding: utf8 -*-
from FGAme.core import EventDispatcher, signal
from FGAme.core import env
import string

class Input(EventDispatcher):
    '''Objetos do tipo listener escutam eventos de entrada do usuário e executam
    os callbacks de resposta registrados a estes eventos'''

    long_press = signal('long-press', 'key')
    key_up = signal('key-up', 'key')
    key_down = signal('key-down', 'key')
    mouse_motion = signal('mouse-motion', num_args=1)
    mouse_click = signal('mouse-click', 'button', num_args=1)

    def __init__(self):
        super(Input, self).__init__()
        self._longpress_keys = set()
    
    # Callbacks globais para cada tipo de evento -------------------------------
    def process_key_down(self, key):
        '''Executa todos os callbacks associados à tecla fornecida'''

        self.trigger_key_down(key)
        self._longpress_keys.add(key)

    def process_key_up(self, key):
        '''Executa todos os callbacks de keyup associados à tecla fornecida'''

        self.trigger_key_up(key)
        self._longpress_keys.discard(key)

    def process_long_press(self):
        '''Executa todos os callbacks de longpress para as teclas pressionadas'''

        for key in self._longpress_keys:
            self.trigger_long_press(key)

    def process_mouse_motion(self, pos):
        '''Executa os callbacks acionados pelo movimento do mouse'''

        self.trigger_mouse_motion(pos)

    def process_mouse_click(self, pos, button):
        '''Executa os callbacks acionados pelo movimento do mouse'''

        self.trigger_mouse_click(button, pos)

    #===========================================================================
    # Passo de resposta a eventos executado em cada loop
    #===========================================================================
    def query(self):
        '''Função executada a cada loop, que investiga todos os eventos de 
        usuários que ocorreram. Deve ser reimplementada nas classes filho'''

        raise NotImplementedError
    
#===============================================================================
# Backends
#===============================================================================
class PyGameInput(Input):
    '''Implementa a interface Input através do Pygame.'''

    def __init__(self):
        super(PyGameInput, self).__init__()
        
        # Registra conversão de teclas
        import pygame.locals as pg
        
        D = dict(up=pg.K_UP, down=pg.K_DOWN, left=pg.K_LEFT, right=pg.K_RIGHT,
            space=pg.K_SPACE,
        )
        D['return'] = pg.K_RETURN

        # Adiciona as letras e números
        chars = '0123456789' + string.ascii_lowercase
        for c in chars:
            D[c] = getattr(pg, 'K_' + c)
        
        self._key_conversions = { v: k for (k, v) in D.items() }
        
    #===========================================================================
    # Laço principal de escuta de eventos
    #===========================================================================
    def query(self):
        from pygame.locals import QUIT, KEYDOWN, KEYUP, MOUSEMOTION
        import pygame
        pygame.init()
        D = self._key_conversions
        
        for event in pygame.event.get():
            if event.type == QUIT:
                raise SystemExit
            elif event.type == KEYDOWN:
                self.process_key_down(D.get(event.key))
            elif event.type == KEYUP:
                self.process_key_up(D.get(event.key))
            elif event.type == MOUSEMOTION:
                x, y = event.pos
                y = env.window_height - y
                self.process_mouse_motion((x, y))

        self.process_long_press()
        
        
# from FGAme.backends.core import Canvas, InputListener
# import pygame
# import sdl2
# import sdl2.ext
# from sdl2.sdlgfx import *
# from sdl2 import *
# import string
# from math import trunc
# import ctypes        
class SDL2Input(Input):
    '''Objetos do tipo listener.'''

    #===========================================================================
    # Conversões entre strings e teclas
    #===========================================================================
#     # Setas direcionais
#     KEY_CONVERSIONS = {
#         'up': SDLK_UP, 'down': SDLK_DOWN, 'left': SDLK_LEFT, 'right': SDLK_RIGHT,
#         'return': SDLK_RETURN, 'space': SDLK_SPACE, 'enter': SDLK_RETURN,
#     }
# 
#     # Adiciona as letras e números
#     chars = '0123456789' + string.ascii_lowercase
#     for c in chars:
#         KEY_CONVERSIONS[c] = getattr(sdl2, 'SDLK_' + c)

    #===========================================================================
    # Laço principal de escuta de eventos
    #===========================================================================

    def query(self):
        for event in sdl2.ext.get_events():
            if event.type == SDL_QUIT:
                raise SystemExit
            elif event.type == SDL_KEYDOWN:
                self.on_key_down(event.key.keysym.sym)
            elif event.type == SDL_KEYUP:
                self.on_key_up(event.key.keysym.sym)
            elif event.type == SDL_MOUSEMOTION:
                # TODO: converter para coordenadas locais em screen
                #self.on_mouse_motion(event.pos)
                pass

        self.on_long_press()
        
        
if __name__ == '__main__':
    input = PyGameInput()
