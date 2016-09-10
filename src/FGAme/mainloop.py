import functools
import time
from collections import deque, namedtuple

from FGAme.signals import global_signal

frame_enter_signal = global_signal('frame-enter')
frame_leave_signal = global_signal('frame-leave', [], ['dt'])
frame_skip_signal = global_signal('frame-skip', [], ['ms'])
simulation_start_signal = global_signal('simulation-start')
pre_draw_signal = global_signal('pre-draw-signal', [], ['screen'])
post_draw_signal = global_signal('post-draw-signal', [], ['screen'])

TimedAction = namedtuple('TimedAction', ['time', 'action', 'args', 'kwds'])


class MainLoop:
    """
    Implements FGAme's main loop.

    The main loop do these tasks at each iteration:
        * Read user input (mouse, keyboard, etc)
        * Update game state.
        * Update screen
        * Keeps an steady frame rate if computer processing allows it.
        * Schedule tasks
        * Manage game states.

    Args:
        screen (Screen):
            Initialized screen object for the current backend.
        input:
            Initialized input object for the current backend.
        fps (float):
            Desired frame rate.
    """

    _instance = None

    def __init__(self, screen, input, fps=None):
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
        """Starts the main loop.

        Args:

        state:
            Game state object. Can be an instance of World.
        timeout:
            If given, finish simulation after the runtime is expired.
        maxiter:
            If given, finish simulation after the given number of frames.
        wait:
            If False, do not wait between two frames to keep the frame rate
            constant. This can be useful in testing and debugging.
        """

        timeout = float('inf') if timeout is None else float(timeout)
        timeout += self.time
        maxiter = float('inf') if maxiter is None else maxiter
        maxiter += self.n_iter

        self._running = True
        simulation_start_signal.trigger()
        while self._running:
            self.step(state, wait=wait)
            if timeout is not None and self.time >= timeout:
                break
            if maxiter is not None and self.n_iter >= maxiter:
                break

    def step_framestart(self):
        """
        Starts frame.
        """

        start_time = time.time()
        frame_enter_signal.trigger()

        # Execute queued one-shot actions
        Q = self._action_queue
        while Q and (self.time > Q[0].time):
            x = Q.popleft()
            x.action(*x.args, **x.kwds)
        return start_time

    def step_input(self, state):
        """
        Process user input.

        The default implementation simply calls the .poll() method of the input
        object.
        """

        self.input.poll()

    def step_state(self, state):
        """
        Update the given state object.

        The default implementation simply calls the .update() method with the
        desired frame duration.
        """

        state.update(self.dt)

    def step_screen(self, state):
        """
        Draw objects on the screen.
        """

        screen = self.screen
        bg_color = getattr(state, 'background', 'white')
        pre_draw_signal.trigger(screen)
        if bg_color is not None:
            screen.clear_background(bg_color)
        state.render_tree().draw(screen.camera)
        post_draw_signal.trigger(screen)
        screen.flip()

    def step_endframe(self, state, start_time, wait=True):
        """
        Finalize frame processing.
        """

        time_interval = time.time() - start_time
        self.sleep_time = self.dt - time_interval
        frame_leave_signal.trigger(time_interval)

        # Recompute the sleep time since frame_leave_signal processing can
        # consume a few cycles
        time_interval = time.time() - start_time
        self.sleep_time = self.dt - time_interval
        if self.sleep_time < 0:
            self.n_skip += 1
            frame_skip_signal.trigger(-wait)
        elif wait:
            time.sleep(self.sleep_time)

        self.time += self.dt
        self.n_iter += 1

    def step(self, state, wait=True):
        """
        Update simulation by a single step.
        """

        start_time = self.step_framestart()
        self.step_input(state)
        self.step_state(state)
        self.step_screen(state)
        self.step_endframe(state, start_time, wait)

    def stop(self):
        """
        Stops main loop.
        """

        self._running = False

    def schedule(self, time, function=None, args=None, kwargs=None,
                 **passed_kwargs):
        """
        Schedule function to execute immediately after the given duration (in
        seconds) is elapsed.

        Actions are always executed in the end of the frame. Additional
        keyword arguments are passed to the function.

        Example:
            This function can be used as a function or a decorator:

            >>> @schedule(1)
            ... def move_to(pos):
            ...     player.pos = 10, 20

            This schedules the `player` object to move to the given position
            after one second.
        """

        # Decorator form
        if function is None or function is ...:
            def decorator(func):
                return self.schedule(time, func, args, kwargs, **passed_kwargs)

            return decorator

        Q = self._action_queue
        kwargs = kwargs or {}
        kwargs.update(passed_kwargs)
        Q.append(TimedAction(self.time + time, function, args or (), kwargs))
        self._action_queue = deque(sorted(Q, key=lambda x: x.time))

    def schedule_steps(self, n_frames, function=None, args=None, kwargs=None,
                       **passed_kwargs):
        """
        Similar to schedule(time, function), but counts the number of frames
        rather than the number of seconds to execution.
        """

        return self.schedule(n_frames * self.dt, function, args, kwargs,
                             **passed_kwargs)

    def schedule_at(self, time, function=None, args=None, kwargs=None,
                    **passed_kwargs):
        """
        Similar to schedule, but marks execution to an specific instant in the
        absolute time line.

        The schedule function interprets time as a relative interval.
        """

        if time > self.time:
            return self.schedule(time - self.time, function, args, kwargs,
                                 **passed_kwargs)

    def periodic(self, delta_t, function=None, args=None, kwargs=None, **passed_kwargs):
        """
        Schedule function to execute every delta_t seconds.


        """

        # Decorador
        if function is None or function is Ellipsis:
            def decorator(func):
                return self.periodic(delta_t, func, *args, **kwds)

            return decorator

        def recursive_action(*r_args, **r_kwds):
            function(*r_args, **r_kwds)
            self.one_shot(delta_t, recursive_action, *args, **kwds)

        self.schedule(0, recursive_action, *args, **kwds)

    def periodic_steps(self, n_frames, function=None, *args, **kwds):
        """Similar à periodic(), mas agenda o intervalo de execução em frames
        ao invés de segundos"""

        self.periodic(n_frames * self.dt, function, *args, **kwds)
    #
    # def schedule_every_frame(self, function=None, *args, **kwds):
    #     """Agenda função para ser executada em cada frame.
    #
    #     Parameters
    #     ----------
    #
    #     function : callable
    #         Função a ser executada em cada frame. Por padrão, a função não
    #         recebe nenhum parâmetro, no entanto os parâmetros posicionais ou
    #         por nome adicionais são repassados.
    #     start : bool
    #         Determina se a ação deve ser executada no início ou ao final do
    #         frame. (padrão=True)
    #     skip : int ou tuple
    #         Determina quantos frames são pulados a cada execução. Por exemplo,
    #         se skip=2, a função é executada a cada dois frames. (padrão=1)
    #         Se for uma tupla (x, y), o primeiro valor representa o intervalo
    #         e o segundo representa quantos frames é necessário esperar para
    #         iniciar a execução.
    #     """
    #
    #     # Decorator form
    #     if function is None or function is Ellipsis:
    #         def decorator(func):
    #             return self.schedule(func, *args, **kwds)
    #
    #         return decorator
    #
    #     skip = kwds.pop('skip', 1)
    #     if skip != 1:
    #         raise NotImplementedError
    #
    #     if kwds.pop('start', True):
    #         return self.frame_enter.listen(function, *args, **kwds)
    #     else:
    #         return self.frame_leave.listen(function, *args, **kwds)
    #
    # def schedule_dt(self, function=None, *args, **kwds):
    #     """Similar à `schedule()`, mas utiliza uma função que recebe o
    #     intervalo de tempo `dt` transcorrido entre cada frame como primeiro
    #     parâmetro.
    #     """
    #
    #     return self.schedule(function, self.dt, *args, **kwds)
    #
    # def schedule_optional(self, function, *args, **kwds):
    #     """Agenda ação para executar ao final de cada frame se o mesmo não
    #     tiver estourado o tempo limite.
    #
    #     Útil para executar ações de manutenção que podem ser adiadas para
    #     quando a CPU estiver mais livre.
    #     """
    #
    #     mainloop = MainLoop._instance
    #
    #     def optional_action():
    #         if mainloop.sleep_tile:
    #             function()
    #
    #     return self.schedule(optional_action, start=False)
    #
    # def schedule_optional_dt(self, function, *args, **kwds):
    #     """Similar à `schedule_optional()`, mas utiliza uma função que recebe o
    #     intervalo de tempo `dt` transcorrido entre cada frame como primeiro
    #     parâmetro.
    #     """
    #
    #     self.schedule_optional(function, self.dt, *args, **kwds)
    #
    # def schedule_iter(self, iterator, *args, **kwds):
    #     """Agenda a execução de um iterador ou gerador em um passo a cada frame.
    #
    #     Quando o gerador for totalmente consumido, ele é eliminado do loop de
    #     execução.
    #
    #     Parameters
    #     ----------
    #
    #     iterator :
    #         Qualquer iterador ou gerador. O loop principal chamará
    #         repetidamente next_level(iterator) para cada frame executado.
    #     start : bool
    #         Determina se a ação será executada no início ou no fim do frame.
    #     skip : int
    #         Executa as ações a cada skip (padrão skip=1) frames.
    #     """
    #
    #     start = kwds.pop('start', True)
    #     skip = kwds.pop('skip', 1)
    #
    #     # Inicia variáveis
    #     action_id = None
    #     idx = [1]
    #
    #     # Aceita uma função geradora como entrada (funções com cláusula yield)
    #     try:
    #         iterator = iter(iterator)
    #     except TypeError:
    #         iterator = iterator(*args, **kwds)
    #
    #     def step():
    #         try:
    #             if idx[0] % skip == 0:
    #                 next_level(iterator)
    #         except StopIteration:
    #             mainloop = MainLoop._instance
    #             if start:
    #                 mainloop.frame_enter.remove(action_id)
    #             else:
    #                 mainloop.frame_leave.remove(action_id)
    #         idx[0] += 1
    #
    #     action_id = self.schedule(step, start=start)
    #     return action_id
    #
    # def schedule_iter_dt(self, iterator, *args, **kwds):
    #     """Similar à `schedule_iter()`, mas utiliza uma função que recebe o
    #     intervalo de tempo `dt` transcorrido entre cada frame como primeiro
    #     parâmetro.
    #     """
    #
    #     self.schedule_iter(iterator, self.dt, *args, **kwds)
    #
    # def delayed(self, time, function=None, *args, **kwds):
    #     """Semelhante à schedule, mas atrasa a execução da função pelo tempo
    #     especificado"""
    #
    #     # Decorador
    #     if function is None:
    #         def decorator(func):
    #             return self.delayed(time, func, *args, **kwds)
    #
    #         return decorator
    #
    #     def do_schedule():
    #         self.schedule(function, *args, **kwds)
    #
    #     return self.one_shot(time, do_schedule)
    #
    # def delayed_frames(self, n_frames, function=None, *args, **kwds):
    #     """Semelhante à delayed(), mas especifica um número de frames ao invés
    #     do intervalo de tempo"""
    #
    #     return self.delayed(self.dt * n_frames, function, *args, **kwds)
    #
    # def delayed_absolute(self, time, function=None, *args, **kwds):
    #     """Semelhante à delayed(), mas inicia após a simulação atingir um valor
    #     absoluto de tempo."""
    #
    #     return self.delayed(time - self.time, function, *args, **kwds)
    #
    # def unschedule(self, handler):
    #     """Remove uma ação da execução"""
    #
    #     # TODO: make everything cancellable!
    #     mainloop = MainLoop._instance
    #     if mainloop is not None:
    #         mainloop.frame_enter.remove(handler)
    #         mainloop.frame_leave.remove(handler)
    #     else:
    #         raise RuntimeError('cannot unschedule action from simulation that '
    #                            'has not started')


