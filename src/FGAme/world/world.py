import threading
import weakref

import collections

from FGAme import conf
from FGAme.signals import Listener
from FGAme.draw import RenderTree, colorproperty
from FGAme.objects import Body
from FGAme.physics import Simulation
from FGAme.utils import delegate_to
from FGAme.utils import lazy
from FGAme.world.factory import ObjectFactory
from FGAme.world.tracker import Tracker


class World(Listener, collections.MutableSequence):
    """
    Combines physical simulation with display.
    """

    # Simulation properties
    background = colorproperty('background', 'white')
    gravity = delegate_to('_simulation')
    damping = delegate_to('_simulation')
    adamping = delegate_to('_simulation')
    time = delegate_to('_simulation', readonly=True)

    # Special properties
    @lazy
    def add(self):
        return ObjectFactory(self)

    @lazy
    def track(self):
        return Tracker(self)

    @lazy
    def _mainloop(self):
        return conf.get_mainloop()

    @lazy
    def _input(self):
        return conf.get_input()

    _last_instances = []

    def __init__(self, background=None,
                 gravity=None, damping=0, adamping=0,
                 restitution=1, friction=0,
                 bounds=None, max_speed=None,
                 simulation=None):

        self.background = background
        self._render_tree = RenderTree()
        self._objects = []

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

        # Populate world with user-customizable init
        self.init()

        # Saves instance
        self._last_instances.append(weakref.ref(self))

        # Connect signals
        self.autoconnect()

    def __len__(self):
        return len(self._objects)

    def __iter__(self):
        return iter(self._objects)

    def __getitem__(self, i):
        return self._objects[i]

    def __delitem__(self, i):
        self.remove(self._objects[i])

    def __setitem__(self, key, value):
        raise IndexError('cannot replace objects in world')

    def _add(self, obj, layer=0):
        """
        Adds object to the world.
        """

        if isinstance(obj, (tuple, list)):
            for obj in obj:
                self.add(obj, layer=layer)
        else:
            self._render_tree.add(obj, layer)
            if isinstance(obj, Body):
                self._simulation.add(obj)
                obj.world = self
            self._objects.append(obj)

    def insert(self, idx, obj):
        raise IndexError('cannot insert objects at specific positions. '
                         'Please user world.add()')

    def append(self, obj, layer=0):
        """
        Alias to World.add()
        """

        self.add(obj, layer)

    def remove(self, obj):
        """
        Remove object from the world.
        """

        if getattr(obj, 'world', None) is self:
            if obj in self._render_tree:
                self._render_tree.remove(obj)
            self._simulation.remove(obj)
            obj.world = None
        else:
            self._render_tree.remove(obj)
        self._objects.remove(obj)

    def init(self):
        """
        Executed after initialization.

        Should be overridden by sub-classes in order to populate the world with
        default objects during its creation. The default implementation does
        nothing.
        """

    def pause(self):
        """
        Pause physics simulation.
        """

        self.is_paused = True

    def resume(self):
        """
        Resume paused physics simulation.
        """

        self.is_paused = False

    def toggle_pause(self):
        """
        Toggles paused state.
        """

        self.is_paused = not self.is_paused

    def update(self, dt):
        """
        Main update routine.
        """

        if not self.is_paused:
            self._simulation.update(dt)

    def run(self, timeout=None, **kwds):
        """
        Runs simulation until the given timeout expires.

        Args:
            timeout (float):
                Maximum duration of simulation (in seconds). Leave None to
                run the simulation indefinitely.
        """

        conf.init()
        conf.show_screen()
        self._mainloop.run(self, timeout=timeout, **kwds)

    def start(self, **kwds):
        """
        Non-blocking version of World.run().

        Starts simulation in a separate thread. This must be supported by the
        backend (pygame, for instance, does).
        """

        if hasattr(self, '_thread'):
            try:
                self._thread.join(0)
            except TimeoutError:
                pass

        self._thread = threading.Thread(target=self.run, kwargs=kwds)
        self._thread.start()

    def stop(self):
        """
        Stops simulation.
        """

        # Forces thread to stop
        try:
            self._thread.join(0)
            del self._thread
        except (AttributeError, TimeoutError):
            pass
        self._mainloop.stop()

    def render_tree(self):
        """
        Return the render tree.
        """

        return self._render_tree


def get_last_world_instance():
    """
    Return the lastly created instance of World()
    """

    L = World._last_instances
    while L:
        ref = L.pop()
        value = ref()
        if value is not None:
            return value

    raise ValueError('no World instance exists yet.')
