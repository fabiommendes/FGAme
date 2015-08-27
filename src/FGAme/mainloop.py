# -*- coding: utf-8 -*-
import time
from collections import deque, namedtuple
from FGAme.core import conf
from FGAme.events import EventDispatcher, signal


TimedAction = namedtuple('TimedAction', ['time', 'action', 'args', 'kwds'])


class MainLoop(EventDispatcher):

    '''Implementa o loop principal de jogo.

    Tarefas do Loop principal:
        * Realizar a leitura de entradas do usuário (mouse, teclado, etc) e
          executar ações pertinentes.
        * Atualizar o estado de jogo
        * Atualizar a visualização
        * Tentar manter uma taxa de atualização fixa (se o computador permitir)
        * Agendar tarefas
        * Gerenciar os estados de jogo (ex., coordenar entre estados de menu,
          jogo, configuração, etc)

    Parameters
    ----------
        fps : float
            Número de quadros por segundo que a simulação de física deve
            tentar rodar.
        time : float (padrão=0.0)
            Tempo de simulação a partir do do método run(). Pode defasar com
            relação ao tempo real devido à eventos de "frame-skip"
        n_iter : int (padrão=0)
            Número de frames processados. É incrementado a cada passo de
            simulação.
        clock : Clock
            Objeto do tipo clock. Serve como controle para a execução de ações
            programadas.

    Attributes
    ----------

    Todos os parâmetros estão disponíveis como atributos. Além destes, temos

        dt : float
            Recíproco de fps, mostra o tempo esperado gasto em cada frame.
        n_skip : int
            Número de frames pulados durante a simulação.


    Sinais
    ------

    pre-draw
        Emitido antes de iniciar a renderização principal, mas após pintar o
        fundo. O callback possui a assinatura callback(screen), onde `screen`
        é o objecto que realiza a renderização na tela no backend selecionado.
    post-draw
        Semelhante ao pre-draw, mas executado após a renderização principal.
    frame-skip
        Acionado sempre que houver uma perda de frames na simulação. O callback
        é chamado como callback(dt), onde dt é o tempo que extrapolou o máximo
        para aquele frame, em segundos. Ex.: se cada frame deve rodar em 0.1s e
        um determinado frame gastou 0.15s, então o callback é acionado com 0.05
        no argumentoframe

    '''

    pre_draw = signal('pre-draw', num_args=1)
    post_draw = signal('post-draw', num_args=1)
    frame_skip = signal('frame-skip', num_args=1)

    def __init__(self, fps=None, time=0.0, n_iter=0, clock=None):
        super(MainLoop, self).__init__()
        self.fps = conf.screen_fps
        self.dt = 1.0 / self.fps
        self.time = 0.0
        self.n_iter = 0
        self.n_skip = 0
        self._running = False
        self._action_queue = deque()

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
            Deve suportar o método state.update(dt), que atualiza o estado
            dado.
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
        conf.init()
        conf.canvas_object.show()  # @UndefinedVariable
        timeout = float('inf') if timeout is None else float(timeout)
        timeout += self.time
        maxiter = float('inf') if maxiter is None else maxiter
        maxiter += self.n_iter

        self._running = True
        while self._running:
            self.step(state, wait=wait)

            # Verifica que já ultrapassou o tempo de simulação
            if timeout is not None and self.time >= timeout:
                break
            if maxiter is not None and self.n_iter >= maxiter:
                break

            # Executa ações one_shot após o término dos frames
            Q = self._action_queue
            while Q and (self.time > Q[0].time):
                x = Q.popleft()
                x.action(*x.args, **x.kwds)

    def step(self, state, wait=True):
        '''Realiza um passo de simulação sobre o estado fornecido'''

        start_time = time.time()
        canvas = conf.canvas_object

        # Captura entrada do usuário
        conf.input_object.poll()  # @UndefinedVariable

        # Atualiza o estado (física e animações) de acordo
        state.update(self.dt)

        # Desenha os objetos na tela
        bg_color = getattr(state, 'background', 'white')
        if bg_color is not None:
            canvas.clear_background(bg_color)
        self.trigger_pre_draw(canvas)
        state.get_render_tree().draw(canvas)
        self.trigger_post_draw(canvas)
        canvas.flip()

        if wait:
            time_interval = time.time() - start_time
            wait_time = self.dt - time_interval
            if wait_time > 0:
                time.sleep(wait_time)
            else:
                self.n_skip += 1
                self.trigger_frame_skip(-wait)

        self.time += self.dt
        self.n_iter += 1

    def stop(self):
        '''Finaliza o loop principal'''

        self._running = False

    def one_shot(self, action, time, *args, **kwds):
        '''Agenda a execução da ação dada para acontecer imediatamente após
        transcorridos o número de segundos fornecidos. A ação será executada
        logo após o fim de cada passo, antes de iniciar o frame seguinte.'''

        timed_action = TimedAction(self.time + time, action, args, kwds)
        self._action_queue.append(timed_action)
        self._action_queue.sort(key=lambda x: x.time)

    def one_shot_frames(self, action, n_frames, *args, **kwds):
        '''Similar a one_shot, mas agenda a execução para ocorrer em um número
        de frames especificado'''

        self.one_shot(action, n_frames * self.dt, *args, **kwds)

    def one_shot_absolute(self, action, time, *args, **kwds):
        '''Similar a one_shot, mas agenda a execução para ocorrer em um valor
        específico de tempo e não após transcorrido o intervalo dado.

        A ação é executada imediatamente se o tempo de simulação superar o
        valor de time.'''

        self.one_shot(action, time - self.time, *args, **kwds)

    def schedule(self, action, time_interval, *args, **kwds):
        '''Similar à one_shot, mas agenda a simulação para ocorrer
        repetidamente cada vez que passar o intervalo de tempo fornecido.'''

        def recursive_action():
            action(*args, **kwds)
            self.one_shot(recursive_action, time_interval)

        self.one_shot(recursive_action, time_interval)

    def schedule_frames(self, action, n_frames, *args, **kwds):
        '''Similar à schedule(), mas agenda o intervalo de execução em frames
        ao invés de segundos'''

        self.schedule(action, n_frames * self.dt, *args, **kwds)
