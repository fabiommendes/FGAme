# -*- coding: utf8 -*-


import cython as C
import mathfuncs as m
from base import auto_public
from util import pyinject
if not C.compiled:
# TODO: REMOVER QUANDO V3 FOR IMPLEMENTADO
#    from mathtools.vec3 import Vec3

 __all__ = ['Mat3','RotMat3','mMat3']

 number = (float,int)


######
#   Matriz 3 x 3
######

class Mat3(object):
    '''
        Implementa uma matriz tridimensional e operações básicas de 
        álgebra linear

    Example
    -------
    Criamos uma matriz a partir de uma lista de listas

    >>> M = Mat3([ [1,2,3],
    ...            [4,5,6],
    ...            [7,8,9]])
    
    Podemos também utilizar classes especializadas, como por exemplo a `RotMat3`
    , que cria uma matriz de rotação de tridimensional

    >>> R = RotMat3(3.1415); R
    |-1 -0 0|
    | 0 -1 0|
    | 0  0 1| 
    
    Os objetos da classe Mat3 implementam as operações algebricas básicas
    TODO: fazer testes para operações basicas de matriz mat3
    

    '''
    __slots__ = ['_a', '_b', '_c',
                 '_d', '_e', '_f',
                 '_g', '_h', '_i']

    def __init__(self,obj):
        c1, c2, c3 = obj
        a, b, c = c1
        d, e, f = c2
        g, h, i  = c3

        self._a = a + 0.0; self._b = b + 0.0; self._c = c + 0.0
        self._d = d + 0.0; self._e = e + 0.0; self._f = f + 0.0
        self._g = g + 0.0; self._h = h + 0.0; self._i = i + 0.0

    @classmethod
    def _from_lists_(cls,M):
        '''Inicia a matriz a partir de uma lista de linhas.Corresponde ao
           método de inicialização padrão, mas pode ser invocado por classes
           caso a assinatura do contrutor padrão seja diferente'''
        new = object.__new__(cls)
        Mat3.__init__(new,M)
        return new

    @classmethod
    def from_flat(cls,data):
        '''Constroi matriz a partir de dados linearizados'''
        return cls.from_flat(data,restype=cls)
    
    @classmethod
    def _from_flat(cls,data,restype=None):
        it = iter(data) 
        new = object.__new__(restype or cls)
        new._a = next(it) + 0.0;new._b = next(it) + 0.0;new._c = next(it)+ 0.0
        new._d = next(it) + 0.0;new._e = next(it) + 0.0;new._f = next(it)+ 0.0
        new._g = next(it) + 0.0;new._h = next(it) + 0.0;new._i = next(it)+ 0.0
        
        return new
        

    # Métodos de apresentação da informação da matriz ##################
    
    def aslist(self):
        '''Retorna a matrix como uma lista de listas'''
        a,b,c,d,e,f,g,h,i = self.flat()
        return [[a,b,c],[d,e,f],[g,h,i]]
    
    def flat(self):
        '''Itera sobre todos os elementos da matriz, primeiro os 
           elementos da primeira linha, depois o da segunda e 
           por último o da terceira linha.'''
        yield(self._a);yield(self._b);yield(self._c)
        yield(self._d);yield(self._e);yield(self._f)
        yield(self._g);yield(self._h);yield(self._i)


    def colvecs(self):
        '''Retorna uma lista com os vecores coluna da matriz.'''
        # TODO: descomentar quando implementado o vec3
        #   return [Vec3(self._a,self._d,self._g),
        #           Vec3(sefl._b,self._e,self._h),
        #           Vec3(self._c,self._f,self_i)]
        pass

    def rowvecs(self):
        '''Retorna uma lista com os vetores das linhas da matriz.'''
        #TODO:   descomentar quando for implementado o vec3
        # return [Vec3(self._a, self._b, self._c),
        #         Vec3(self._d, self._e, self._f),
        #         Vec3(self._g, self._h, self._i)]
        pass

    # Métodos para cálculo de propriedades lineares da matriz ###########
    def det(self):
        '''Retorna o determinante da matriz
        >>> M = Mat3([[1,2,3],[4,5,6],[7,8,9]])
        >>> M.det() 
        0.0
        '''
        d1 = + (self._a * self._e * self._i)
        d2 = + (self._b * self._f * self._g)
        d3 = + (self._c * self._d * self._h)
        d4 = - (self._c * self._e * self._g)
        d5 = - (self._a * self._f * self._h)
        d6 = - (self._b * self._d * self._i)
        return d1 + d2 + d3 + d4 + d5 + d6
        
    def trace(self):
        '''  retornar o traco da matriz 
        >>> M = Mat3([[1,2,3],[4,5,6],[7,8,9]])
        >>> M.trace() 
        15.0
        '''
        return self._a+self._e+self._i

    def diag(self):
        '''Retorna uma lista com os valores na diagonal principal da matriz
    
        >>> M = Mat3([[1,2,3],[4,5,6],[7,8,9]])
        >>> M.diag() 
        [1.0, 5.0, 9.0]
        '''
        return [self._a,self._e,self._i] 

    def eig(self):
        '''Retorna uma tupla com a lista de autovalores e a matriz dos 
        autovetores'''
        #TODO: Vec3
        pass
    
    def eigval(self):
        '''Retorna uma tupla com os autovalores da matriz

        '''
        #TODO:
        pass
        
        
    def eigvec(self, transpose=False):
        '''Retorna uma lista com os autovetores normalizados da matriz.

        A ordem dos autovetores corresponde àquela retornada pelo método
        `M.eigval()`'''
        #TODO:
        pass

    def transpose(self):
        '''Retorna a transposta da matriz

        >>> M = Mat3([[1, 2, 3],[4, 5, 6],[7, 8, 9]])
        >>> M.transpose()
        |1  4  7| 
        |2  5  8|
        |3  6  9|
        '''
        a, b, c, d, e, f, g, h, i = self.flat()
        M = [[ a, d, g ],
             [ b, e, h ],
             [ c, f, i ]]
        return self._from_lists_(M)


    def rotate(self):
        '''Retorna uma matriz rotacionada pro um ângulo theta
        '''
        R = RotMat3(theta)
        return R * self * R.transpose()

    def inv(self):
        '''Retorna a inversa da matriz'''
        
        det  = self.det()
        a,b,c,d,e,f,g,h,i = self.flat()
        #TODO: tentar grassman
        return det

    # Sobrescrita de operadores #################################
    def _fmt_number(self,x):
        '''Função auxiliar para __repr__: formata número para impressão'''
        return ('%3f' % x).rstrip('0').rstrip('.')

    def __repr__(self):
        '''x.__repr__(): <==> repr(x)'''
        l  = []
        for element in self.flat(): 
             l.append(element)
        a, b, c, d, e, f, g, h, i = map(self._fmt_number, l)
        n = max(len(a), len(d),len(g))
        m = max(len(b), len(e),len(h))
        o = max(len(c), len(f), len(i))

        l1 = '|%s  %s  %s|' % (a.rjust(n), b.rjust(m), c.rjust(o))
        l2 = '|%s  %s  %s|' % (d.rjust(n), e.rjust(m), f.rjust(o))
        l3 = '|%s  %s  %s|' % (g.rjust(n), h.rjust(m), i.rjust(o))
        return '%s\n%s\n%s' % (l1, l2,l3)
        
    def __str__(self):
       '''x.__str__() <==> str(x)'''
       return repr(self)

    def __len__(self):
        return 3

    def __iter__(self):
        it = self.flat()
    # TODO:   ESPERANDO VETOR 3
    #    yield Vec3(next(it),next(it),next(it))
    #    yield Vec3(next(it),next(it),next(it))
    #    yield Vec3(next(it),next(it),next(it))

    def __getitem__(self, idx):
        '''x.__getitem__(i) <==> x[i]'''
        if isinstance(idx,tuple):
            i, j = idx
            return self._data[i][j]
