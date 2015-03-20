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
    
