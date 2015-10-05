import random
from FGAme import conf
from FGAme.util import lazy
from FGAme.mathtools import Vec2, pi, ux2D

__all__ = ['pos', 'vel']


def _factory_pos_property(pos):
    '''Cria propriedades que retornam as posições absolutas no objeto `pos`'''
    a, b = pos

    def pos_prop(self):
        w, h = self._shape
        x0, y0 = self._origin
        return Vec2(x0 + a * w, y0 + b * h)

    pos_prop.terms = (a, b)

    return property(pos_prop)


def _factory_from_func(prop):
    '''Cria funções que retornam posições relativas no objeto `pos`'''

    a, b = prop.fget.terms

    def from_pos(self, x, y):
        w, h = self._shape
        x0, y0 = self._origin
        return Vec2(x0 + a * w + x, y0 + b * h + y)

    return from_pos


class GlobalObject(object):

    '''Base para PosObject e VelObject'''

    @lazy
    def _globals(self):
        conf.init()
        self._globals = conf
        return self._globals

    @property
    def _shape(self):
        return self._globals.get_resolution()

    @property
    def _origin(self):
        return Vec2(0, 0)


class PosObject(GlobalObject):

    '''
    Implementa o objeto "pos", que permite acessar facilmente algumas posições
    na tela.

    Exemplos
    --------

    O objeto pos conhece as coordenadas de vários pontos de interesse na tela

    >>> pos.middle, pos.nw, pos.ne, pos.sw, pos.se
    (Vec(400, 300), Vec(0, 600), Vec(800, 600), Vec(0, 0), Vec(800, 0))

    >>> pos.north, pos.south, pos.east, pos.west
    (Vec(400, 600), Vec(400, 0), Vec(800, 300), Vec(0, 300))

    Também podemos especificar coordenadas relativas a partir de qualquer um
    destes pontos

    >>> pos.from_middle(100, 100), pos.from_ne(0, -100)
    (Vec(500, 400), Vec(800, 500))
    '''

    # Alinhados
    middle, north, south, east, west = \
        map(_factory_pos_property,
            [(.5, .5), (.5, 1), (.5, 0), (1, .5), (0, .5)])

    # Alinhados relativos
    from_middle, from_north, from_south, from_east, from_west = \
        map(_factory_from_func, [middle, north, south, east, west])

    # Diagonais
    sw, se, ne, nw = \
        map(_factory_pos_property, [(0, 0), (1, 0), (1, 1), (0, 1)])

    # Diagnoais (verboso)
    south_west, sout_east, north_east, nort_west = sw, se, ne, nw

    # Relativos diagonais
    from_sw, from_se, from_ne, from_nw = \
        map(_factory_from_func, [sw, se, ne, nw])

    # Relativos diagonais (verboso)
    from_south_west, from_south_east, from_north_east, from_north_west = \
        from_sw, from_se, from_ne, from_nw


class VelObject(GlobalObject):

    '''Implementa o objeto `vel`, que permite definir facilmente algumas
    velocidades no mundo'''

    def set_speeds(self, slow, fair, fast):
        '''Define o padrão de referência para as velocidades lenta, média e
        rápida'''

        if slow <= fair <= fast:
            self.set_slow(slow)
            self.set_fair(fair)
            self.set_fast(fast)

    def set_fast(self, value):
        '''Define a velocidade referência considerada "rápida"'''

        self._globals.speed_fast = value

    def set_fair(self, value):
        '''Define a velocidade referência considerada "média"'''

        self._globals.speed_fair = value

    def set_slow(self, value):
        '''Define a velocidade referência considerada "lenta"'''

        self._globals.speed_slow = value

    @property
    def fast(self):
        return self._globals.speed_fast

    @property
    def slow(self):
        return self._globals.speed_slow

    @property
    def fair(self):
        return self._globals.speed_fair

    # TODO: definir atributos e métodos para as velocidades
    # Velocidades aleatórias ##################################################
    def _random(self, scale, angle):
        return scale * ux2D.rotated(random.uniform(0, 2 * pi))

    def random(self, angle=None):
        return self._random(self.fair, angle)

    def random_fast(self, angle=None):
        return self._random(self.slow, angle)

    def random_slow(self, angle=None):
        return self._random(self.slow, angle)

# Velocidades em direções específicas #########################################
_speeds = dict(
    up=Vec2(0, 1),
    down=Vec2(0, -1),
    right=Vec2(1, 0),
    left=Vec2(-1, 0),
    ne=Vec2(1, 1).normalized(),
    nw=Vec2(-1, 1).normalized(),
    se=Vec2(1, -1).normalized(),
    sw=Vec2(-1, -1).normalized(),
)


def speed_prop(name, scale, Vec):
    def prop(self):
        return getattr(self, scale) * Vec
    prop.__name__ = name
    return property(prop)

for name, Vec in _speeds.items():
    setattr(VelObject, name, speed_prop(name, 'fair', Vec))
    setattr(VelObject, name, speed_prop('%s_fast' % name, 'fast', Vec))
    setattr(VelObject, name, speed_prop('%s_slow' % name, 'slow', Vec))

# Inicializa objetos
vel = VelObject()
pos = PosObject()

if __name__ == '__main__':
    import doctest
    doctest.testmod()
