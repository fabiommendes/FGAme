# -*- coding: utf-8 -*-
import time
import functools
from collections import deque, namedtuple
from FGAme.events import EventDispatcher, signal


TimedAction = namedtuple('TimedAction', ['time', 'action', 'args', 'kwds'])


class MainLoop(EventDispatcher):

    '''Implementa o loop principal de jogo.

    Tarefas do Loop principal:
        * Realizar a leitura de entradas do usuário (mouse, teclado, etc) e
          executar ações pertinentes.
        * Atualizar o estado de jogo
        * Atualizar a visualização
        * Tentar manter uma taxa de atualização fixa (se a capacidade de
          processamento do computador permitir)
        * Agendar tarefas
        * Gerenciar os estados de jogo (ex., coordenar entre estados de menu,
          jogo, configuração, etc)

    Parameters
    ----------

    screen : Screen
        Objeto do tipo Screen já inicializado.
    input : Screen
        Objeto do tipo Input já inicializado.
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
    sleep_time : float
        Tempo necessário dormir que manteria a taxa de atualização constante.


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
    frame_enter = signal('frame-enter')
    frame_frame_leave = signal('frame-leave')
    _instance = None

    def __init__(self, screen, input, fps=None):  # @ReservedAssignment
        super(MainLoop, self).__init__()
        self.screen = screen
        self.input = input
        self.fps = fps or 60
        self.dt = 1.0 / self.fps
        self.time = 0.0
        self.sleep_time = 0.0
        self.n_iter = 0
        self.n_skip = 0
        self._running = False
        self._action_queue = deque()

        if self._instance is not None:
            raise RuntimeError('MainLoop is a singleton')
        else:
            MainLoop._instance = self

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

    def step(self, state, wait=True):
        '''Realiza um passo de simulação sobre o estado fornecido'''

        start_time = time.time()
        self.trigger_frame_enter()

        # Executa ações one_shot no início dos frames
        Q = self._action_queue
        while Q and (self.time > Q[0].time):
            x = Q.popleft()
            x.action(*x.args, **x.kwds)

        # Captura entrada do usuário
        self.input.poll()  # @UndefinedVariable

        # Atualiza o estado (física e animações) de acordo
        state.update(self.dt)

        # Desenha os objetos na tela
        screen = self.screen
        bg_color = getattr(state, 'background', 'white')
        if bg_color is not None:
            screen.clear_background(bg_color)
        self.trigger_pre_draw(screen)
        state.get_render_tree().draw(screen)
        self.trigger_post_draw(screen)
        screen.flip()

        # Finaliza o frame
        time_interval = time.time() - start_time
        self.sleep_time = self.dt - time_interval
        self.trigger_frame_leave()

        # Recalcula o tempo de dormir pois frame_leave() pode ter consumido
        # alguns ciclos
        time_interval = time.time() - start_time
        self.sleep_time = self.dt - time_interval
        if wait:
            if self.sleep_time > 0:
                time.sleep(self.sleep_time)
            else:
                self.n_skip += 1
                self.trigger_frame_skip(-wait)

        self.time += self.dt
        self.n_iter += 1

    def stop(self):
        '''Finaliza o loop principal'''

        self._running = False

    def one_shot(self, time, function=None, *args, **kwds):
        '''Agenda a execução da ação dada para acontecer imediatamente após
        transcorridos o número de segundos fornecidos. A ação será executada
        logo após o fim de cada passo, antes de iniciar o frame seguinte.
        '''

        # Decorator form
        if function is None or function is Ellipsis:
            def decorator(func):
                return self.one_shot(time, func, *args, **kwds)
            return decorator

        Q = self._action_queue
        Q.append(TimedAction(self.time + time, function, args, kwds))
        self._action_queue = deque(sorted(Q, key=lambda x: x.time))

    def one_shot_frames(self, n_frames, function=None, *args, **kwds):
        '''Similar a one_shot, mas agenda a execução para ocorrer em um número
        de frames especificado
        '''

        return self.one_shot(n_frames * self.dt, function, *args, **kwds)

    def one_shot_absolute(self, time, function=None, *args, **kwds):
        '''Similar a one_shot, mas agenda a execução para ocorrer em um valor
        absoluto na linha de tempo e não após transcorrido o intervalo dado.
        '''

        return self.one_shot(time - self.time, function, *args, **kwds)

    def periodic(self, time_interval, function=None, *args, **kwds):
        '''Similar à one_shot, mas agenda a simulação para ocorrer
        repetidamente cada vez que passar o intervalo de tempo fornecido.'''

        # Decorador
        if function is None or function is Ellipsis:
            def decorator(func):
                return self.periodic(time_interval, func, *args, **kwds)
            return decorator

        def recursive_action(*r_args, **r_kwds):
            function(*r_args, **r_kwds)
            self.one_shot(time_interval, recursive_action, *args, **kwds)

        self.one_shot(0, recursive_action, *args, **kwds)

    def periodic_frames(self, n_frames, function=None, *args, **kwds):
        '''Similar à periodic(), mas agenda o intervalo de execução em frames
        ao invés de segundos'''

        self.periodic(n_frames * self.dt, function, *args, **kwds)

    def schedule(self, function=None, *args, **kwds):
        '''Agenda função para ser executada em cada frame.

        Parameters
        ----------

        function : callable
            Função a ser executada em cada frame. Por padrão, a função não
            recebe nenhum parâmetro, no entanto os parâmetros posicionais ou
            por nome adicionais são repassados.
        start : bool
            Determina se a ação deve ser executada no início ou ao final do
            frame. (padrão=True)
        skip : int ou tuple
            Determina quantos frames são pulados a cada execução. Por exemplo,
            se skip=2, a função é executada a cada dois frames. (padrão=1)
            Se for uma tupla (x, y), o primeiro valor representa o intervalo
            e o segundo representa quantos frames é necessário esperar para
            iniciar a execução.
