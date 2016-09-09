import threading
import weakref

from FGAme import conf
from FGAme.draw import RenderTree, colorproperty
from FGAme.objects import Body
from FGAme.physics import Simulation
from FGAme.utils import delegate_to
from FGAme.utils import lazy
from FGAme.world.factory import ObjectFactory
from FGAme.world.tracker import Tracker


class World:
    """
    Combines physical simulation with display.
    """

    # Events
    # long_press = signal('long-press', 'key', delegate_to='_input')
    # key_up = signal('key-up', 'key', delegate_to='_input')
    # key_down = signal('key-down', 'key', delegate_to='_input')
    # mouse_motion = signal('mouse-motion', delegate_to='_input')
    # mouse_button_up = \
    #     signal('mouse-button-up', 'button', delegate_to='_input')
    # mouse_button_down = \
    #     signal('mouse-button-down', 'button', delegate_to='_input')
    # mouse_long_press = \
    #     signal('mouse-long-press', 'button', delegate_to='_input')
    # pre_draw = signal('pre-draw', num_args=1, delegate_to='_mainloop')
    # post_draw = signal('post-draw', num_args=1, delegate_to='_mainloop')
    # frame_enter = signal('frame-enter')
    # frame_skip = signal('frame-skip', num_args=1)
    # collision = signal('collision', num_args=1)

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

    def __contains__(self, obj):
        return obj in self._render_tree or obj in self._simulation

    def _add(self, obj, layer=0):
        """
        Add object to the world.
        """

        if isinstance(obj, (tuple, list)):
            for obj in obj:
                self.add(obj, layer=layer)
        elif hasattr(obj, 'update_world'):
            obj.update_world(self, layer=layer)
        else:
            self._render_tree.add(obj, layer)
            if isinstance(obj, Body):
                self._simulation.add(obj)
                obj.world = self

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
        Resume physics simulation.
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
        Run simulation until the given timeout expires.

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