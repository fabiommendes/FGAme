#-*- coding: utf8 -*-
from __future__ import print_function

from FGAme.physics import AABB, Poly, Simulation
from FGAme.core import EventDispatcher, signal
from FGAme.core import conf
from FGAme.draw import RenderTree, color_property

#===============================================================================
# Classe Mundo -- coordena todos os objetos com uma física definida e resolve a
# interação entre eles
#===============================================================================
class World(EventDispatcher):
    '''Documente-me!
    '''

    def __init__(self, background=None,
                 gravity=None, damping=0, adamping=0,
                 rest_coeff=1, sfriction=0, dfriction=0, stop_velocity=1e-6,
                 simulation=None):
        
        self.background = background
        self._render_tree = RenderTree()
        
        if simulation:
            self.simulation = simulation
        else:
            self.simulation = Simulation(
                gravity=gravity, damping=damping, adamping=adamping,
                rest_coeff=rest_coeff, sfriction=sfriction, dfriction=dfriction,
                stop_velocity=stop_velocity)

        # Controle de callbacks
        self.is_paused = False
        super(World, self).__init__()

    background = color_property('background', 'white')

    #===========================================================================
    # Propriedades do objeto Simulation
    #===========================================================================
    @property
    def gravity(self): 
        return self.simulation.gravity

    @gravity.setter
    def gravity(self, value):
        self.simulation.gravity = value

    @property
    def damping(self):
        return self.simulation.damping

    @damping.setter
    def damping(self, value):
        self.simulation.damping = value

    @property
    def adamping(self):
        return self.simulation.adamping

    @adamping.setter
    def adamping(self, value):
        self.simulation.adamping = value
        
    @property
    def time(self):
        return self.simulation.time

    #===========================================================================
    # Gerenciamento de objetos
    #===========================================================================
    def add(self, obj, layer=0):
        '''Adiciona um novo objeto ao mundo.
        
        Exemplos
        --------
        
        >>> obj = AABB((-10, 10, -10, 10))
        >>> world = World()
        >>> world.add(obj, layer=1)
        '''

        # Verifica se trata-se de uma lista de objetos
        if isinstance(obj, (tuple, list)):
            for obj in obj:
                self.add(obj, layer=layer)
            return

        # Adiciona na lista de renderização
        if getattr(obj, 'is_drawable', False):
            self._render_tree.add(obj, layer)
        else:
            drawable = obj.get_drawable()
            self._render_tree.add(drawable, layer)
            self.simulation.add(obj)

    def remove(self, obj):
        '''Descarta um objeto do mundo'''

        if getattr(obj, 'is_drawable', False):
            drawable = obj.get_drawable()
            self._render_tree.remove(obj)
            self.simulation.remove(obj)
        else:
            self._render_tree.remove(obj)
            
    #===========================================================================
    # Controle de eventos
    #===========================================================================
    # Delegações
    long_press = signal('long-press', 'key', delegate='simulation')
    key_up = signal('key-up', 'key', delegate='simulation')
    key_down = signal('key-down', 'key', delegate='simulation')
    mouse_motion = signal('mouse-motion', delegate='simulation')
    mouse_click = signal('mouse-click', 'button', delegate='simulation')
    
    # Eventos privados
    frame_enter = signal('frame-enter')
    frame_skip = signal('frame-skip', num_args=1)
    collision = signal('collision', num_args=1)
    #TODO: collision_pair = signal('collision-pair', 'obj1', 'obj2', num_args=1)

    #===========================================================================
    # Simulação de Física
    #===========================================================================
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
        self.simulation.update(dt)
        return self.simulation.time

    #===========================================================================
    # Laço principal
    #===========================================================================
    def run(self, timeout=None, real_time=True):
        '''Roda a simulação de física durante o tempo 'timeout' especificado.
        
        O parâmetro `real_time` especifica se o tempo considerado consiste no
        tempo real ou no tempo de simulação.'''
        
        conf._mainloop_object.run(self, timeout=timeout)

    def stop(self):
        '''Finaliza o laço principal de simulação'''
        
        conf._mainloop_object.stop()

    def set_next_state(self, value):
        '''Passa a simulação para o próximo estado'''
        
        pass
    
    def get_render_tree(self):
        return self._render_tree
    
    #===========================================================================
    # Criação de objetos especiais
    #===========================================================================
    def set_bounds(self, *args, **kwds):
        '''Cria contorno'''
        
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
        maker = Poly.rect if use_poly else AABB
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

if __name__ == '__main__':
    import doctest
    doctest.testmod()

