#-*-coding: utf8 -*-
from FGAme.draw import Drawable, Color
from FGAme.mathutils import VectorM, sin, cos, pi
import copy

class Geometric(Drawable):
    '''Classe pai para todos os objetos geométricos'''
    
    # Especifica a geometria primitiva explicitamente --------------------------
    is_circle = False
    is_poly = False
    is_line = False
    is_rect = False
    is_drawable = True

    # Constantes da classe -----------------------------------------------------
    __slots__ = ['pos', 'theta', 'solid', 'lw', 'color']

    def __init__(self, pos=(0, 0), theta=0.0, color='black', solid=True, lw=0.0):
        self.pos = VectorM(*pos)
        self.theta = float(theta)
        self.solid = bool(solid)
        self.lw = float(lw)
        self.color = Color(color)

    def rotate(self, theta, axis=None):
        if axis is None:
            if theta:
                self.theta += theta
        else:
            delta = self.pos - axis
            self.rotate(theta)
            self.move(delta.rotated(theta))

    def move(self, delta):
        if delta[0] or delta[1]:
            self.pos += delta

    def as_poly(self):
        vertices = self.as_vertices(relative=True)
        return Poly(vertices, pos=self.pos, color=self.color, solid=self.solid)

    def as_vertices(self, relative=False):
        raise NotImplementedError

class Circle(Geometric):
    '''Objetos da classe Circle representam círculos.'''
    
    __slots__ = ['radius']
    is_circle = True
    
    def __init__(self, pos, radius, color='black', solid=True, lw=0.0):
        super(Circle, self).__init__(pos, 0, color, solid, lw)
        self.radius = float(radius)

    def as_poly(self, N=20):
        '''Retorna a aproximação do círculo como um polígono de N lados'''

        vertices = self.as_vertices(N, relative=True, scaled=True)
        return Poly(vertices, pos=self.pos, color=self.color, solid=self.solid)

    def as_vertices(self, N=20, relative=False, scaled=True):
        R = self._radius * (self._scale if scaled else 1)
        cos, sin = cos, sin

        if relative == False:
            delta = 2 * pi / N
            vertices = ((cos(delta * t), sin(delta * t)) for t in range(N))
            return list(vertices)
        X, Y = self._pos
        return [ (x + X, y + Y) for (x, y) in vertices ]

    def paint(self, screen):
        screen.paint_circle(self.pos, self.radius, self.color)

