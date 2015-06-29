# -*- coding: utf8 -*-
# TODO: manter este modelo de renderização?
import copy
from FGAme.draw import Color
from FGAme import mathutils as shapes
from FGAme.core import PyGameTextureManager

black = Color('black')
white = Color('white')


class Drawable(object):

    '''Classe mãe para todos os objetos que podem ser desenhados na tela'''

    __slots__ = []

    # Funções que modificam o objeto selecionado *inplace* ####################
    def irotate(self, theta, axis=None):
        '''Rotaciona o objeto pelo ângulo dado. É possível fornecer um eixo
        opcional para realizar a rotação. Caso contrário, realiza a rotação
        em torno do centro.'''

        raise NotImplementedError

    def move(self, delta):
        '''Desloca o objeto pelas coordenadas (delta_x, delta_y) fornecidas'''

        raise NotImplementedError

    def rescale(self, scale):
        '''Multiplica as dimensões do objeto por um fator de escala'''

        raise NotImplementedError

    def transform(self, M):
        '''Realiza uma transformação linear por uma matriz M'''

        raise NotImplementedError

    # Retorna versões transformadas dos objetos ###############################
    def copy(self):
        '''Retorna uma cópia do objeto'''

        return copy.copy(self)

    def rescaled(self, value):
        '''Retorna uma versão modificada por um fator de escala igual a
        `value`'''

        new = self.copy()
        new.scale(value)
        return new

    def rotate(self, theta, axis=None):
        '''Retorna uma cópia do objeto rotacionada pelo ângulo fornecido em
        torno do eixo fornecido (ou o centro do objeto)'''

        new = self.copy()
        new.irotate(theta, axis)
        return new

    def moved(self, delta):
        '''Retorna uma cópia do objeto deslocada por um fator
        (delta_x, delta_y)'''

        new = self.copy()
        new.move(delta)
        return new

    def transformed(self, M):
        '''Retorna uma cópia do objeto transformada por uma matriz M'''

        new = self.copy()
        new.transform(M)
        return new

    def update(self, dt):
        '''Update its state after elapsing a time dt'''

    @property
    def visualization(self):
        return self

###############################################################################
#                            Objetos primitivos
###############################################################################


def delegate_property(name):
    '''Propriedade que simplesmente extrai o valor do atributo .geometric'''
    @property
    def getter(self):
        return getattr(self.geometric, name)

    return getter


class ShapeBase(Drawable):

    '''Classe pai para todos os objetos de geometria simples.'''

    __slots__ = ['geometric', 'color', 'line_color', 'line_width', 'sync']
    canvas_primitive = None

    def __init__(self, geometric,
                 color='black', line_color='black', line_width=0.0):

        self.geometric = geometric
        self.color = Color(color)
        self.line_color = Color(line_color)
        self.line_width = line_width

    @classmethod
    def from_primitive(cls, obj,
                       color='black', line_color='black', line_width=0.0):

        if isinstance(obj, shapes.AbstractCircle):
            obj_cls = Circle
        elif isinstance(obj, shapes.AbstractPoly):
            obj_cls = Poly
        elif isinstance(obj, shapes.AbstractAABB):
            obj_cls = AABB
        else:
            tname = type(obj).__name__
            raise ValueError('unsupported primitive: %s' % tname)

        new = Shape.__new__(obj_cls, obj, color, line_color, line_width)
        Shape.__init__(new, obj, color, line_color, line_width)
        return new

    def get_vertices(self, tol=2):
        '''Retorna uma lista de vértices que aproxima o objeto.

        Em caso de figuras poligonais, tol é ignorado e a lista de vértices
        corresponde aos vértices do objeto original. Em figuras não poligonais,
        tol corresponde a uma margem de tolerância (estimada) de quantos pixels
        as linhas do polígono podem se afastar do objeto original.'''

        raise NotImplementedError

    def __getattr__(self, attr):
        return getattr(self.geometric, attr)

    def draw(self, canvas):
        '''Desenha o objeto no objeto canvas fornecido'''

        getattr(canvas, 'draw_' + self.canvas_primitive)(self)


