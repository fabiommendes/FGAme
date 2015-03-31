# -*- coding: utf8 -*-
# @PydevCodeAnalysisIgnore

import os
from math import pi
cdef extern from "math.h":
    double log(double)
    double sqrt(double)
    double cos(double)
    double sin(double)

cdef double PI = pi
cdef double SQRT_2 = sqrt(2)
cdef tuple number = (float, int)

if not os.environ.get('FGAME_USE_EXTENSIONS', True):
    raise ImportError

__all__ = ['Vector', 'VectorM', 'asvector', 'dot', 'cross']


cdef class Vector(object):
    cdef double _x, _y

    def __cinit__(Vector self, x_or_data, y=None):
        '''Representa um vetor bidimensional.
        
        Exemplo
        -------
        
        Criamos um vetor chamando a classe com as componentes como argumento.
        
        >>> v = Vector(3, 4); print(v)
        Vector(3, 4)

        Os métodos de listas funcionam para objetos do tipo Vector:
        
        >>> v[0], v[1], len(v)
        (3.0, 4.0, 2)
        
        Objetos do tipo Vector também aceitam operações matemáticas
        
        >>> v + 2 * v
        Vector(9, 12)
        
        Além de algumas funções de conveniência para calcular o módulo, 
        vetor unitário, etc.
        
        >>> v.norm()
        5.0
        
        >>> v.normalized()
        Vector(0.6, 0.8)
        '''

        if y is None:
            self._x, self._y = x_or_data
        else:
            self._x = x_or_data
            self._y = y

    def __init__(self, x_or_data, y=None):
        pass

    def as_tuple(self):
        '''Retorna a representação do vetor como uma tupla'''
        return (self._x, self._y)

    cpdef double norm(self):
        '''Retorna o módulo (norma) do vetor'''

        return sqrt(self._x * self._x + self._y * self._y)

    cpdef double norm_sqr(self):
        '''Retorna o módulo do vetor ao quadrado'''

        return self._x * self._x + self._y *self._y

    cpdef Vector normalized(self):
        '''Retorna um vetor unitário'''

        cdef double norm = self.norm()
        if norm != 0:
            return Vector(self._x/norm, self._y/norm)
        else:
            return Vector(0, 0)

    cpdef Vector rotated(Vector self, theta, axis=None):
        '''Retorna um vetor rotacionado por um ângulo theta'''

        cdef double t = float(theta)
        cdef double x, y, cos_t = cos(t), sin_t = sin(t)
    
        if axis is None:
            x = self._x
            y = self._y
            return self._new(x * cos_t - y * sin_t, x * sin_t + y * cos_t)
        else:
            x, y = self - axis
            return self._new(x * cos_t - y * sin_t, x * sin_t + y * cos_t) + axis

    # Métodos mágicos ----------------------------------------------------------
    def __len__(self):
        return 2

    def __repr__(Vector self):
        '''x.__repr__() <==> repr(x)'''

        x, y = self
        x = str(x) if x != int(x) else str(int(x))
        y = str(y) if y != int(y) else str(int(y))
        tname = type(self).__name__
        return '%s(%s, %s)' % (tname, x, y)

    def __str__(Vector self):
        '''x.__str__() <==> str(x)'''
        return repr(self)

    def __iter__(Vector self):
        yield self._x
        yield self._y

    def __getitem__(Vector self, i):
        '''x.__getitem__(i) <==> x[i]'''
        if i == 0:
            return self._x
        elif i == 1:
            return self._y
        else:
            raise IndexError(i)

    def __mul__(A, B):
        '''x.__mul__(y) <==> x * y'''

        cdef Vector self
        cdef double scalar

        if isinstance(A, Vector):
            self = A
            other = B
        else:
            self = B
            other = A
            
        try:
            scalar = float(other)
            return self._new(self._x * scalar, self._y * scalar)
        except TypeError:
            if isinstance(other, Vector):
                raise
            return other.__rmul__(self)

    def __div__(Vector self, other):
        '''x.__div__(y) <==> x / y'''

        return self._new(self._x / other, self._y / other)

    def __truediv__(Vector self, other):
        '''x.__div__(y) <==> x / y'''

        return self._new(self._x / other, self._y / other)

    def __add__(self, other):
        '''x.__add__(y) <==> x + y'''

        cdef double X=0, Y=0
        cdef Vector aux
        new = None
        
        # Processa o primeiro argumento
        if isinstance(self, Vector):
            aux = self
            X += aux._x
            Y += aux._y
            new = self._new
        else:
            x, y = self
            X += x
            Y += y
            
        # Processa o segundo argumento
        if isinstance(other, Vector):
            aux = other
            X += aux._x
            Y += aux._y
            if new is None:
                new = other._new
        else:
            x, y = other
            X += x
            Y += y
            
        return new(X, Y)

    def __sub__(self, other):
        '''x.__sub__(y) <==> x - y'''
        
        
        cdef double X=0, Y=0
        cdef Vector aux
        new = None
        
        # Processa o primeiro argumento
        if isinstance(self, Vector):
            aux = self
            X += aux._x
            Y += aux._y
            new = self._new
        else:
            x, y = self
            X += x
            Y += y
            
        # Processa o segundo argumento
        if isinstance(other, Vector):
            aux = other
            X -= aux._x
            Y -= aux._y
            if new is None:
                new = other._new
        else:
            x, y = other
            X -= x
            Y -= y
            
        return new(X, Y)

    def __neg__(Vector self):
        '''x.__neg() <==> -x'''
        return self._new(-self._x, -self._y)

    def __nonzero__(self):
        return True
    
    def __richcmp__(Vector self, other, int method):
        x, y = other
        return self._x == x and self._y == y            
        
    cpdef Vector _new(self, double x, double y):
        return type(self)(x, y)

    property x:
        def __get__(Vector self): 
            return self._x
        
        def __set__(self, value): 
            raise AttributeError

        def __del__(self):
            raise AttributeError

    property y:
        def __get__(Vector self): 
            return self._y
        
        def __set__(self, value): 
            raise AttributeError
        
        def __del__(self):
            raise AttributeError


