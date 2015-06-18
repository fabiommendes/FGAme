# -*- coding: utf8 -*-

from FGAme.events import EventDispatcher, signal


class Input(EventDispatcher):

    '''Objetos do tipo listener escutam eventos de entrada do usuário e executam
    os callbacks de resposta registrados a estes eventos'''

    long_press = signal('long-press', 'key')
    key_up = signal('key-up', 'key')
    key_down = signal('key-down', 'key')
    mouse_motion = signal('mouse-motion', num_args=1)
    mouse_button_up = signal('mouse-button-up', 'button', num_args=1)
    mouse_button_down = signal('mouse-button-down', 'button', num_args=1)
    mouse_long_press = signal('mouse-long-press', 'button', num_args=1)

    def __init__(self):
        super(Input, self).__init__()
        self._longpress_keys = set()
        self._longpress_mouse_buttons = set()
        self._mouse_pos = (0, 0)

    def init(self):
        pass

    # Callbacks globais para cada tipo de evento -----------------------------
    def process_key_down(self, key):
        '''Executa todos os callbacks associados à tecla fornecida'''

        self.trigger_key_down(key)
        self._longpress_keys.add(key)

    def process_key_up(self, key):
        '''Executa todos os callbacks de keyup associados à tecla fornecida'''

        self.trigger_key_up(key)
        self._longpress_keys.discard(key)

    def process_long_press(self):
        '''Executa todos os callbacks de longpress para as teclas
        pressionadas'''

        callback = self.trigger_long_press
        for key in self._longpress_keys:
            callback(key)

    def process_mouse_motion(self, pos):
        '''Executa callbacks associados ao movimento do mouse'''

        self.trigger_mouse_motion(pos)
        self._mouse_pos = pos

    def process_mouse_button_down(self, button, pos):
        '''Executa callbacks associados a pressionar um botão do mouse'''

        self.trigger_mouse_button_down(button, pos)
        self._longpress_mouse_buttons.add(button)

    def process_mouse_button_up(self, button, pos):
        '''Executa callbacks associados a levantar um botão previamente
        pressionado do mouse'''

        self.trigger_mouse_button_up(button, pos)
        self._longpress_mouse_buttons.discard(button)

    def process_mouse_longpress(self):
        '''Executa callbacks de long-press para os botões do mouse.

        A posição do ponteiro é guardada automaticamente no processamento dos
        sinais de 'mouse-motion'.'''

        pos = self._mouse_pos
        callback = self.trigger_mouse_long_press
        for button in self._longpress_mouse_buttons:
            callback(button, pos)

    ###########################################################################
    #             Passo de resposta a eventos executado em cada loop
    ###########################################################################
    def query(self):
        '''Função executada a cada loop, que investiga todos os eventos de
        usuários que ocorreram. Deve ser reimplementada nas classes filho'''

        raise NotImplementedError
