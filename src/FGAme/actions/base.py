from FGAme import schedule_iter_dt, schedule, unschedule
from FGAme.mathtools import Vec2, cos, sin
from FGAme.draw import Color


class RunnerControl(object):

    def __init__(self, action):
        self.is_cancelled = False
        self.action = action

    def _assure_cancelled(self):
        if self.is_cancelled:
            raise RuntimeError('cannot operate in a cancelled action')

    def cancel(self):
        unschedule(self.action)
        self.is_cancelled = True

    def pause(self):
        self._assure_cancelled()
        unschedule(self.action)

    def resume(self):
        schedule(self.action)


class Action(object):

    '''Classe mãe de todas as ações.


    Usamos a convenção que classes abstratas são nomeadas em CamelCase enquanto
    classes que realizam ações concretas são nomeadas como funções.
    '''
    instant = False

    def copy(self):
        '''Retorna copia de si mesmo'''

    def prepare(self, target=None, **kwds):
        '''Prepara a ação para iniciar a execução.'''

    def finish(self, target, **kwds):
        ''''''
        pass

    def start(self, target=None, **kwds):
        '''Executa a ação'''

        return schedule_iter_dt(self.runner, target, **kwds)

    def runner(self, dt, target=None, **kwds):
        raise NotImplementedError

    #
    # Define operações
    #
    def __rshift__(self, action):
        return sequence(self, action)

    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError("Can only multiply actions by ints")
        if other == 0:
            return DoNothingAction()
        elif other == 1:
            return self
        elif other > 1:
            return loop(self, other)
        else:
            raise ValueError('cannot loop a negative number of times')

    def __or__(self, action):
        return parallel(self, action)

    def __reversed__(self):
        raise Exception("Action %s cannot be reversed" % type(self).__name__)


class DoNothingAction(Action):

    def runner(self, *args, **kwds):
        yield


class ActionModifier(Action):

    def __init__(self, action):
        if not isinstance(action, Action):
            raise TypeError('must be initialized with an Action object')
        self.action = action


class InstantAction(Action):
    instant = True

    def runner(self, dt, target=None, **kwds):
        self.execute(target, **kwds)
        yield


class IntervalAction(Action):
    instant = False

    def __init__(self, duration):
        self.duration = float(duration)


class delay(IntervalAction):

    def runner(self, dt, target=None, **kwds):
        delay = self.duration
        time = 0.0
        while time < delay:
            time += dt
            yield


class sequence(Action):

    def __init__(self, *actions):
        self.actions = list(actions)

    def runner(self, dt, target=None, **kwds):
        for action in self.actions:
            if action.instant:
                action.execute(target, **kwds)
            else:
                for _ in action.runner(dt, target, **kwds):
                    yield


class parallel(Action):

    def __init__(self, *actions):
        self.actions = list(actions)

    def runner(self, dt, target=None, **kwds):
        iterators = [action.runner(dt, target, **kwds)
                     for action in self.actions]
        while iterators:
            finished = []
            for (idx, runner) in enumerate(iterators):
                try:
                    next(runner)
                except StopIteration:
                    finished.append(idx)
            if finished:
                for idx in reversed(finished):
                    iterators.pop(idx)


class move_to(IntervalAction):

    def __init__(self, pos, interval):
        super(move_to, self).__init__(interval)
        self.pos = Vec2(*pos)

    def runner(self, dt, target, **kwds):
        final_pos = self.pos
        interval = self.duration
        time = 0

        while time < interval:
            time += dt
            try:
                fraction = min(dt / (interval - time), 1.0)
            except ZeroDivisionError:
                fraction = 1.0

            if fraction <= 0.0:
                return
            else:
                target.pos += (final_pos - target.pos) * fraction
                yield


class move_by(move_to):

    def runner(self, dt, target, **kwds):
        time = 0
        interval = self.duration
        delta = self.pos * (dt / interval)

        while time < interval:
            time += dt
            target.pos += delta
            yield


class place_at(InstantAction):

    def __init__(self, x, y=None):
        if y is None:
            self.pos = Vec2(*x)
        else:
            self.pos = Vec2(x, y)

    def execute(self, target, **kwds):
        target.pos = self.pos


class hide(InstantAction):

    def execute(self, target, **kwds):
        target.hide()


class show(InstantAction):

    def execute(self, target, **kwds):
        target.show()


class toggle_visibility(InstantAction):

    def execute(self, target, **kwds):
        if target.visible:
            target.hide()
        else:
            target.show()


class stop(InstantAction):

    def execute(self, target, **kwds):
        target.vel *= 0