class Poly(ShapeBase):

    '''Objetos da classe Poly representam polígonos especificados por uma lista
    de vértices.'''

    __slots__ = []
    shape = delegate_property('vertices')
    canvas_primitive = 'poly'

    def __init__(self, vertices, **kwds):
        obj = shapes.Poly(vertices)
        super(Poly, self).__init__(obj, **kwds)

    def get_vertices(self, tol=1e-6):
        return self.geometric.vertices

    def draw(self, canvas):
        canvas.draw_poly(self)


class Rectangle(Poly):
    __slots__ = []

    def __init__(self, bbox=None, rect=None, shape=None, pos=None,
                 xmin=None, ymin=None, xmax=None, ymax=None, **kwds):

        obj = m.Rectangle(bbox=bbox, rect=rect, shape=shape, pos=pos,
                          xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
        super(Poly, self).__init__(**kwds)


###############################################################################
# TODO: refatorar para shapes herdarem dos primitivos geométricos extendidos
# com a classe shape
###############################################################################
class Curve(Drawable):

    '''Classe pai para todos os objetos geométricos que definem uma curva
    aberta.
     '''

    def __init__(self, width=1.0, color=black):
        self._color = Color(color)
        self.width = width

    def _init_colors_from_kwds(self, kwds):
        '''Extrai as keywords do dicionário kwds, e inicializa as propriedades
        de cores do objeto. As outras entradas do dicionário podem ser
        passadas para o construtor do objeto geométrico'''

        width = kwds.pop('solid', 1.0)
        color = kwds.pop('solid', black)
        Curve.__init__(self, width, color)

    def draw(self, canvas):
        '''Desenha o objeto no objeto canvas fornecido'''

        raise NotImplementedError('must be implemented in subclasses')

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = Color(value)

    @property
    def line_color(self):
        return self._color

    @line_color.setter
    def line_color(self, value):
        self._color = Color(value)


class Segment(Curve):

    '''Um segmento de reta que vai do ponto pt1 até pt2'''

    def __init__(self, pt1, pt2, **kwds):
        pass


# Objetos sólidos (figuras fechadas) ##########################################
class Shape(Drawable):

    '''Classe pai para todas as figuras fechadas. Define as propriedades
    solid, color, line_width e line_color.'''

    def __init__(self, solid=True, color=black,
                 line_width=0.0, line_color=black):

        self._color = Color(color)
        self._line_color = Color(line_color)
        self.line_width = line_width
        self.solid = bool(solid)

    def _init_colors_from_kwds(self, kwds):
        '''Extrai as keywords do dicionário kwds, e inicializa as propriedades
        de cores do objeto. As outras entradas do dicionário podem ser
        passadas para o construtor do objeto geométrico'''

        solid = kwds.pop('solid', True)
        color = kwds.pop('solid', black)
        line_color = kwds.pop('solid', black)
        line_width = kwds.pop('solid', 0.0)
        Shape.__init__(self, solid, color, line_width, line_color)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = Color(value)

    @property
    def line_color(self):
        return self._line_color

    @line_color.setter
    def line_color(self, value):
        self._line_color = Color(value)


class Circle(shapes.Circle, Shape):

    '''Um círculo de raio `radius` e centro em `pos`.'''

    def __init__(self, radius, pos=(0, 0), **kwds):

        shapes.Circle.__init__(self, radius, pos)
        Shape.__init__(self, **kwds)

    def draw(self, canvas):
        canvas.draw_circle(self)


class AABB(shapes.mAABB, Shape):

    '''Um círculo de raio `radius` e centro em `pos`.'''

    def __init__(self, *args, **kwds):
        self._init_colors_from_kwds(kwds)
        shapes.AABB.__init__(self, *args, **kwds)

    def draw(self, canvas):
        canvas.draw_circle(self)


class Image(AABB):

    '''Define uma imagem/pixmap não-animado'''

    manager = PyGameTextureManager()
    canvas_primitive = 'image'

    def __init__(self, path, pos=(0, 0), reference='center'):
        #self._data = self.manager.get_image(name)
        #shape = self.manager.get_shape(self._data)
        #super(Image, self).__init__(pos=pos, shape=shape)
        pass

    def draw(self, canvas):
        self.draw_image(self)


class Sprite(Image):

    '''Define uma image animada. O controle de frames é feito a cada chamada
    do método draw(). Desta forma, caso o método seja chamado duas vezes por
    frame, a velocidade de animação será o dobro da desejada.'''