# Global schedulers
def _scheduler_factory(name):
    """
    Scheduler function that calls the corresponding method in the correct
    mainloop instance.
    """

    @functools.wraps(getattr(MainLoop, name))
    def scheduler_function(*args, **kwds):
        try:
            func = getattr(MainLoop._instance, name)
        except AttributeError:
            raise RuntimeError('MainLoop is not configured')
        return func(*args, **kwds)

    globals()[name] = scheduler_function
    return scheduler_function


schedule = _scheduler_factory('schedule')
schedule_steps = _scheduler_factory('schedule_steps')
schedule_at = _scheduler_factory('schedule_at')
# one_shot_absolute = _scheduler_factory('one_shot_absolute')
# periodic = _scheduler_factory('periodic')
# periodic_frames = _scheduler_factory('periodic_frames')
# schedule = _scheduler_factory('schedule')
# schedule_optional = _scheduler_factory('schedule_optional')
# schedule_iter = _scheduler_factory('schedule_iter')
# schedule_dt = _scheduler_factory('schedule_dt')
# schedule_optional_dt = _scheduler_factory('schedule_optional_dt')
# schedule_iter_dt = _scheduler_factory('schedule_iter_dt')
# delayed = _scheduler_factory('delayed')
# delayed_frames = _scheduler_factory('delayed_frames')
# delayed_absolute = _scheduler_factory('delayed_absolute')
# unschedule = _scheduler_factory('unschedule')