class call_function(InstantAction):

    def __init__(self, function, args=(), kwds={}, pass_target=False):
        self.function = function
        self.args = tuple(args)
        self.kwds = dict(kwds)
        self.pass_target = pass_target

    def execute(self, target=None, **kwds):
        args = self.args
        args = (target,) + args if self.pass_target else args
        kwds = self.kwds
        self.function(*args, **kwds)


class loop(ActionModifier):

    def __init__(self, action, iterations=None):
        super(loop, self).__init__(action)
        self.iterations = float('inf') if iterations is None else iterations

    def runner(self, *args, **kwds):
        i = 0
        while i < self.iterations:
            i += 1
            for _ in self.action.runner(*args, **kwds):
                yield


class ping_pong(ActionModifier):

    def runner(self, *args, **kwds):
        for _ in self.action.runner(*args, **kwds):
            yield
        for _ in reversed(self.action).runner(*args, **kwds):
            yield


class evolve(Action):

    def __init__(self, property_name, evolution, interval, relative=True):
        self.property_name = property_name
        self.evolution = evolution
        self.interval = interval
        self.relative = relative

    def runner(self, dt, target, **kwds):
        property_name = self.property_name
        evolution = self.evolution
        interval = self.interval
        relative = self.relative
        starting_value = getattr(target, property_name)
        time = 0

        while time < interval:
            time += dt
            new_value = evolution(time)
            if relative:
                new_value -= starting_value
            setattr(target, property_name, new_value)


class set_trajectory(Action):

    def __init__(self, trajectory, interval, relative=True):
        self.trajectory = trajectory
        self.interval = interval
        self.relative = relative

    def runner(self, dt, target, **kwds):
        time = 0
        interval = self.interval
        position = self.trajectory
        pos_shift = Vec2(0, 0) if not self.relative else target.pos

        while time < interval:
            time += dt
            target.pos = pos_shift + position(time)


class set_attribute(InstantAction):

    def __init__(self, attribute, value):
        self.attribute = attribute
        self.value = value

    def execute(self, target, **kwds):
        setattr(target, self.attribute, self.value)


class set_color(InstantAction):

    def __init__(self, color):
        self.color = Color(color)

    def execute(self, target, **kwds):
        target.color = self.color


class set_velocity(set_attribute):

    def __init__(self, velocity, vy=None):
        if vy is not None:
            velocity = (velocity, vy)
        super(set_velocity, self).__init__('vel', velocity)


class color_effect(IntervalAction):

    def __init__(self, effect, interval, *args, **kwds):
        super(color_effect, self).__init__(interval)
        self.effect = effect
        self.args = tuple(args)
        self.kwds = dict(kwds)

    def runner(self, dt, target, **kwds):
        target.color = self.color


class time_map(ActionModifier):

    def __init__(self, action, mapping=None):
        super(time_map, self).__init__(action)
        self.mapping = mapping or self._default_mapping

    def _default_mapping(self, tau):
        return tau


class accelerate(time_map):

    def _default_mapping(self, tau):
        return tau ** 2


class deaccelerate(time_map):

    def _default_mapping(self, tau):
        return 1 - (tau - 1) ** 2


class finish_game(InstantAction):

    def __init__(self, *args):
        self.args = args

    def execute(self, *args, **kwds):
        raise SystemExit(*args)


class destroy(InstantAction):

    def execute(self, target, **kwds):
        target.destroy()


class add_to(InstantAction):

    def __init__(self, world):
        self.world = world

    def execute(self, target, **kwds):
        self.world.add(target)


class from_generator(Action):

    def __new__(self, generator=None, *args, **kwds):
        if generator is None or generator is Ellipsis:
            def decorator(generator):
                return from_generator(generator, *args, **kwds)
            return decorator

        new = object.__new__(from_generator)
        new.generator = generator
        new.args = tuple(args)
        return new
        self.kwds = dict(kwds)

    def runner(self, *args, **kwds):
        for _ in self.generator(*args, **kwds):
            yield


class step_forward(IntervalAction):

    def __init__(self, step, duration):
        super(step_forward, self).__init__(duration)
        self.step = step

    def runner(self, dt, target, **kwds):
        n_steps = dt / self.duration
        delta = self.step / n_steps

        for _ in range(n_steps):
            target.pos += Vec2.from_polar(delta, target.theta)


if __name__ == '__main__':
    from FGAme import *
    w = World()
    circles = [draw.Circle(10, pos=pos.middle) for _ in range(20)]
    w.add(circles)

    action = (delay(0.5) >> place_at(0, 0) >> delay(0.5)
              >> move_to(pos.middle, 1) >> set_color('red'))

    for idx, c in enumerate(circles):
        (delay(0.1 + 0.1 * idx) >> action).start(c)

    w.run()
