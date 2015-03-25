# -*- coding: utf-8 -*-
import time
from FGAme.core import env


class MainLoop(object):

    '''Implementa o loop principal de jogo.

    Tarefas do Loop principal:
        * Realizar a leitura de entradas do usuário (mouse, teclado, etc)
        * Atualizar o estado de jogo
        * Atualizar a visualização
        * Tentar manter uma taxa de atualização fixa (se o computador permitir)
        * Gerenciar os estados de jogo (ex., coordenar entre estados de menu,
          jogo, configuração, etc)

    Parameters
    ----------
        fps : float
            Número de quadros por segundo que a simulação de física deve
            tentar rodar
    '''

    def __init__(self, fps=60):
        self.fps = fps
        self.dt = 1.0 / self.fps

    def init(self):
        '''Ações adicionais que devem ser feitas entre a alocação e execução
        do método run()'''

        pass

    def run(self, state, timeout=None):
        # Assegura que o motor de jogos foi inicializado
        from FGAme.core import init
        init()

        # Prepara o loop principal
        self._running = True
        sleep = time.sleep
        gettime = time.time
        input_ = env.input_object
        screen = env.canvas_object
        sim_start = gettime()
        screen.show()

        while self._running:
            t0 = gettime()

            # Captura entrada do usuário e atualiza o estado (e física) de
            # acordo
            input_.query()
            state.update(self.dt)

            # Desenha os objetos na tela
            screen.clear_background(state.background)
            screen.draw_tree(state.get_render_tree())
            screen.flip()

            # Espera até completar o frame
            t = gettime()
            wait = self.dt - (t - t0)
            t0 = t
            if wait > 0:
                sleep(wait)
            else:
                state.trigger('frame-skip', -wait)

            # Verifica que já ultrapassou o tempo de simulação
            if timeout is not None and t - sim_start > timeout:
                break

    def stop(self):
        '''Finaliza o jogo'''

        self._running = False
