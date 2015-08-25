'''
Created on 01/07/2015

@author: chips
'''
# TODO: mudar run() para start() e fazer o run() iniciar um shell IPython

import functools as _functools
from collections import deque as _deque
import threading as _threading
import smallshapes as _mathtools
from FGAme.mathtools import Vec2
from FGAme import World as _World
from FGAme.draw import Pen as _Pen, Color
from FGAme import draw
import FGAme

_TURTLE = None
_PEN_LOCK = _threading.RLock()
_FGAME_THREAD = None
_RUNNING = False


class Turtle(_Pen):
    _blacklist = [
        'draw',
        'current', 'tip', 'move_tip',
        'lock_pen_z', 'lock_pen_xy'
    ]

    def __init__(self, pos=(0, 0)):
        super(Turtle, self).__init__(pos)
        self._jobs = _deque()

    def set_pos(self, x_or_pos, y=None):
        '''Move o cursor para a posição fornecida'''

        pos = _mathtools.util.args_to_vec2(x_or_pos, y)
        self.pos = pos

    def set_angle(self, value):
        '''Define a orientação do cursor (em graus)'''

        self.angle = value

    def set_theta(self, value):
        '''Define a orientação do cursor (em radianos)'''

        self.theta = value

    def center(self, penup=True):
        '''Move o cursor para o centro'''

        if penup:
            self.up()
        self.pos = FGAme.pos.middle

    #
    # Suporte à animação
    #
    def _add_job(self, func, *args, **kwds):
        with _PEN_LOCK:
            self._jobs.append([(func, args, kwds)])

    def _add_job_first(self, func, *args, **kwds):
        with _PEN_LOCK:
            self._jobs.insert(0, [(func, args, kwds)])

    def _add_job_first_mapping(self, func, seq):
        with _PEN_LOCK:
            L = [[(func, (x,), {})] for x in seq]
            self._jobs.extendleft(L)

    def _add_task(self, func, *args, **kwds):
        with _PEN_LOCK:
            if not self._jobs:
                self._jobs.append([])
            self._jobs[-1].append((func, args, kwds))

    def job_wrap(self, method):
        @_functools.wraps(method)
        def decorated(*args, **kwds):
            self._add_job(method, *args, **kwds)
        return decorated

    def step(self):
        '''Avança uma tarefa de execução'''

        with _PEN_LOCK:
            if self._jobs:
                print(len(self._jobs))
                job = self._jobs.popleft()
                for task in job:
                    task[0](*task[1], **task[2])

    def move_tip(self, pos):
        '''Move a ponta para a nova posição pos'''

        self._pos = self._current[-1] = Vec2(*pos)

    def make_move_job(self, method):
        @_functools.wraps(method)
        def decorated(*args, **kwds):
            pos = self.pos
            method(*args, **kwds)
            final = self.pos
            self._current[-1] = pos
            interpolated = self.interpolate(pos, final, 1)
            self._add_job_first_mapping(self.move_tip, interpolated)
        return decorated

    def interpolate(self, start, end, steps):
        '''Retorna a lista de interpolação que vai de start até end no número
        dado de passos (steps). O ponto inicial não é incluido'''

        delta = (end - start) / float(steps)
        out = [start + (n + 1) * delta for n in range(steps)]
        out[-1] = end  # diminui acúmulo de erros
        return out

    #
    # Renderização
    #
    def current(self):
        '''Retorna um objeto Path com o caminho atual'''

        if self._pen_down and len(self._current) >= 2:
            return draw.Path(self._current, **self._curve_kwds())

    def tip(self):
        '''Retorna um triângulo apontando para a direção da tartaruga'''

        L = 12
        vertices = [(L, 0), (0, L / 3), (0, -L / 3)]
        tip = draw.Poly(vertices, color=Color('red'))
        tip.rotate(self.theta)
        tip.move(self.pos)
        return tip

    def draw(self, canvas):
        super(Turtle, self).draw(canvas)
        path = self.current()
        if path is not None:
            path.draw(canvas)
        self.tip().draw(canvas)

    #
    # Inicialização do módulo
    #
    @classmethod
    def _populate_ns(cls, ns):
        '''Populate the given namespace with turtle functions and a Turtle()
        instance named _TURTLE.'''

        turtle = ns['_TURTLE'] = cls(FGAme.pos.middle)
        for name in dir(turtle):
            method = getattr(turtle, name)

            # Não adiciona implementações manuais de add_job
            if name.endswith('_job'):
                continue
            if name.startswith('_') or not callable(method):
                continue

            # Embrulha de forma padronizada ou adiciona implementação manual
            if name not in cls._blacklist:
                method = getattr(turtle, name + '_job', method)
                ns.setdefault(name, turtle.job_wrap(method))


