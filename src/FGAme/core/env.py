#-*- coding: utf8 -*-

__all__ = ['env']


class Environment(object):

    '''Classe que atua apenas como um namespace para as variáveis globais.'''

    #=========================================================================
    # Propriedades relativas ao backend
    #=========================================================================
    backend = None
    backends = ['pygame', 'pygamegfx', 'pygamegl', 'sdl2']
    backend_classes = None

    #=========================================================================
    # Leitura de entradas do usuário
    #=========================================================================
    input_class = None
    input_object = None

    #=========================================================================
    # Propriedades da tela
    #=========================================================================
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

    #=========================================================================
    # Propriedades do loop principal
    #=========================================================================
    mainloop_class = None
    mainloop_object = None

    #=========================================================================
    # Controle de inicialização e configuração
    #=========================================================================
    has_init = False
    app_name = None
    conf_path = None

    #=========================================================================
    # Propriedades da simulação
    #=========================================================================
    physics_fps = 60
    physics_dt = 1 / 60.
    screen_fps = 60
    screen_dt = 1 / 60.


env = Environment()
