# -*- coding: utf8 -*-

from mathtools import RotMat2, Vec2, Point2, VecArray, dot
from mathtools.shapes import aabb_bbox
from math import sqrt, pi, sin


###############################################################################
# Generic polygons
###############################################################################
class CircuitBase(VecArray):

    '''Base class for Circuit and mCircuit'''

    __slots__ = ['vertices']

    def iter_closing(self):
        '''Itera sobre os pontos do objeto repetindo o primeiro ao final'''

        for x in self._data:
            yield x
        yield self._data[0]

    def get(self, i):
        '''Semelhante à obj[i], mas ao invés de overflow, assume índices
        periódicos'''

        return self._data[i % len(self._data)]

    # Métodos utilizado pelo SAT ##############################################
    def directions(self, n):
        '''Retorna a lista de direções exaustivas para o teste do SAT
        associadas ao objeto.'''

        out = []
        p0 = self._data[-1]
        for p in self._data:
            x, y = p - p0
            p0 = p
            out.append(Vec2(-y, x))
        return out

    def shadow(self, n):
        '''Retorna as coordenadas da sombra na direção n dada.
        Assume n normalizado.'''

        r = self.radius
        center_pos = dot(self.pos, n)
        return (center_pos - r, center_pos + r)

    # Propriedades do polígono ################################################
    def is_simple(self):
        pass

    def is_convex(self):
        pass

    # Funções de manipulação de envoltórias e extração de propriedades
    # geométricas
    def center(self):
        '''Retorna o centro geométrico do objeto'''

        return center_of_mass(self)

    def clip(self, other):
        return clip(self, other)

    def convex_hull(self, other):
        return convex_hull(self)

    def ROG(self, axis=None):
        '''Retorna o raio de giração do objeto. Para objetos com densidade
        constante, relacionamos o raio de giração R com a massa M e o momento
        de inércia com relação ao centro de massa I_cm pela fórmula:

            I_cm = M R^2.
        '''

        return sqrt(ROG_sqr(self, axis))

    def ROG_sqr(self, axis=None):
        '''Retorna o raio de giração do polígono ao quadrado'''

        return ROG_sqr(self, axis)


class Circuit(CircuitBase):

    '''Circuit is a closed path with a well defined inside.

    Differently from polygons, circuits allows for lines crossing each other'''


class mCircuit(CircuitBase):

    '''A mutable polygon'''


###############################################################################
# Simple polygons
###############################################################################
class PolyBase(CircuitBase):

    '''Base class for Poly and mPoly'''
    __slots__ = []

    def is_simple(self):
        True


class Poly(PolyBase, Circuit):

    '''Generic polygon class.

    The sides of a simple polygon never cross each other'''


class mPoly(PolyBase, mCircuit):

    '''A mutable simple polygon'''


###############################################################################
# Convex polygons
###############################################################################
class ConvexPolyBase(PolyBase):

    '''Base class for ConvexPoly and mConvexPoly'''
    __slots__ = []

    def is_convex(self):
        True


class ConvexPoly(ConvexPolyBase, Poly):

    '''A convex polygon'''


class mConvexPoly(ConvexPolyBase, mPoly):

    '''A mutable convex polygon'''


###############################################################################
# Regular polygons
###############################################################################
class RegularPolyBase(ConvexPolyBase):

    '''Base class for RegularPoly and mRegularPoly'''

    __slots__ = []

    def __init__(self, N, length, theta=None, pos=None):
        alpha = pi / N
        R = RotMat2(2 * alpha)
        p = Vec2(length / (2 * sin(alpha)), 0)
        vertices = []
        for _ in range(N):
            vertices.append(p)
            p = R * p
        super(RegularPolyBase, self).__init__(vertices)

        # Altera posição e ângulo
        if pos is not None:
            self += pos
        if theta is not None:
            self.rotate(theta)


class RegularPoly(RegularPolyBase, ConvexPoly):

    '''A regular polygon with N sides'''


class mRegularPoly(RegularPolyBase, mConvexPoly):

    '''A mutable regular polygon'''


###############################################################################
# Specific geometric shapes
###############################################################################
class TriangleBase(ConvexPolyBase):

    '''Base class for Triangle and mTriangle'''
    __slots__ = []


class Triangle(TriangleBase, ConvexPoly):

    '''A generic triangle'''


class mTriangle(TriangleBase, mConvexPoly):

    '''A mutable triangle'''


class RectangleBase(ConvexPolyBase):

    '''Base class for Rectangle and mRectangle'''

    def __init__(self, *args, **kwds):
        theta = kwds.pop('theta', 0.0)
        self.theta = 0.0
        xmin, xmax, ymin, ymax = aabb_bbox(*args, **kwds)
        vertices = [(xmax, ymin), (xmax, ymax), (xmin, ymax), (xmin, ymin)]
        super(RectangleBase, self).__init__(vertices)
        if theta:
            self.rotate(theta)


class Rectangle(RectangleBase, ConvexPoly):

    '''A rectangle'''


class mRectangle(RectangleBase, mConvexPoly):

    '''A mutable rectangle'''


###############################################################################
# Utility functions
###############################################################################
def _w_list(L):
    '''Calcula os termos W0 = 1/2 * (y1*x0 - y0*x1) de todos os pontos da
    lista'''

    N = len(L)
    out = []
    for i in range(N):
        x1, y1 = L[(i + 1) % N]
        x0, y0 = L[i]
        out.append(0.5 * (y1 * x0 - y0 * x1))
    return out


def area(L):
    '''Calcula a área do polígono definido por uma lista de pontos.

    A lista de pontos deve rodar no sentido anti-horário. Caso contrário, o
    resultado da área será negativo.

    >>> pontos = [(0, 0), (1, 0), (1, 2), (0, 1)]
    >>> area(pontos)
    1.5
    '''

    return sum(_w_list(L))


