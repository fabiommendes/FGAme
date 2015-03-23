from FGAme.mathutils import Vector

__all__ = ['AABB',
           'aabb_rect', 'aabb_bbox',
           'aabb_pshape', 'aabb_shape', 'aabb_center']


class AABB(object):

    '''Representa uma caixa alinhada aos eixos.

    Exemplos
    --------

    >>> C = Circle(50, (50, 0))
    '''

    __slots__ = ['xmin', 'xmax', 'ymin', 'ymax']

    def __init__(self,
                 bbox=None, rect=None, shape=None, pos=None,
                 xmin=None, xmax=None, ymin=None, ymax=None):

        self.xmin, self.xmax, self.ymin, self.ymax = map(
            float, aabb_bbox(bbox, rect, shape, pos, xmin, xmax, ymin, ymax)
        )

    @property
    def pos(self):
        '''Centro da AABB'''

        x = (self.xmin + self.xmax) / 2
        y = (self.ymin + self.ymax) / 2
        return Vector(x, y)

    @property
    def shape(self):
        '''Formato da AABB (width, height)'''

        width = self.xmax - self.xmin
        height = self.ymax - self.ymin
        return width, height

    @property
    def rect(self):

        return (self.xmin, self.ymin,
                self.xmax - self.xmin, self.ymax - self.ymin)

    @property
    def bbox(self):
        return (self.xmin, self.xmax, self.ymin, self.ymax)

    # Magic methods ###########################################################
    def __repr__(self):
        data = '%.1f, %.1f, %.1f, %.1f' % self.bbox()
        return 'AABB(bbox=[%.1f])' % data

    ###########################################################################
    #                           Cálculo de distâncias
    ###########################################################################

    def distance_center(self, other):
        '''Retorna a distância entre centros de duas AABBs.'''

    def distance_aabb(self, other):
        '''Retorna a distância para outra AABB. Zero se elas se interceptam'''

    ###########################################################################
    #                     Pontos de intersecção
    ###########################################################################

    def intercepts_aabb(self, other):
        '''Retorna True caso os dois objetos se interceptem'''

    def intercepts_point(self, point, tol=1e-6):
        '''Retorna True se o ponto está na linha que forma a AABB a menos de
        uma margem de tolerância tol.'''

    ###########################################################################
    #                         Contêm figuras
    ###########################################################################

    def contains_aabb(self, other):
        '''Retorna True se o segundo objeto está contido na AABB.'''

    def contains_point(self, point):
        '''Retorna True se o ponto está contido na AABB.'''

###############################################################################
# Extrai caixas de contorno a partir das entradas
###############################################################################


def aabb_bbox(bbox=None, rect=None,
              shape=None, pos=None,
              xmin=None, xmax=None,
              ymin=None, ymax=None):
    '''
    Retorna a caixa de contorno (xmin, xmax, ymin, ymax) a partir dos
    parâmetros fornecidos.
    '''

    if bbox is not None:
        xmin, xmax, ymin, ymax = map(float, bbox)
        if pos is not None:
            raise TypeError('cannot set bbox and pos simultaneously')
        x = (xmin + xmax) / 2.
        y = (ymin + ymax) / 2.
    elif shape is not None:
        pos = pos or (0, 0)
        dx, dy = map(float, shape)
        x, y = pos
        xmin, xmax = x - dx / 2., x + dx / 2.
        ymin, ymax = y - dy / 2., y + dy / 2.
    elif rect is not None:
        xmin, ymin, dx, dy = map(float, rect)
        xmax = xmin + dx
        ymax = ymin + dy
    elif None not in (xmin, xmax, ymin, ymax):
        pass
    else:
        raise TypeError('either shape, bbox or rect  must be defined')

    return (xmin, xmax, ymin, ymax)


def aabb_rect(bbox=None, rect=None,
              shape=None, pos=None,
              xmin=None, xmax=None,
              ymin=None, ymax=None):
    '''
    Retorna o rect  (xmin, ymin, width, height) a partir dos parâmetros
    fornecidos.
    '''

    x, y, xmax, ymax = aabb_bbox(bbox, rect, shape, pos,
                                 xmin, xmax, ymin, ymax)
    return (x, y, xmax - x, ymax - y)


def aabb_pshape(bbox=None, rect=None,
                shape=None, pos=None,
                xmin=None, xmax=None,
                ymin=None, ymax=None):
    '''
    Retorna uma tupla de (centro, shape) a partir dos parâmetros fornecidos.
    '''
    x, y, xmax, ymax = aabb_bbox(bbox, rect, shape, pos,
                                 xmin, xmax, ymin, ymax)
    center = Vector((x + xmax) / 2.0, (y + ymax) / 2.0)
    shape = (xmax - x, ymax - y)
    return center, shape


def aabb_center(bbox=None, rect=None,
                shape=None, pos=None,
                xmin=None, xmax=None,
                ymin=None, ymax=None):
    '''
    Retorna um vetor com a posição do centro da caixa de contorno.
    '''

    return aabb_pshape(bbox, rect, shape, pos, xmin, ymin, xmax, ymax)[0]


def aabb_shape(bbox=None, rect=None,
               shape=None, pos=None,
               xmin=None, xmax=None,
               ymin=None, ymax=None):
    '''
    Retorna uma tupla (width, height) com o formato da caixa de contorno.
    '''

    return aabb_shape(bbox, rect, shape, pos, xmin, ymin, xmax, ymax)[1]

if __name__ == '__main__':
    import doctest
    doctest.testmod()