class RectangleAA(Geometric):
    '''Objetos da classe RectangleAA representam retângulos alinhados aos eixos 
    principais.
    
    É inicializado com uma tupla (x, y, dx, dy) onde (x,y) representam as 
    coordenadas inferior-esquerda do retângulo e dx e dy as dimensões nos eixos
    X e Y respectivamente.
    
    Existem construtores alternativos: centered(), ..., etc.
    '''
    __slots__ = ['shape']
    is_rect = True
    
    def __init__(self, rect=None, shape=None, pos=(0, 0), color='black', solid=True, lw=0.0):
        if rect:
            super(RectangleAA, self).__init__(rect[:2], 0, color, solid, lw)
            self.shape = tuple(rect[2:])
            if len(rect) != 4:
                raise ValueError('shape must be a tuple: (x, y, dx, dy)')
        else:
            super(RectangleAA, self).__init__(pos, 0, color, solid, lw)
            self.shape = shape
        
    # Construtores alternativos ------------------------------------------------
    @classmethod
    def centered(self, *args, **kwds):
        '''Inicia o retângulo especificando as coordenadas do centro e as 
        dimensões em X e em Y.'''
        if len(args) == 1:
            x, y, dx, dy = args[0]
        elif len(args) == 2:
            x, y = args[0]
            dx, dy = args[1]
        elif len(args) == 4:
            x, y, dx, dy = args
        else:
            raise TypeError('must be initialized with 1, 2, or 4 arguments')
        x -= dx/2
        y -= dy/2
        return RectangleAA((x, y, dx, dy), **kwds)
    
    # Funções da API -----------------------------------------------------------
    @property
    def rect(self):
        return tuple(self.pos) + self.shape
    
    def rotate(self, theta):
        raise ValueError('cannot rotate a Rect object')

    def as_poly(self, mode=4, scaled=True):
        '''Retorna o retângulo como um objeto do tipo polígono'''

        vertices = self.as_vertices(mode, relative=True)
        return Poly(vertices, pos=self.pos, color=self.color, solid=self.solid)

    def as_vertices(self, mode=4, relative=False, scaled=True):
        '''Calcula apenas os vértices do polígono
        
        Parameters
        ----------
        
        mode : int
            Modo de conversão, caso a posição seja relativa: 0-começa no canto
            inferior direito, em sentido anti-horário até 3. `mode=4` 
            corresponde ao centro.
        '''
        if scaled:
            dX, dY = self.shape * self._scale
        else:
            dX, dY = self.shape
        X, Y = self._pos

        if not relative:
            mode = 0

        if mode == 4:
            dX /= 2
            dY /= 2
            vertices = [(X - dX, Y - dY), (X + dX, Y - dY),
                        (X + dX, Y + dY), (X - dX, Y + dY)]
        elif mode == 0:
            vertices = [(X, Y), (X + dX, Y),
                        (X + dX, Y + dY), (X, Y + dY)]
        elif mode == 1:
            vertices = [(X - dX, Y), (X, Y),
                        (X, Y + dY), (X - dX, Y + dY)]
        elif mode == 2:
            vertices = [(X - dX, Y - dY), (X, Y - dY),
                        (X, Y), (X - dX, Y)]
        elif mode == 3:
            vertices = [(X, Y - dY), (X + dX, Y - dY),
                        (X + dX, Y), (X, Y)]
        else:
            raise ValueError('mode must be in range(0, 5)')

        if relative:
            return vertices
        else:
            return [ (x + X, y + Y) for (x, y) in vertices ]

class Poly(Geometric):
    '''Objetos da classe Poly representam polígonos especificados por uma lista
    de vértices.'''
    
    is_poly = True
    __slots__ = ['vertices']
    
    def __init__(self, vertices, color='black', solid=True, lw=0):
        super(Poly, self).__init__((0, 0), 0, color, solid, lw)
        self.vertices = vertices

    def as_poly(self):
        return copy.deepcopy(self)

    def as_vertices(self, relative=False, scaled=True):
        vertices = self.vertices
        if scaled and self._scale != 0:
            scale = self._scale
            vertices = [ v * scale for v in vertices ]
        if relative:
            pos = self._pos
            return [ v + pos for v in vertices ]
        return vertices

#===============================================================================
# Delegate classes
#===============================================================================
class GeometricEcho(object):
    '''Classe base para objetos geométricos sem estado que assumem suas 
    características do objeto físico correspondente'''
    
    __slots__ = ['obj', 'color', 'lw', 'solid']

    def __init__(self, obj, color=None, lw=None, solid=None):
        self.obj = obj
        
        if color is None:
            try:
                self.color = obj.color or Color('black')
            except AttributeError:
                self.color = Color('black')
        else:
            self.color = Color(color)
        
        if lw is None:
            try:
                self.lw = obj.lw
            except AttributeError:
                self.lw = 0.0
        else:
            self.lw = float(lw)
        
        if solid is None:
            try:
                self.solid = obj.solid
            except AttributeError:
                self.solid = True
        else:
            self.solid = bool(solid)
            
    @property
    def pos(self):
        return self.obj.pos
    
    @property
    def theta(self):
        return self.obj.theta
    
class CircleEcho(GeometricEcho):
    base = Circle
    is_circle = True
    
    @property
    def radius(self):
        return self.obj.radius

class RectEcho(GeometricEcho):
    base = RectangleAA
    is_rect = True
    
    @property
    def shape(self):
        return self.obj.shape

    @property
    def rect(self):
        return self.obj.rect
    
class PolyEcho(GeometricEcho):
    base = Poly
    is_poly = True

    @property
    def vertices(self):
        return self.obj.vertices

if __name__ == '__main__':
    import doctest
    doctest.testmod()