from FGAme.util import lazy
from FGAme.mathutils import Vector

__all__ = ['pos', 'vel']


def _factory_pos_property(pos):
    a, b = pos

    def pos_prop(self):
        w, h = self._shape
        x0, y0 = self._origin
        return Vector(x0 + a * w, y0 + b * h)

    pos_prop.terms = (a, b)

    return property(pos_prop)


def _factory_from_func(prop):
    a, b = prop.fget.terms

    def from_pos(self, x, y):
        w, h = self._shape
        x0, y0 = self._origin
        return Vector(x0 + a * w + x, y0 + b * h + y)

    return from_pos


class GlobalObject(object):

    @lazy
    def _globals(self):
        from FGAme.core import env
        if not env.has_init:
            from FGAme.core import init_canvas
            init_canvas()
        self._globals = env
        return self._globals

    @property
    def _shape(self):
        return self._globals.screen_shape

    @property
    def _origin(self):
        return self._globals.screen_origin


class PosObject(GlobalObject):

    '''
    Implementa o objeto "pos", que permite acessar facilmente algumas posições
    na tela.

    Exemplos
    --------

    O objeto pos conhece as coordenadas de vários pontos de interesse na tela

    >>> pos.middle, pos.nw, pos.ne, pos.sw, pos.se
    (Vector(400, 300), Vector(0, 600), Vector(800, 600), Vector(0, 0), Vector(800, 0))

    >>> pos.north, pos.south, pos.east, pos.west
    (Vector(400, 600), Vector(400, 0), Vector(800, 300), Vector(0, 300))

    Também podemos especificar coordenadas relativas a partir de qualquer um
    destes pontos

    >>> pos.from_middle(100, 100), pos.from_ne(0, -100)
    (Vector(500, 400), Vector(800, 500))
    '''

    middle, north, south, east, west = \
        map(_factory_pos_property,
            [(.5, .5), (.5, 1), (.5, 0), (1, .5), (0, .5)])

    from_middle, from_north, from_south, from_east, from_west = \
        map(_factory_from_func, [middle, north, south, east, west])

    sw, se, ne, nw = map(
        _factory_pos_property, [
            (0, 0), (1, 0), (1, 1), (0, 1)])
    south_west, sout_east, north_east, nort_west = sw, se, ne, nw

    from_sw, from_se, from_ne, from_nw = map(
        _factory_from_func, [
            sw, se, ne, nw])
    from_south_west, from_south_east, from_north_east, from_north_west = \
        from_sw, from_se, from_ne, from_nw


class VelObject(GlobalObject):

    @property
    def fast(self):
        return self._globals.speed_fast

    @property
    def slow(self):
        return self._globals.speed_slow

    @property
    def fair(self):
        return self._globals.speed_fair

    def _random(self, scale, angle):
        pass

    def random(self, angle=None):
        return self._random(self.fair, angle)

    def random_fast(self, angle=None):
        return self._random(self.slow, angle)

    def random_slow(self, angle=None):
        return self._random(self.slow, angle)

# Inicializa objetos
vel = VelObject()
pos = PosObject()

if __name__ == '__main__':
    import doctest
    doctest.testmod()