# TODO: ESPERANDO VETOR 3
#       elif isinstance(idx,int):
#            return Vec3(*self._data[])


    # Operações matemáticas###############



    def __mul__(self,other):
        '''x.__mul__(y) <==> x * y'''
        #TODO:
        pass
        

    def __rmult__(self,other):
        #TODO:
        pass 



    def __div__(self, other):
        '''x.__div__(y) <==> x / y'''
        return self._from_flat(x / other for x in self.flat())

    def __truediv__(self, other):
        '''x.__div__(y) <==> x / y'''
        return self._from_flat(x / other for x in self.flat())

    def __floordiv__(self,other):
        '''x.__div__(y) <==> x / y'''
        return self._from_flat(x // other for x in self.flat())

    def __add__(self,other):
        '''x.__add__(y) <==> x + y'''
        return self._from_flat(x + y for (x,y) in
                               zip(self.flat(),other.flat()))
    def __radd__(self,other):
        '''x.__radd__(y) <==> y + x'''
        return self + other

    def __sub__(self,other):    
        '''x.__sub__(y) <==> x - y'''
        return self._from_flat(x - y for (x,y) in
                               zip(self.flat(),other.flat()))

    def __rsub__(self,other):
        '''x.__rsub__(y) <==> y - x '''
        return self._from_flat(y - x for (x,y) in 
                               zip(self.flat(),other.flat()))

    def __neg__(self):
        '''x.__neg__() <==> -x'''
        return self._from_flat(-x for x in self.flat())    

    def __nonzero__(self):
        return any(self.flat())


class mMat3(Mat3):
    '''Versão mutável de Mat3'''

    __slots__ = ['_data']

    def __init__(self,data):
        super(mMat3,self).__init__(data)
        self.data = list(data)
    def __setattr__(self,idx,value):
        i, j, k = idx
        self._data[i][j] = value


if __name__ == '__main__':
    import doctest
    doctest.testmod()
