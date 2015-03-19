# -*- coding: utf-8 -*-
import time
from FGAme.core import env

class MainLoop(object):
    '''Implements the main loop of application'''

    def __init__(self, fps=60):
        self.fps = fps
        self.dt = 1.0 / self.fps

    def run(self, state, timeout=None):
        # Assegura que o motor de jogos foi inicializado
        from FGAme.core import init
        init()

        # Prepara o loop principal        
        self._running = True
        sleep = time.sleep
        gettime = time.time
        input = env.input_object
        screen = env.canvas_object
        sim_start = gettime()
        
        while self._running:
            t0 = gettime()
            
            # Captura entrada do usuário e atualiza o estado (e física) de acordo
            input.query()
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
        self._running = False

class StepperMainLoop(MainLoop):
    pass
