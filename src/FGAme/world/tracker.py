from FGAme import conf


class Tracker:
    def __init__(self, world):
        self._world = world

    def energy(self, auto_connect=True, ratio=True, raise_on_change=None):
        """
        Return a function that tracks total energy and prints any changes.
        """

        last_data = [None]
        if raise_on_change is None:
            raise_on_change = conf.DEBUG

        if ratio:
            def energy_tracker():
                last = last_data[0]
                total = self._world._simulation.energy_ratio()
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

        #if auto_connect:
        #    self._world.listen('frame-enter', energy_tracker)

        return energy_tracker
