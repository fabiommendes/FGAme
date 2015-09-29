# -*- coding: utf8 -*-

from FGAme import conf
from FGAme.objects import AABB, Rectangle
from FGAme.physics import Simulation
from FGAme.events import EventDispatcher, signal
from FGAme.draw import RenderTree, color_property
from FGAme.util import delegate_to
from FGAme.physics import Body
from FGAme.util import lazy


class World(EventDispatcher):

    '''Classe Mundo: coordena todos os objetos com uma física definida e
    resolve a interação entre eles.
    '''

    def __init__(self, background=None,
                 gravity=None, damping=0, adamping=0,
                 restitution=1, friction=0,
                 bounds=None, max_speed=None,
                 simulation=None, force_init=True):

        if force_init:
            conf.init()
            conf.show_screen()
        self.background = background
        self._render_tree = RenderTree()
        self._input = conf.get_input()

        if simulation:
            self._simulation = simulation
        else:
            self._simulation = Simulation(
                gravity=gravity,
                damping=damping,
                adamping=adamping,
                restitution=restitution,
                friction=friction,
                max_speed=max_speed,
                bounds=bounds)

        self.is_paused = False
        super(World, self).__init__()

        # Inicia e popula o mundo
        self.init()

    background = color_property('background', 'white')

    # Propriedades do objeto Simulation #######################################
    gravity = delegate_to('_simulation.gravity')
    damping = delegate_to('_simulation.damping')
    adamping = delegate_to('_simulation.adamping')
    time = delegate_to('_simulation.time', read_only=True)

    # Gerenciamento de objetos ################################################
    def add(self, obj, layer=0):
        '''Adiciona um novo objeto ao mundo.

        Exemplos
        --------

        >>> obj = AABB(-10, 10, -10, 10)
        >>> world = World()
        >>> world.add(obj, layer=1)
        >>> obj in world
        True

        Os objetos podem ser removidos com o método remove()

        >>> world.remove(obj)
        '''

        # Verifica se trata-se de uma lista de objetos
        if isinstance(obj, (tuple, list)):
            for obj in obj:
                self.add(obj, layer=layer)
            return

        # Objetos que implementam update_world()
        elif hasattr(obj, 'update_world'):
            obj.update_world(self, layer=layer)
            return

        # Adiciona na lista de renderização
        self._render_tree.add(obj, layer)
        if isinstance(obj, Body):
            self._simulation.add(obj)

    def remove(self, obj):
        '''Descarta um objeto do mundo'''

        self._render_tree.remove(obj)
        if isinstance(obj, Body):
            self._simulation.remove(obj)

    def init(self):
        '''Método executado após a inicialização do objeto World(). Normalmente
        é sobrescrito pelas sub-classes para popular o mundo com objetos e
        realizar outras operações de inicialização. A implementação padrão não
        faz nada.'''

    def __contains__(self, obj):
        return obj in self._render_tree or obj in self._simulation

    # Controle de eventos #####################################################

    # Delegações para o Input
    long_press = signal('long-press', 'key', delegate_to='_input')
    key_up = signal('key-up', 'key', delegate_to='_input')
    key_down = signal('key-down', 'key', delegate_to='_input')
    mouse_motion = signal('mouse-motion', delegate_to='_input')
    mouse_button_up = \
        signal('mouse-button-up', 'button', delegate_to='_input')
    mouse_button_down = \
        signal('mouse-button-down', 'button', delegate_to='_input')
    mouse_long_press = \
        signal('mouse-long-press', 'button', delegate_to='_input')

    # Delegação para o mainloop
    pre_draw = signal('pre-draw', num_args=1, delegate_to='_mainloop')
    post_draw = signal('post-draw', num_args=1, delegate_to='_mainloop')

    # Eventos privados
    frame_enter = signal('frame-enter')
    frame_skip = signal('frame-skip', num_args=1)
    collision = signal('collision', num_args=1)
    # TODO: collision_pair = signal('collision-pair', 'obj1', 'obj2',
    # num_args=1)

    # Simulação de Física #####################################################
    def pause(self):
        '''Pausa a simulação de física'''

        self.is_paused = True

    def unpause(self):
        '''Resume a simulação de física'''

        self.is_paused = False

    def toggle_pause(self):
        '''Alterna o estado de pausa da simulação'''

        self.is_paused = not self.is_paused

    def update(self, dt):
        '''Rotina principal da simulação de física.'''

        self.trigger('frame-enter')
        if not self.is_paused:
            self._simulation.update(dt)

    # Laço principal ##########################################################
    @lazy
    def _mainloop(self):
        return conf.get_mainloop()

    def run(self, timeout=None, real_time=True, **kwds):
        '''Roda a simulação de física durante o tempo 'timeout' especificado.

        O parâmetro `real_time` especifica se o tempo considerado consiste no
        tempo real ou no tempo de simulação.'''

        self._mainloop.run(self, timeout=timeout, **kwds)

    def stop(self):
        '''Finaliza o laço principal de simulação'''

        self._mainloop.stop()

    def set_next_state(self, value):
        '''Passa a simulação para o próximo estado'''

        pass

    def get_render_tree(self):
        return self._render_tree

    ###########################################################################
    #                     Criação de objetos especiais
    ###########################################################################
    def add_bounds(self, *args, **kwds):
        '''Cria um conjunto de AABB's que representa uma região fechada.

        Parameters
        ----------

        '''

        # Processa argumentos
        hard = kwds.pop('hard', True)
        delta = kwds.pop('delta', 10000)
        use_poly = kwds.pop('use_poly', False)

        if len(args) == 4:
            xmin, xmax, ymin, ymax = args
        elif len(args) == 1:
            xmin, xmax, ymin, ymax = args[0]
        elif not args:
            if 'width' not in kwds:
                raise TypeError('not enougth parameters to set boundaries')

            W, H = conf.get_resolution()
            value = kwds.pop('width')
            try:
                N = len(value)
                if N == 2:
                    dx, dy = value
                    xmin, xmax = dx, W - dx
                    ymin, ymax = dy, H - dy
                elif N == 4:
                    dx, dy, dx1, dy1 = value
                    xmin, xmax = dx, W - dx1
                    ymin, ymax = dy, H - dy1
                else:
                    raise ValueError('width can have 1, 2 or 4 values')
            except TypeError:
                dx = dy = value
                xmin, xmax = dx, W - dx
                ymin, ymax = dy, H - dy
        else:
            raise TypeError('invalid number of positional arguments')

        assert xmin < xmax and ymin < ymax, 'invalid bounds'
        maker = Rectangle if use_poly else AABB

        up = maker(
            bbox=(xmin - delta, xmax + delta, ymax, ymax + delta), **kwds)
        down = maker(
            bbox=(xmin - delta, xmax + delta, ymin - delta, ymin), **kwds)
        left = maker(
            bbox=(xmin - delta, xmin, ymin, ymax), **kwds)
        right = maker(
            bbox=(xmax, xmax + delta, ymin, ymax), **kwds)

        for box in [up, down, left, right]:
            box.make_static()
            assert box._invmass == 0.0
        self.add([up, down, left, right])
        self._bounds = (left, right, up, down)
        self._hard_bounds = hard

    ###########################################################################
    #                         Funções úteis
    ###########################################################################
    def register_energy_tracker(self, auto_connect=True, ratio=True,
                                raise_on_change=None):
        '''Retorna uma função que rastreia a energia total do mundo a cada
        frame e imprime sempre que houver mudança na energia total.

        O comportamento padrão é imprimir a razão entre a energia inicial e a
        atual. Caso ``ratio=False`` imprime o valor da energia em notação
        científica.

        A função resultante é conectada automaticamente ao evento
        "frame-enter", a não ser que ``auto_conect=False``.
        '''

        last_data = [None]
        if raise_on_change is None:
            raise_on_change = conf.DEBUG

        if ratio:
            def energy_tracker():
                last = last_data[0]
                total = self._simulation.energy_ratio()
                if (last is None) or (abs(total - last) > 1e-6):
                    msg = 'Energia total / energia inicial: %s' % total

                    if (last is not None) and raise_on_change:
                        raise ValueError(msg)
                    else:
                        if not conf.DEBUG:
                            print(msg)
                    last_data[0] = total
        else:
            def energy_tracker():
                raise NotImplementedError

        if auto_connect:
            self.listen('frame-enter', energy_tracker)

        return energy_tracker


if __name__ == '__main__':
    import doctest
    doctest.testmod()
