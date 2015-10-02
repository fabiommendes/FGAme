from FGAme.events import EventDispatcher, signal


class Input(EventDispatcher):

    '''Objetos do tipo listener escutam eventos de entrada do usuário e executam
    os callbacks de resposta registrados a estes eventos.

    Esta classe define uma interface genérica que não implementa o método
    poll() que busca por eventos a cada frame de simulação. Este método deve
    ser implementado pelo backend específico (ex.: pygame, SDL2, etc)'''

    _instance = None
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

        if self._instance is None:
            Input._instance = self
        else:
            raise RuntimeError('Input() is a singleton')

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

    #
    # Consulta as entradas de comandos pelo usuário
    #
    def poll(self):
        '''Função executada a cada loop, que investiga todos os eventos de
        usuários que ocorreram. Deve ser reimplementada nas classes filho'''

        raise NotImplementedError

    #
    # Funções utilizadas como funções globais no módulo FGAme.input
    #
    def _on_key_down(self, key, func=None, *args, **kwds):
        '''Registra função func para ser executada no frame em que a tecla
        fornecida for pressionada'''

        return self.listen_key_down(key, func, *args, **kwds)

    def _on_key_up(self, key, func=None, *args, **kwds):
        '''Registra função func para ser executada no frame em que o usuário
        liberar a tecla fornecida previamente pressionada'''

        return self.listen_key_up(key, func, *args, **kwds)

    def _on_long_press(self, key, func=None, *args, **kwds):
        '''Registra função func para ser executada em todos os frames em que a
        tecla fornecida estiver pressionada.'''

        return self.listen_long_press(key, func, *args, **kwds)

    def _on_mouse_motion(self, func=None, *args, **kwds):
        '''Registra função que é executada a cada frame em que o mouse se
        mover dentro da janela do jogo.

        A função recebe as coordenadas do ponteiro como primeiro argumento'''

        return self.listen_mouse_motion(func, *args, **kwds)

    def _on_mouse_button_down(self, button, func=None, *args, **kwds):
        '''Semelhante à `on_key_down()`, mas rastreia os cliques do mouse.

        A função de callback recebe a posição do ponteiro como primeiro
        argumento. Os botões são "left", "right", "middle", "wheel-up" e
        "wheel-down".'''

        return self.listen_mouse_button_down(func, *args, **kwds)

    def _on_mouse_button_up(self, button, func=None, *args, **kwds):
        '''Semelhante à `on_key_up()`, mas rastreia os cliques do mouse.

        A função de callback recebe a posição do ponteiro como primeiro
        argumento. Os botões são "left", "right", "middle", "wheel-up" e
        "wheel-down".'''

        return self.listen_mouse_button_up(func, *args, **kwds)

    def _on_mouse_long_press(self, button, func=None, *args, **kwds):
        '''Semelhante à `on_long_press()`, mas rastreia os cliques do mouse.

        A função de callback recebe a posição do ponteiro como primeiro
        argumento. Os botões são "left", "right", "middle", "wheel-up" e
        "wheel-down".'''

        return self.listen_mouse_button_long_press(func, *args, **kwds)


#
# Registra as funções globais
#
def _register(func_name):
    input_method = getattr(Input, func_name)

    def signal_handler_func(*args, **kwds):
        try:
            worker = getattr(Input._instance, func_name)
        except AttributeError:
            raise RuntimeError(
                'Input system has not started. '
                'Have you tried to execute conf.init() first?')
        return worker(*args, **kwds)

    signal_handler_func.__name__ = input_method.__name__
    signal_handler_func.__doc__ = input_method.__doc__
    return signal_handler_func


on_key_down = _register('_on_key_down')
on_key_up = _register('_on_key_up')
on_long_press = _register('_on_long_press')
on_mouse_motion = _register('_on_mouse_motion')
on_mouse_button_down = _register('_on_mouse_button_down')
on_mouse_button_up = _register('_on_mouse_button_up')
on_mouse_long_press = _register('_on_mouse_long_press')
