# -*- coding: utf8 -*-

from FGAme.objects import AABB, Rectangle
from FGAme.physics import Simulation
from FGAme.core import EventDispatcher, signal, conf
from FGAme.draw import RenderTree, color_property
from FGAme.util import delegate_to
from FGAme.physics import Dynamic


class World(EventDispatcher):

    '''Classe Mundo: coordena todos os objetos com uma física definida e
    resolve a interação entre eles.
    '''

    def __init__(self, background=None,
                 gravity=None, damping=0, adamping=0,
                 restitution=1, sfriction=0, dfriction=0,
                 bounds=None, max_speed=None,
                 simulation=None):

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
                sfriction=sfriction,
                dfriction=dfriction,
                max_speed=max_speed,
                bounds=bounds)

        self.is_paused = False
        super(World, self).__init__()

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
        '''

        # Verifica se trata-se de uma lista de objetos
        if isinstance(obj, (tuple, list)):
            for obj in obj:
                self.add(obj, layer=layer)
            return

        # Adiciona na lista de renderização
        self._render_tree.add(obj, layer)
        if isinstance(obj, Dynamic):
            self._simulation.add(obj)

    def remove(self, obj):
        '''Descarta um objeto do mundo'''

        if getattr(obj, 'is_drawable', False):
            drawable = obj.visualization
            self._render_tree.remove(obj)
            self._simulation.remove(obj)
        else:
            self._render_tree.remove(obj)

    # Controle de eventos #####################################################
    # Delegações
    long_press = signal('long-press', 'key', delegate_to='_input')
    key_up = signal('key-up', 'key', delegate_to='_input')
    key_down = signal('key-down', 'key', delegate_to='_input')
    mouse_motion = signal('mouse-motion', delegate_to='_input')
    mouse_click = signal('mouse-click', 'button', delegate_to='_input')

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
        if self.is_paused:
            return
        self._simulation.update(dt)
        return self._simulation.time

    # Laço principal ##########################################################
    def run(self, timeout=None, real_time=True, **kwds):
        '''Roda a simulação de física durante o tempo 'timeout' especificado.

        O parâmetro `real_time` especifica se o tempo considerado consiste no
        tempo real ou no tempo de simulação.'''

        conf.get_mainloop().run(self, timeout=timeout, **kwds)

    def stop(self):
        '''Finaliza o laço principal de simulação'''

        conf.get_mainloop().stop()

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
        hard = kwds.get('hard', True)
        delta = kwds.get('delta', 10000)
        use_poly = kwds.get('use_poly', False)
        color = kwds.get('color', 'black')

        if len(args) == 4:
            xmin, xmax, ymin, ymax = args
        elif len(args) == 1:
            xmin, xmax, ymin, ymax = args[0]
        elif not args:
            if 'width' not in kwds:
                raise TypeError('not enougth parameters to set boundaries')

            W, H = conf.get_window_shape()
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
        up = maker(bbox=(xmin - delta, xmax + delta, ymax, ymax + delta))
        down = maker(bbox=(xmin - delta, xmax + delta, ymin - delta, ymin))
        left = maker(bbox=(xmin - delta, xmin, ymin, ymax))
        right = maker(bbox=(xmax, xmax + delta, ymin, ymax))
        for box in [up, down, left, right]:
            box.make_static()
        self.add(down)
        self.add(up)
        self.add(left)
        self.add(right)
        self._bounds = (left, right, up, down)
        self._hard_bounds = hard

    ###########################################################################
    #                         Funções úteis
    ###########################################################################
    def register_energy_tracker(self, auto_connect=True, ratio=True):
        '''Retorna uma função que rastreia a energia total do mundo a cada
        frame e imprime sempre que houver mudança na energia total.

        O comportamento padrão é imprimir a razão entre a energia inicial e a
        atual. Caso ``ratio=False`` imprime o valor da energia em notação
        científica.

        A função resultante é conectada automaticamente ao evento
        "frame-enter", a não ser que ``auto_conect=False``.
        '''

        E0 = []
        last = [None]

        if ratio:
            def energy_tracker():
                total = self._simulation.energy_ratio()
                if (last[0] is None) or (abs(total - last[0]) > 1e-6):
                    last[0] = total
                    print('Energia total / energia inicial:', total)

        else:
            def energy_tracker():
                raise NotImplementedError

        if auto_connect:
            self.listen('frame-enter', energy_tracker)

        return energy_tracker


if __name__ == '__main__':
    import doctest
    doctest.testmod()
