#-*- coding: utf8 -*-

from FGAme.physics import Object, AABB, Collision, get_collision
from FGAme.draw import PolyEcho
from FGAme.mathutils import Vector, VectorM, dot, cross
from FGAme.mathutils import area, center_of_mass, ROG_sqr
from FGAme.mathutils import sin, cos, pi
from FGAme.mathutils import clip
from FGAme.util import lazy

class Poly(Object):
    '''Define um polígono arbitrário de N lados.'''

    def __init__(self, vertices, pos=None, **kwds):
        if pos is not None:
            raise TypeError('cannot define pos for polygonal shapes')

        self.vertices = [VectorM(*pt) for pt in vertices]
        self._xmin = min(pt.x for pt in self.vertices)
        self._xmax = max(pt.x for pt in self.vertices)
        self._ymin = min(pt.y for pt in self.vertices)
        self._ymax = max(pt.y for pt in self.vertices)
        super(Poly, self).__init__(pos=center_of_mass(self.vertices), **kwds)
        self.num_sides = len(self.vertices)
        self._normals_idxs = self.get_li_indexes()
        self.num_normals = len(self._normals_idxs or self.vertices)

        # Aceleramos um pouco o cálculo para o caso onde todas as normais são LI.
        # entre si. Isto é sinalizado por self._normals_idx = None, que implica
        # que todas as normais do polígono devem ser recalculadas a cada frame
        if self.num_normals == self.num_sides:
            self._normals_idxs = None


    #===========================================================================
    # Construtores alternativos
    #===========================================================================
    @classmethod
    def regular(cls, N, length, pos=(0, 0), **kwds):
        '''Cria um polígono regoular com N lados de tamanho "length".'''

        alpha = pi / N
        theta = 2 * alpha
        b = length / (2 * sin(alpha))
        P0 = Vector(b, 0)
        points = [ (P0.rotated(n * theta)) for n in range(N) ]

        new = Poly(points, **kwds)
        new.pos = pos
        return new

    @classmethod
    def rect(cls, bbox=None, shape=None, pos=None, centered=False, **kwds):
        '''Cria um retângulo especificando ou a caixa de contorno ou a posição 
        do centro de massa e a forma.'''

        if bbox:
            xmin, xmax, ymin, ymax = bbox
            if pos is not None:
                raise TypeError('cannot set bbox and pos simultaneously')
            points = [ (xmax, ymin), (xmax, ymax), (xmin, ymax), (xmin, ymin) ]

            return Poly(points, **kwds)

        elif shape:
            x, y = pos or (0, 0)
            dx, dy = shape
            if centered:
                xmin, xmax = x - dx / 2., x + dx / 2.
                ymin, ymax = y - dy / 2., y + dy / 2.
            else:
                xmin, xmax = x, x + dx
                ymin, ymax = y, y + dy
            bbox = (xmin, xmax, ymin, ymax)
            return Poly.rect(bbox=bbox, **kwds)

        else:
            raise TypeError('either shape or bbox must be defined')

    @classmethod
    def triangle(cls, sides, pos=(0, 0), **kwds):
        '''Cria um triângulo especificando o tamanho dos lados'''
        pass

    @classmethod
    def blob(cls, N, scale, pos=(0, 0), **kwds):
        '''Cria um polígono convexo aleatório especificando o número de lados e 
        um fator de escala.'''
        pass

    #===========================================================================
    # Métodos específicos da classe polígono
    #===========================================================================
    def get_li_indexes(self):
        '''Retorna os índices referents às normais linearmente independentes 
        entre si.
        
        Este método é invocado apenas na inicialização do objeto e pode involver
        testes de independencia linear relativamente caros.'''

        normals = [ self.get_normal(i).normalized() for i in range(self.num_sides) ]
        LI = []
        LI_idx = []
        for idx, n in enumerate(normals):
            for n_other in LI:
                # Produto vetorial nulo ==> dependência linear
                if abs(cross(n, n_other)) < 1e-3:
                    break
            else:
                # Executado se o loop "for" não terminar em um break
                # Implica em independência linear
                LI.append(n)
                LI_idx.append(idx)
        return LI_idx

    def get_side(self, i):
        '''Retorna um vetor na direção do i-ésimo lado do polígno. Cada segmento 
        é definido pela diferença entre o (i+1)-ésimo ponto e o i-ésimo ponto.'''

        points = self.vertices
        return points[(i + 1) % self.num_sides] - points[i]

    def get_normal(self, i):
        '''Retorna a normal unitária associada ao i-ésimo segmento. Cada segmento 
        é definido pela diferença entre o (i+1)-ésimo ponto e o i-ésimo ponto.'''

        points = self.vertices
        x, y = points[(i + 1) % self.num_sides] - points[i]
        return Vector(y, -x).normalized()

    def get_normals(self):
        '''Retorna uma lista com as normais linearmente independentes.'''

        if self._normals_idxs is None:
            N = self.num_sides
            points = self.vertices
            segmentos = (points[(i + 1) % N] - points[i] for i in range(N))
            return [ Vector(y, -x).normalized() for (x, y) in segmentos ]
        else:
            return [ self.get_normal(i) for i in self._normals_idxs ]

    def is_internal_point(self, pt):
        '''Retorna True se um ponto for interno ao polígono.'''

        n = self.get_normal
        P = self.vertices
        return all(dot(pt - P[i], n(i)) <= 0 for i in range(self.num_sides))

    #===========================================================================
    # Sobrescrita de PhysicsObject
    #===========================================================================
    def get_primitive_drawable(self, color='black', solid=True, lw=0):
        
        return PolyEcho(self, color, solid, lw)

    def move(self, delta):
        super(Poly, self).move(delta)
        for v in self.vertices:
            v += delta

    def rotate(self, theta):
        super(Poly, self).rotate(theta)

        # Realiza a matriz de rotação manualmente para melhor performance
        cos_t, sin_t = cos(theta), sin(theta)
        X, Y = self._pos
        for v in self.vertices:
            x = v.x - X
            y = v.y - Y
            v.x = cos_t * x - sin_t * y + X
            v.y = cos_t * y + sin_t * x + Y

        self._xmin = min(pt.x for pt in self.vertices)
        self._xmax = max(pt.x for pt in self.vertices)
        self._ymin = min(pt.y for pt in self.vertices)
        self._ymax = max(pt.y for pt in self.vertices)

    def scale(self, scale, update_physics=False):
        # Atualiza os pontos
        Rcm = self.pos
        for v in self.vertices:
            v -= Rcm
            v *= scale
            v += Rcm

        # Atualiza AABB
        X = [ x for (x, _) in self.vertices ]
        Y = [ y for (_, y) in self.vertices ]
        self._xmin, self._xmax = min(X), max(X)
        self._ymin, self._ymax = min(Y), max(Y)

    @property
    def area(self):
        return area(self.vertices)

    @lazy
    def ROG_sqr(self):
        return ROG_sqr(self.vertices)

