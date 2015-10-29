# TODO: manter este modelo de renderização?
import copy
from FGAme.draw import Color
from FGAme.mathtools import shapes

black = Color('black')
white = Color('white')


class Drawable(object):

    '''Classe mãe para todos os objetos que podem ser desenhados na tela'''

    __slots__ = ()

    visible = True
    has_physics = False

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def copy(self):
        '''Retorna uma cópia do objeto'''

        return copy.copy(self)

    def draw(self, canvas):
        '''Desenha objeto na tela'''

        try:
            func = getattr(canvas, self._canvas_shape_name)
        except AttributeError:
            name = 'draw_' + type(self).__name__.lower()
            type(self)._canvas_shape_name = name
            func = getattr(canvas, self._canvas_shape_name)
        return func(self, **self._draw_kwds())


###############################################################################
def lazy_curve_init(self, *args, **kwds):
    '''Generic init implementation for multiple inheritance from a
    mathematical shape and Curve.

    It is less efficient that it could be, but is a workable default for
    lazy coders.'''

    get = kwds.pop
    Curve.__init__(self, get('width', 1.0), get('color', black))
    type(self).__bases__[0].__init__(self, *args, **kwds)


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

        get = kwds.pop
        width = get('width', 1.0)
        color = get('color', black)
        Curve.__init__(self, width, color)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if isinstance(value, Color):
            self._color = value
        else:
            self._color = Color(value)

    @property
    def linecolor(self):
        return self._color

    @linecolor.setter
    def linecolor(self, value):
        self._color = Color(value)

    def _draw_kwds(self):
        return dict(color=self.color, width=self.width)


class Segment(shapes.mSegment, Curve):

    '''Um segmento de reta que vai do ponto start até end'''

    __init__ = lazy_curve_init
    __slots__ = 'screen_handle'

class Ray(shapes.mRay, Curve):

    '''Um segmento de reta semi-finito que inicia em um ponto start
    específico'''

    __init__ = lazy_curve_init
    __slots__ = 'screen_handle'

class Line(shapes.mLine, Curve):

    '''Uma linha infinita'''

    __init__ = lazy_curve_init
    __slots__ = 'screen_handle'


class Path(shapes.mPath, Curve):

    '''Um caminho formado por uma sequência de pontos'''

    __init__ = lazy_curve_init
    __slots__ = 'screen_handle'
    
# Objetos sólidos (figuras fechadas) ##########################################


def lazy_shape_init(self, *args, **kwds):
    '''Generic init implementation for multiple inheritance from a
    mathematical shape and Shape.

    It is less efficient that it could be, but is a workable default for
    lazy coders.'''

    get = kwds.pop
    Shape.__init__(self, get('solid', True), get('color', black),
                   get('linewidth', 0.0), get('linecolor', black))
    type(self).__bases__[0].__init__(self, *args, **kwds)


class Shape(Drawable):

    '''Classe pai para todas as figuras fechadas. Define as propriedades
    solid, color, linewidth e linecolor.'''

    def __init__(self, solid=True, color=black,
                 linewidth=0.0, linecolor=black):

        if not isinstance(color, Color):
            color = Color(color)
        if not isinstance(linecolor, Color):
            linecolor = Color(color)
        self._color = color
        self._linecolor = linecolor
        self.linewidth = linewidth
        self.solid = bool(solid)

    def _init_colors_from_kwds(self, kwds):
        '''Extrai as keywords do dicionário kwds, e inicializa as propriedades
        de cores do objeto. As outras entradas do dicionário podem ser
        passadas para o construtor do objeto geométrico'''

        solid = kwds.pop('solid', True)
        color = kwds.pop('solid', black)
        linecolor = kwds.pop('solid', black)
        line_width = kwds.pop('solid', 0.0)
        Shape.__init__(self, solid, color, line_width, linecolor)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = Color(value)

    @property
    def linecolor(self):
        return self._linecolor

    @linecolor.setter
    def linecolor(self, value):
        self._linecolor = Color(value)

    def _draw_kwds(self):
        return dict(
            solid=self.solid,
            color=self.color,
            line_width=self.linewidth,
            linecolor=self.linecolor)


class Circle(shapes.mCircle, Shape):

    '''Um círculo de raio `radius` e centro em `center`.'''

    __slots__ = 'screen_handle'
    
    def __init__(self, radius, pos=(0, 0), **kwds):

        shapes.mCircle.__init__(self, radius, pos)
        Shape.__init__(self, **kwds)


class AABB(shapes.mAABB, Shape):

    '''Caixa de contorno alinhada aos eixos'''

    __init__ = lazy_shape_init
    __slots__ = 'screen_handle'

class Sprite(AABB):

    '''Define uma image animada. O controle de frames é feito a cada chamada
    do método draw(). Desta forma, caso o método seja chamado duas vezes por
    frame, a velocidade de animação será o dobro da desejada.'''
    

class Circuit(shapes.mCircuit, Shape):

    '''Um caminho fechado com um interior bem definido.'''

    __init__ = lazy_shape_init
    __slots__ = 'screen_handle'

class Poly(shapes.mPoly, Shape):

    '''Objetos da classe Poly representam polígonos dados por uma lista
    de vértices.'''

    __init__ = lazy_shape_init
    __slots__ = 'screen_handle'


class RegularPoly(Poly):

    '''Objetos da classe Poly representam polígonos regulares dados por uma lista
    de vértices.'''
    
    #TODO: implementar
    
    def __init__(self, *args, **kwds): 
        raise NotImplementedError


class Rectangle(shapes.mRectangle, Shape):

    '''Especialização de Poly para representar retângulos.

    Pode ser inicializado como uma AABB, mas com um parâmetro extra `theta`
    para definir um ângulo de rotação.'''

    # TODO: não consegue herdar de Poly. Porque?
    __init__ = lazy_shape_init
    __slots__ = 'screen_handle'

    def draw(self, canvas):
        canvas.draw_poly(self, **self._draw_kwds())


class Triangle(shapes.mTriangle, Shape):

    '''Especialização de Poly para representar triângulos.'''

    # TODO: não consegue herdar de Poly. Porque?
    __init__ = lazy_shape_init
    __slots__ = 'screen_handle'

    def draw(self, canvas):
        canvas.draw_poly(self, **self._draw_kwds())


if __name__ == '__main__':
    seg = Segment((0, 1), (1, 0), width=2, color=white)
    print(seg.__dict__)
