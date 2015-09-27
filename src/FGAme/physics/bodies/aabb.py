# -*- coding: utf8 -*-

from . import LinearRigidBody
from FGAme.mathtools import sqrt, shapes

__all__ = ['AABB']


class AABB(LinearRigidBody):

    '''Define um objeto físico que responde a colisões como uma caixa de
    contorno alinhada aos eixos.

    Deve ser inicializada ou por uma tupla com os valores (xmin, xmax, ymin,
    ymax) ou por definido shape=(lado x, lado y).


    Example
    -------

    Os objetos tipo AABB podem ser iniciados de 4 maneiras diferentes.
    A primeira é fornecendo um formato e opcionalmente a posição do centro::

        >>> A = AABB(shape=(100, 200))
        >>> A.bbox  # (xmin, xmax, ymin, ymax)
        (-50.0, 50.0, -100.0, 100.0)

    A segunda opção é indicar o uma tupla com a posição do vértice inferior
    esquerdo e a forma::

        >>> B = AABB(rect=(0, 0, 100, 200))
        >>> B.bbox
        (0.0, 100.0, 0.0, 200.0)

    A outra maneira é fornecer a caixa de contorno como uma lista::

        >>> C = AABB(bbox=(0, 100, 0, 200))

    E, finalmente, podemos fornecer os valores de xmin, xmax, ymin, ymax
    individualmente::

        >>> D = AABB(0, 100, 0, 200)
        >>> E = AABB(xmin=0, xmax=100, ymin=0, ymax=200)

    Em todos os casos, a massa já é calculada automaticamente a partir da área
    assumindo-se uma densidade de 1.0. O momento de inércia é infinito pois
    trata-se de um objeto sem dinâmica angular::

        >>> A.mass, A.inertia  # 20.000 == 200 x 100
        (20000.0, inf)

    '''

    __slots__ = []

    def __init__(self, xmin=None, xmax=None, ymin=None, ymax=None,
                 pos=None, vel=(0, 0), mass=None, density=None,
                 bbox=None, shape=None, rect=None, **kwds):

        # Define as propriedades das caixas de contorno
        xmin, xmax, ymin, ymax = shapes.aabb_bbox(bbox=bbox, rect=rect,
                                                  shape=shape, pos=pos,
                                                  xmin=xmin, xmax=xmax,
                                                  ymin=ymin, ymax=ymax)

        pos = ((xmin + xmax) / 2., (ymin + ymax) / 2.)
        self._delta_x = dx = (xmax - xmin) / 2
        self._delta_y = dy = (ymax - ymin) / 2
        self.cbb_radius = sqrt(dx ** 2 + dy ** 2)
        aabb = shapes.AABB(-dx, dx, -dy, dy)
        super(AABB, self).__init__(pos, vel, mass=mass, density=density,
                                   baseshape=aabb, **kwds)

    def __repr__(self):
        tname = type(self).__name__
        if not self._invmass:
            tname += '*'
        vel = ', '.join('%.1f' % x for x in self._vel)
        data = ', '.join('%.1f' % x for x in self.bbox)
        return '%s(bbox=[%s], vel=(%s))' % (tname, data, vel)

    # Torna as os limites da AABB mutáveis ####################################
    @property
    def aabb(self):
        return self.bounding_box

    @property
    def xmin(self):
        return self._pos.x - self._delta_x

    @xmin.setter
    def xmin(self, value):
        xmin = float(value)
        xmax = self.xmax
        self._pos = self._pos.setx((xmax + xmin) / 2)
        self._delta_x = (xmax - xmin) / 2

    @property
    def xmax(self):
        return self._pos.x + self._delta_x

    @xmax.setter
    def xmax(self, value):
        xmin = self.xmin
        xmax = float(value)
        self._pos = self._pos.setx((xmax + xmin) / 2)
        self._delta_x = (xmax - xmin) / 2

    @property
    def ymin(self):
        return self._pos.y - self._delta_y

    @ymin.setter
    def ymin(self, value):
        ymin = float(value)
        ymax = self.ymax
        self._pos = self._pos.sety((ymax + ymin) / 2)
        self._delta_y = (ymax - ymin) / 2

    @property
    def ymax(self):
        return self._pos.y + self._delta_y

    @ymax.setter
    def ymax(self, value):
        ymin = self.ymin
        ymax = float(value)
        self.pos = self.pos.copy(y=(ymax + ymin) / 2)
        self._delta_y = (ymax - ymin) / 2

    # Propriedades geométricas ################################################
    def area(self):
        return 4 * self._delta_x * self._delta_y

    def ROG_sqr(self):
        a = self._delta_x
        b = self._delta_y
        return (a ** 2 + b ** 2) / 3


if __name__ == '__main__':
    import doctest
    doctest.testmod()