def start():
    '''Inicia a janela do FGAme turtle ao fundo e espera por eventos'''

    global _RUNNING, _FGAME_THREAD

    if not _RUNNING:
        world = _World()
        world.add(_TURTLE)

        @world.listen('frame-enter')
        def step():
            _TURTLE.step()

        # Roda FGAme num thread secundário
        _FGAME_THREAD = _threading.Thread(target=world.run)
        _FGAME_THREAD.start()
        _RUNNING = True


def run(shell='ipython'):
    '''Inicia o turtle e executa um terminal interativo para interagir com a
    aplicação'''

    start()

    if shell == 'ipython':
        import IPython
        IPython.embed()
    elif shell == 'bpython':
        import bpython
        print('embeding bpython shell')
        bpython.embed()
    else:
        raise ValueError('invalid shell: %s' % shell)


#
# Adiciona métodos do objeto Turtle ao namespace do módulo
#
# TODO: fazer isto manualmente para cada classe de métodos?
Turtle._populate_ns(globals())


#
# Anima funções de movimento linear do cursor
#
def _animate_move_factory(method):
    '''Embrulha funções que implicam em movimento da tartaruga para que o mesmo
    seja animado ao longo de vários frames'''

    turtle = _TURTLE
    move_method = getattr(turtle, method)

    @_functools.wraps(move_method)
    def animated(*args, **kwds):
        start()

        def job():
            pos = turtle.pos
            move_method(*args, **kwds)
            final = turtle.pos
            turtle._current[-1] = pos
            turtle._pos = pos
            steps = turtle.interpolate(pos, final, 10)
            jobs = [[(turtle.move_tip, (x,), {})] for x in steps]
            with _PEN_LOCK:
                turtle._jobs.extendleft(reversed(jobs))

        turtle._add_job(job)

    return animated

G = globals()
for name in ['fwd', 'forward', 'back', 'backwards', 'move', 'goto']:
    G[name] = _animate_move_factory(name)
del G, name


#
# Anima funções de movimento rotacional do cursor
#
def _animate_rotation_factory(method):
    '''Embrulha funções que implicam em movimento rotacional do cursor
    para que o mesmo seja animado ao longo de vários frames'''

    turtle = _TURTLE
    rotate_method = getattr(turtle, method)

    @_functools.wraps(rotate_method)
    def animated(*args, **kwds):
        start()

        def job():
            angle = turtle.angle
            rotate_method(*args, **kwds)
            final = turtle.angle
            steps = turtle.interpolate(angle, final, 10)
            jobs = [[(turtle.set_angle, (x,), {})] for x in steps]
            with _PEN_LOCK:
                turtle._jobs.extendleft(reversed(jobs))

        turtle._add_job(job)

    return animated

G = globals()
for name in ['left', 'right', 'set_angle', 'set_theta']:
    G[name] = _animate_rotation_factory(name)
del G, name


#
# Figuras geométricas adicionais
#
def star(num_sides=7, size=100):
    '''Desenha uma estrela de num_sides lados com o tamanho de cada lado igual
    à size'''

    for _ in range(12):
        fwd(200)  # @UndefinedVariable
        left(7 * 360 / 12)  # @UndefinedVariable

if __name__ == '__main__':
    import IPython
    start()
    star()
    # run()
    print('starting debugging')
    #IPython.embed(header='FGAme Turtle')