def center_of_mass(L):
    '''Calcula o vetor centro de massa de um polígono definido por uma lista de
    pontos.

    >>> pontos = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> center_of_mass(pontos)
    Vec2(0.5, 0.5)
    '''

    W = _w_list(L)
    A = sum(W)
    N = len(L)
    x_cm = 0
    y_cm = 0
    for i in range(N):
        x1, y1 = L[(i + 1) % N]
        x0, y0 = L[i]
        wi = W[i]
        x_cm += (x1 + x0) * wi / 3.0
        y_cm += (y1 + y0) * wi / 3.0
    x_cm /= A
    y_cm /= A
    return Vec2(x_cm, y_cm)


def ROG_sqr(L, axis=None):
    '''Calcula o quadrado do raio de giração. O raio de giração é uma grandeza
    geométrica definida como o momento de inércia de um objeto com densidade
    igual a 1.

    >>> pontos = [(0, 0), (2, 0), (2, 2), (0, 2)]

    Se o eixo axis não for determinado, assume o centro de massa (no caso de
    um quadrado, o raio de giração ao quadrado é igual a L**2/6)

    >>> ROG_sqr(pontos)                             # doctest: +ELLIPSIS
    0.666...

    Outro eixo pode ser determinado. Por exemplo, em torno da origem temos
    I=2*M*L**2/3

    >>> ROG_sqr(pontos, axis=(0, 0))                # doctest: +ELLIPSIS
    2.666...
    '''

    W = _w_list(L)
    A = sum(W)
    N = len(L)
    ROG2_orig = 0
    for i in range(N):
        x1, y1 = L[(i + 1) % N]
        x0, y0 = L[i]
        ROG2_orig += ((x1 + x0) ** 2 - x1 * x0 + (y1 + y0)
                      ** 2 - y1 * y0) * W[i] / 6
    ROG2_orig /= A

    # Usa o teorema dos eixos paralelos para determinar o momento em torno
    # do centro de massa
    cm = center_of_mass(L)
    ROG2_cm = ROG2_orig - (cm.x ** 2 + cm.y ** 2)
    if axis is None:
        return ROG2_cm
    else:
        # Usa o teorema dos eixos paralelos novamente para deslocar para o
        # outro eixo
        D = (cm - axis)
        return ROG2_cm + (D.x ** 2 + D.y ** 2)


def clip(poly1, poly2):
    '''Sutherland-Hodgman polygon clipping'''

    def inside(pt):
        '''Retorna verdadeiro se o ponto estiver dentro do polígono 2'''
        pt_rel = pt - r0
        return T.x * pt_rel.y >= T.y * pt_rel.x

    def intercept_point():
        '''Retorna o ponto de intercepção entre os segmentos formados por
        r1-r0 e v1-v0'''

        A = r0.x * r1.y - r0.y * r1.x
        B = v0.x * v1.y - v0.y * v1.x
        C = 1.0 / (T.x * T_.y - T.y * T_.x)
        return Vec2((-A * T_.x + B * T.x) * C, (-A * T_.y + B * T.y) * C)

    out = list(poly1)
    r0 = poly2[-1]

    # Itera sobre todas as linhas definidas pelos lados do polígono 2
    for r1 in poly2:
        if not out:
            raise ValueError('no superposition detected')

        T = r1 - r0
        points, out = out, []
        v0 = points[-1]
        v0_inside = inside(v0)

        # Em cada linha, itera sobre todos os pontos do polígono de saída
        # (inicialmente, o polígono 1)
        for v1 in points:
            T_ = v1 - v0

            # Um vértice dentro e outro fora ==> cria ponto intermediário
            # Dois vértices dentro ==> copia para a lista de saída
            # Dois vértices fora ==> abandona o ponto anterior
            v1_inside = inside(v1)
            if (v1_inside + v0_inside) == 1:
                out.append(intercept_point())
            if v1_inside:
                out.append(v1)

            # Atualiza ponto anterior
            v0 = v1
            v0_inside = v1_inside

        # Atualiza ponto inicial da face
        r0 = r1
    return(out)


def convex_hull(points):
    '''Retorna a envoltória convexa do conjunto de pontos fornecidos.

    Implementa o algorítimo da cadeia monótona de Andrew, O(n log n)

    Exemplo
    -------

    >>> convex_hull([(0, 0), (1, 1), (1, 0), (0, 1), (0.5, 0.5)])
    [Vec2(0, 0), Vec2(1, 0), Vec2(1, 1), Vec2(0, 1)]
    '''

    # Ordena os pontos pela coordenada x, depois pela coordenada y
    points = sorted(set(map(tuple, points)))
    points = [Vec2(*pt) for pt in points]
    if len(points) <= 1:
        return points

    # Cria a lista L: lista com os vértices da parte inferior da envoltória
    #
    # Algoritimo: acrescenta os pontos de points em L e a cada novo ponto
    # remove o último caso não faça uma volta na direção anti-horária
    L = []
    for p in points:
        while len(L) >= 2 and (L[-1] - L[-2]).cross(p - L[-2]) <= 0:
            L.pop()
        L.append(p)

    # Cria a lista U: vértices da parte superior
    # Semelhante à anterior, mas itera sobre os pontos na ordem inversa
    U = []
    for p in reversed(points):
        while len(U) >= 2 and (U[-1] - U[-2]).cross(p - U[-2]) <= 0:
            U.pop()
        U.append(p)

    # Remove o último ponto de cada lista, pois ele se repete na outra
    return L[:-1] + U[:-1]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
