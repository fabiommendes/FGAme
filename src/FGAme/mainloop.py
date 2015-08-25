# -*- coding: utf-8 -*-
import time
from FGAme.core import conf
from FGAme.events import EventDispatcher, signal


class MainLoop(EventDispatcher):

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

    Sinais
    ------

    pre-draw :
        Emitido antes de iniciar a renderização principal, mas após pintar o
        fundo. O callback possui a assinatura callback(screen), onde `screen`
        é o objecto que realiza a renderização na tela no backend selecionado.
    post-draw :
        Semelhante ao pre-draw, mas executado após a renderização principal.
    '''

    pre_draw = signal('pre-draw', num_args=1)
    post_draw = signal('post-draw', num_args=1)

    def __init__(self, fps=None):
        super(MainLoop, self).__init__()
        self.fps = conf.screen_fps
        self.dt = 1.0 / self.fps

    def init(self):
        '''Ações adicionais que devem ser feitas entre a alocação e execução
        do método run()'''

        pass

    def run(self, state, timeout=None, maxiter=None, wait=True):
        '''Roda o loop principal.

        Parameters
        ----------

        state :
            Objeto que controla o estado principal do jogo ou aplicação.
            Deve suportar o método state.update(dt), que atualiza o estado dado
            um incremento temporal e o sinal 'frame-skip', que é disparado
            quando a computação demora mais que o frame-rate desejado.
        timeout : float
            Executa a simulação até o tempo máximo especificado.
        maxiter : int
            Define um número máximo de iterações.
        wait : bool
            Se wait=False, renderiza e atualiza cada frame imediatamente após
            o outro. Isto desabilita o controle de frame-rate e é utilizado
            apenas para depuração.
        '''

        # Assegura que o motor de jogos foi inicializado
        conf.init()  # @UndefinedVariable

        # Prepara o loop principal
        self._running = True
        sleep = time.sleep
        gettime = time.time
        input_ = conf.input_object  # @UndefinedVariable
        screen = conf.canvas_object  # @UndefinedVariable
        sim_start = gettime()
        screen.show()
        n_skip = 0
        n_iter = 0

        while self._running:
            n_iter += 1
            t0 = gettime()

            # Captura entrada do usuário e atualiza o estado (e física) de
            # acordo
            input_.poll()
            state.update(self.dt)

            # Desenha os objetos na tela
            screen.clear_background(getattr(state, 'background', 'white'))
            self.trigger_pre_draw(screen)
            state.get_render_tree().draw(screen)
            self.trigger_post_draw(screen)
            screen.flip()

            # Espera até completar o frame
            t = gettime()
            wait_time = self.dt - (t - t0)
            if wait_time > 0 and wait:
                sleep(max(0, wait_time))
            else:
                n_skip += 1
                state.trigger('frame-skip', -wait)
            t0 = t

            # Verifica que já ultrapassou o tempo de simulação
            if timeout is not None and t - sim_start >= timeout:
                break
            if maxiter is not None and n_iter >= maxiter:
                break

    def stop(self):
        '''Finaliza o jogo'''

        self._running = False