cdef class VectorM(Vector):
    '''Como Vector, mas com elementos mutáveis'''
    
    def __setitem__(Vector self, i, value):
        if i == 0:
            self._x = value
        elif i == 1:
            self._y = value
        else:
            raise IndexError

    def __iadd__(Vector self, other):
        '''x.__iadd__(y) <==> x += y'''

        self._x += other[0]
        self._y += other[1]
        return self

    def __isub__(Vector self, other):
        '''x.__isub__(y) <==> x -= y'''

        self._x -= other[0]
        self._y -= other[1]
        return self

    def __imul__(Vector self, other):
        '''x.__imul__(y) <==> x *= y'''

        self._x *= other
        self._y *= other
        return self

    def __idiv__(Vector self, other):
        '''x.__idiv__(y) <==> x /= y'''
 
        self._x /= other
        self._y /= other
        return self
    
    def __itruediv__(Vector self, other):
        '''x.__idiv__(y) <==> x /= y'''
 
        self._x /= other
        self._y /= other
        return self
 
    def rotate(Vector self, theta, axis=(0, 0)):
        '''Realiza rotação *inplace*'''

        x, y = self -axis
        cos_t, sin_t = cos(theta), sin(theta)
        self._x = x * cos_t - y * sin_t + axis[0]
        self._y = x * sin_t + y * cos_t + axis[1]

    def update(Vector self, other, y=None):
        '''Copia as coordenadas x, y do objeto other'''

        cdef Vector vector 
        if y is None:
            try:
                vector = other
                self._x = vector._x
                self._y = vector._y
            except TypeError:
                x, y = map(float, other)
                self._x = x
                self._y = y
        else:
            self._x = float(other)
            self._y = float(y)

    def copy(self):
        '''Retorna uma cópia de si mesmo'''

        return VectorM(self._x, self._y)
    
    property x:
        def __get__(Vector self): 
            return self._x
        
        def __set__(self, value): 
            self._x = value

        def __del__(self):
            raise AttributeError
        
    property y:
        def __get__(Vector self): 
            return self._y
        
        def __set__(self, value): 
            self._y = value
    
        def __del__(self):
            raise AttributeError

def asvector(v):
    '''Retorna o objeto como uma instância da classe Vetor'''

    if isinstance(v, Vector):
        return v
    else:
        return Vector(*v)

#===============================================================================
# Funções com vetores
#===============================================================================
def dot(v1, v2):
    '''Calcula o produto escalar entre dois vetores'''

    cdef Vector u1, u2
    
    if isinstance(v1, Vector) and isinstance(v2, Vector):
        u1 = v1
        u2 = v2
        return u1._x * u2._x + u1._y * u2._y
    else:
        return sum(zip(v1, v2))

def cross(v1, v2):
    '''Retorna a compontente z do produto vetorial de dois vetores bidimensionais'''

    cdef Vector u1, u2
    
    if isinstance(v1, Vector) and isinstance(v2, Vector):
        u1 = v1
        u2 = v2
        return u1._x * u2._y - u2._x * u1._y
    else:
        x1, y1 = v1
        x2, y2 = v2
        return x1 * y2 - x2 * y1

if __name__ == '__main__':
    import doctest
    doctest.testmod()