#===============================================================================
# Implementa colisões
#===============================================================================
u_x = Vector(1, 0)
DEFAULT_DIRECTIONS = [u_x.rotated(n * pi / 12) for n in [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11]]

@get_collision.dispatch(Poly, Poly)
def get_collision_poly(A, B, directions=None):
    '''Implementa a colisão entre dois polígonos arbitrários'''

    # Cria a lista de direções a partir das normais do polígono
    if directions is None:
        if A.num_normals + B.num_normals < 9:
            directions = A.get_normals() + B.get_normals()
        else:
            directions = DEFAULT_DIRECTIONS

    # Testa se há superposição de sombras em todas as direções consideradas
    # e calcula o menor valor para sombra e a direção normal
    min_shadow = float('inf')
    norm = None
    for u in directions:
        A_coords = [ round(dot(pt, u), 6) for pt in A.vertices ]
        B_coords = [ round(dot(pt, u), 6) for pt in B.vertices ]
        Amax, Amin = max(A_coords), min(A_coords)
        Bmax, Bmin = max(B_coords), min(B_coords)
        minmax, maxmin = min(Amax, Bmax), max(Amin, Bmin)
        shadow = minmax - maxmin
        if shadow < 0 :
            return None
        elif shadow < min_shadow:
            min_shadow = shadow
            norm = u

    # Determina o sentido da normal
    if dot(A.pos, norm) > dot(B.pos, norm):
        norm = -norm

    # Computa o polígono de intersecção e usa o seu centro de massa como ponto
    # de colisão
    try:
        clipped = clip(A.vertices, B.vertices)
    except ValueError:  # não houve superposição (talvez por usar normais aproximadas)
        return None

    if area(clipped) == 0:
        return None
    col_pt = center_of_mass(clipped)
    return Collision(A, B, col_pt, norm, min_shadow)

@get_collision.dispatch(Poly, AABB)
def get_collision_poly_aabb(A, B):
    '''Implementa a colisão entre um polígono arbitrário e uma caixa AABB'''

    B_poly = Poly.rect(bbox=B.bbox, density=B.density)
    col = get_collision_poly(A, B_poly)
    if col is not None:
        col.objects = (A, B)
        return col


@get_collision.dispatch(AABB, Poly)
def get_collision_aabb_poly(A, B):
    '''Implementa a colisão entre um polígono arbitrário e uma caixa AABB'''

    A_poly = Poly.rect(bbox=A.bbox, density=A.density)
    col = get_collision_poly(A_poly, B)
    if col is not None:
        col.objects = (A, B)
        return col

if __name__ == '__main__':
    R = Poly.rect(shape=(100, 100))
    print(R.vertices)
    print([ R.get_normal(i) for i in range(4)])
    print([R.get_side(i) for i in range(4)])
    print([R.get_normal(i) for i in range(4)])