'''

        # Decorator form
        if function is None or function is Ellipsis:
            def decorator(func):
                return self.schedule(func, *args, **kwds)
            return decorator

        skip = kwds.pop('skip', 1)
        if skip != 1:
            raise NotImplementedError

        if kwds.pop('start', True):
            return self.frame_enter.listen(function, *args, **kwds)
        else:
            return self.frame_leave.listen(function, *args, **kwds)

    def schedule_dt(self, function=None, *args, **kwds):
        '''Similar à `schedule()`, mas utiliza uma função que recebe o
        intervalo de tempo `dt` transcorrido entre cada frame como primeiro
        parâmetro.
        '''

        return self.schedule(function, self.dt, *args, **kwds)

    def schedule_optional(self, function, *args, **kwds):
        '''Agenda ação para executar ao final de cada frame se o mesmo não
        tiver estourado o tempo limite.

        Útil para executar ações de manutenção que podem ser adiadas para
        quando a CPU estiver mais livre.
        '''

        mainloop = MainLoop._instance

        def optional_action():
            if mainloop.sleep_tile:
                function()

        return self.schedule(optional_action, start=False)

    def schedule_optional_dt(self, function, *args, **kwds):
        '''Similar à `schedule_optional()`, mas utiliza uma função que recebe o
        intervalo de tempo `dt` transcorrido entre cada frame como primeiro
        parâmetro.
        '''

        self.schedule_optional(function, self.dt, *args, **kwds)

    def schedule_iter(self, iterator, *args, **kwds):
        '''Agenda a execução de um iterador ou gerador em um passo a cada frame.

        Quando o gerador for totalmente consumido, ele é eliminado do loop de
        execução.

        Parameters
        ----------

        iterator :
            Qualquer iterador ou gerador. O loop principal chamará
            repetidamente next(iterator) para cada frame executado.
        start : bool
            Determina se a ação será executada no início ou no fim do frame.
        skip : int
            Executa as ações a cada skip (padrão skip=1) frames.
        '''

        start = kwds.pop('start', True)
        skip = kwds.pop('skip', 1)

        # Inicia variáveis
        action_id = None
        idx = 1

        # Aceita uma função geradora como entrada (funções com cláusula yield)
        try:
            iterator = iter(iterator)
        except TypeError:
            iterator = iterator(*args, **kwds)

        def step():
            nonlocal idx

            try:
                if idx % skip == 0:
                    next(iterator)
            except StopIteration:
                mainloop = MainLoop._instance
                if start:
                    mainloop.frame_enter.remove(action_id)
                else:
                    mainloop.frame_leave.remove(action_id)
            idx += 1

        action_id = self.schedule(step, start=start)
        return action_id

    def schedule_iter_dt(self, iterator, *args, **kwds):
        '''Similar à `schedule_iter()`, mas utiliza uma função que recebe o
        intervalo de tempo `dt` transcorrido entre cada frame como primeiro
        parâmetro.
        '''

        self.schedule_iter(iterator, self.dt, *args, **kwds)

    def delayed(self, time, function=None, *args, **kwds):
        '''Semelhante à schedule, mas atrasa a execução da função pelo tempo
        especificado'''

        # Decorador
        if function is None:
            def decorator(func):
                return self.delayed(time, func, *args, **kwds)
            return decorator

        def do_schedule():
            self.schedule(function, *args, **kwds)

        return self.one_shot(time, do_schedule)

    def delayed_frames(self, n_frames, function=None, *args, **kwds):
        '''Semelhante à delayed(), mas especifica um número de frames ao invés
        do intervalo de tempo'''

        return self.delayed(self.dt * n_frames, function, *args, **kwds)

    def delayed_absolute(self, time, function=None, *args, **kwds):
        '''Semelhante à delayed(), mas inicia após a simulação atingir um valor
        absoluto de tempo.'''

        return self.delayed(time - self.time, function, *args, **kwds)

    def unschedule(self, handler):
        '''Remove uma ação da execução'''

        # TODO: make everything cancellable!
        mainloop = MainLoop._instance
        if mainloop is not None:
            mainloop.frame_enter.remove(handler)
            mainloop.frame_leave.remove(handler)
        else:
            raise RuntimeError('cannot unschedule action from simulation that '
                               'has not started')


#
# Global schedulers
#
def _make_scheduler(name):
    '''Cria uma função tipo "scheduler" que delega a ação para o objeto
    mainloop principal'''

    @functools.wraps(getattr(MainLoop, name))
    def scheduler_function(*args, **kwds):
        try:
            func = getattr(MainLoop._instance, name)
        except AttributeError:
            raise RuntimeError('MainLoop is not configured')
        return func(*args, **kwds)

    globals()[name] = scheduler_function
    return scheduler_function

one_shot = _make_scheduler('one_shot')
one_shot_frames = _make_scheduler('one_shot_frames')
one_shot_absolute = _make_scheduler('one_shot_absolute')
periodic = _make_scheduler('periodic')
periodic_frames = _make_scheduler('periodic_frames')
schedule = _make_scheduler('schedule')
schedule_optional = _make_scheduler('schedule_optional')
schedule_iter = _make_scheduler('schedule_iter')
schedule_dt = _make_scheduler('schedule_dt')
schedule_optional_dt = _make_scheduler('schedule_optional_dt')
schedule_iter_dt = _make_scheduler('schedule_iter_dt')
delayed = _make_scheduler('delayed')
delayed_frames = _make_scheduler('delayed_frames')
delayed_absolute = _make_scheduler('delayed_absolute')
unschedule = _make_scheduler('unschedule')


if __name__ == '__main__':
    from FGAme import World, Circle, pos
    w = World()
    c1 = Circle(10, world=w)
    c2 = Circle(10, color='red', world=w)
    c3 = Circle(10, color='blue', world=w)

    @schedule
    def move():
        c2.pos += (1, 1)

    @schedule_iter
    def move_circle():
        for _ in range(50):
            c1.pos += (2, 5)
            yield

    @periodic(1)
    def move_c3():
        c3.pos += (50, 30)

    @delayed(2)
    def move_circle2():
        c1.pos += (1, 0)

    @one_shot(3)
    def move_circle3():
        c1.pos = pos.middle

    w.run()
