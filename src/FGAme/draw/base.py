import copy
from FGAme.draw import Color
from FGAme.mathtools import shapes


# Constantes
black = Color('black')
white = Color('white')
__all__ = [
    # Abstratos
    'Drawable', 'Curve', 'Shape',
    
    # Curvas
    'Segment', 'Path',
    
    # Sólidos
    'AABB', 'Circle', 'Circuit', 'Poly', 'Rectangle', 'RegularPoly', 'Triangle',
]


class Drawable(object):

    """Classe mãe para todos os objetos que podem ser desenhados na tela"""

    visible = True
    __slots__ = ('__dict__',)

    def show(self):
        """Marca a propriedade `visible` como verdadeira e renderiza o 
        objeto na tela."""
        
        self.visible = True

    def hide(self):
        """Marca a propriedade `visible` como falsa e para de renderizar o 
        objeto na tela."""
        
        self.visible = False

    def copy(self):
        """Retorna uma cópia do objeto"""

        return copy.copy(self)

    def draw(self, canvas):
        """Desenha objeto na tela"""

        raise NotImplementedError
    
    def _prepare_canvas(self, canvas_obj):
        name = 'draw_' + type(self).__name__.lower()
        type(self)._canvas_func = getattr(canvas_obj, name)
        type(self)._canvas_obj = canvas_obj


class CurveOrShape(Drawable):
    """Base class for Curve and Shape objects"""
    
    _linewidth = 1
    _linecolor = None
    _fillcolor = None

    def __init__(self, *args, **kwds):
        linecolor = kwds.pop('linecolor', None)
        fillcolor = kwds.pop('fillcolor', None)
        linewidth = kwds.pop('linewidth', 0)

        if linecolor is not None:
            self._linecolor = Color(linecolor)
        if linewidth is not None:
            self._linewidth = float(linewidth)
        if fillcolor is not None:
            self._fillcolor = Color(fillcolor)
        super(CurveOrShape, self).__init__(*args, **kwds)
    
    @property
    def linecolor(self):
        return self._linecolor

    @linecolor.setter
    def linecolor(self, value):
        self._linecolor = Color(value)

    @property
    def linewidth(self):
        return self._linewidth
    
    @linewidth.setter
    def linewidth(self, value):
        self._linewidth = float(value)


#
# Curve
#
class Curve(CurveOrShape):

    """Classe pai para todos os objetos geométricos que definem uma curva
    aberta.
    """

    def __init__(self, *args, **kwds):
        linewidth = kwds.pop('linewidth', 1)
        linecolor = kwds.pop('linecolor', None)
        color = kwds.pop('color', black)
        linecolor = color if linecolor is None else linecolor
        kwds.update(linewidth=linewidth, linecolor=linecolor)
        super(Curve, self).__init__(*args, **kwds)

    color = CurveOrShape.linecolor
    
    def draw(self, canvas):
        try:
            if self._canvas_obj is not canvas:
                raise AttributeError
        except AttributeError:
            self._prepare_canvas(canvas)

        self._prepare_canvas(canvas)
        lc = self.linecolor
        lw = self.linewidth
        return self._canvas_func(self, lc, lw)
    

class Segment(Curve, shapes.mSegment):

    """Um segmento de reta que vai do ponto start até end"""


class Ray(Curve, shapes.mRay):

    """Um segmento de reta semi-finito que inicia em um ponto start
    específico"""

    def __init__(self, *args, **kwds):
        raise RuntimeError('lines are not supported, perhaps you mean Segment?')


class Line(Curve, shapes.mLine):

    """Uma linha infinita"""

    def __init__(self, *args, **kwds):
        raise RuntimeError('lines are not supported, perhaps you mean Segment?')


class Path(Curve, shapes.mPath):

    """Um caminho formado por uma sequência de pontos"""


#
# Objetos sólidos (figuras fechadas)
#
class Shape(CurveOrShape):

    """Classe pai para todas as figuras fechadas. Define as propriedades
    color, fillcolor, linewidth e linecolor."""

    def __init__(self, *args, **kwds):
        linewidth = kwds.pop('linewidth', None)
        linecolor = kwds.pop('linecolor', None)
        fillcolor = kwds.pop('fillcolor', None)
        color = kwds.pop('color', black)

        if linewidth is None:
            linewidth = 0 if fillcolor is not None else 1
        if not linewidth:
            linecolor = None
        if linecolor is None:
            linecolor = color
        fillcolor = color if fillcolor is None else fillcolor

        kwds.update(fillcolor=fillcolor,
                    linecolor=linecolor, linewidth=linewidth)
        super(Shape, self).__init__(*args, **kwds)

    @property
    def fillcolor(self):
        return self._fillcolor

    @fillcolor.setter
    def fillcolor(self, value):
        self._fillcolor = Color(value)

    color = fillcolor
    
    def draw(self, canvas):
        try:
            if self._canvas_obj is not canvas:
                raise AttributeError
        except AttributeError:
            self._prepare_canvas(canvas)
            
        color = self.fillcolor
        lc = self.linecolor
        lw = self.linewidth
        return self._canvas_func(self, color, lc, lw)


class Circle(Shape, shapes.mCircle):

    """Um círculo de raio `radius` e centro em `center`."""


class AABB(Shape, shapes.mAABB):

    """Caixa de contorno alinhada aos eixos"""


class Circuit(Shape, shapes.mCircuit):

    """Um caminho fechado com um interior bem definido."""


class Poly(Shape, shapes.mPoly):

    """Objetos da classe Poly representam polígonos dados por uma lista
    de vértices."""


class RegularPoly(Poly, shapes.mRegularPoly):

    """Objetos da classe Poly representam polígonos regulares dados por uma lista
    de vértices."""
    

class Rectangle(Poly, shapes.mRectangle):

    """Especialização de Poly para representar retângulos.

    Pode ser inicializado como uma AABB, mas com um parâmetro extra `theta`
    para definir um ângulo de rotação."""


class Triangle(Poly, shapes.mTriangle):

    """Especialização de Poly para representar triângulos."""
