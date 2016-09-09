from warnings import warn
from generic import generic
from FGAme.mathtools import Vec2, dot, ux2D
from FGAme.mathtools import shadow_x, shadow_y, area, center_of_mass, clip, pi
from FGAme.physics import Collision
from FGAme.physics import Circle, AABB, Poly, Rectangle

DEFAULT_DIRECTIONS = [ux2D.rotated(n * pi / 12) for n in
                      [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11]]


class CollisionError(Exception):

    '''Declara que não existem colisões disponíveis para os dois tipos de
    objetos'''


@generic
def get_collision(A, B):
    '''Retorna um objeto de colisão caso ocorra uma colisão com o objeto
    other. Caso não haja colisão, retorna None.

    Esta função é implementada por multidispatch. As classes derivadas de
    PhysicsObject devem registrar explicitamente a colisão entre todos os pares
    suportados (ex.: Circle com Circle, Circle com AABB, etc). Caso não tenha
    nenhuma implementação registrada, então utiliza-se a lógica de AABB's.'''

    tA = type(A).__name__
    tB = type(B).__name__
    warn('no collision defined for: (%s, %s)' % (tA, tB))

    return collision_circle(A, B)


#
# Colisões entre objetos do mesmo tipo
#
@get_collision.overload([Circle, Circle])
def collision_circle(A, B):
    '''Testa a colisão pela distância dos centros'''

    rA = A.cbb_radius
    rB = B.cbb_radius
    normal = B.pos - A.pos
    distance = normal.norm()

    if distance < rA + rB:
        normal /= distance
        delta = rA + rB - distance
        pos = A.pos + (rA - delta / 2) * normal
        return Collision(A, B, pos=pos, normal=normal, delta=delta)
    else:
        return None


@get_collision.overload([AABB, AABB])
def collision_aabb(A, B):
    '''Retorna uma colisão com o objeto other considerando apenas a caixas
    de contorno alinhadas ao eixo.'''

    # Detecta colisão pelas sombras das caixas de contorno
    x0, x1 = max(A.xmin, B.xmin), min(A.xmax, B.xmax)
    y0, y1 = max(A.ymin, B.ymin), min(A.ymax, B.ymax)
    dx = x1 - x0
    dy = y1 - y0
    if x1 < x0 or y1 < y0:
        return None
    
    # Elege o centro da aabb de interseção como o ponto de colisão
    pos = Vec2((x1 + x0) / 2, (y1 + y0) / 2)

    # Escolhe a direção da menor superposição e a normal
    if dy < dx:
        delta = dy
        normal = Vec2(0, (1 if A.pos.y < B.pos.y else -1))
    else:
        delta = dx
        normal = Vec2((1 if A.pos.x < B.pos.x else -1), 0) 
    
    return Collision(A, B, pos=pos, normal=normal, delta=delta)


@get_collision.overload([Poly, Poly])
def collision_poly(A, B, directions=None):
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
        A_coords = [dot(pt, u) for pt in A.vertices]
        B_coords = [dot(pt, u) for pt in B.vertices]
        Amax, Amin = max(A_coords), min(A_coords)
        Bmax, Bmin = max(B_coords), min(B_coords)
        minmax, maxmin = min(Amax, Bmax), max(Amin, Bmin)
        shadow = minmax - maxmin
        if shadow < 0:
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
    # não houve superposição (talvez por usar normais aproximadas)
    except ValueError:
        return None

    if area(clipped) == 0:
        return None
    col_pt = center_of_mass(clipped)
 
    return Collision(A, B, pos=col_pt, normal=norm, delta=min_shadow)


#
# Colisões entre objetos de tipos diferentes
#
@get_collision.overload([AABB, Poly])
def aabb_poly(A, B):
    '''Implementa a colisão entre um polígono arbitrário e uma caixa AABB'''

    if shadow_x(A, B) < 0 or shadow_y(A, B) < 0:
        return None

    A_poly = Rectangle(bbox=A.bbox)
    col = collision_poly(A_poly, B)
    if col is not None:
        return Collision(A, B, pos=col.pos, normal=col.normal, delta=col.delta)
    else:
        return None


@get_collision.overload([Circle, Poly])
def circle_poly(A, B):
    '''Implementa a colisão entre um círculo arbitrário um polígono.
    
    A normal resultante sempre sai do círculo na direção do polígono.
    '''
    
    # Verifica as AABB
    if shadow_x(A, B) < 0 or shadow_y(A, B) < 0:
        return None

    # Procura o ponto mais próximo de B
    vertices = B.vertices
    center = A.pos
    normals = [(i, v - center, v) for i, v in enumerate(vertices)]
    idx, _, pos = min(normals, key=lambda x: x[1].norm())
    
    # A menor distância para o centro pode ser do tipo vértice-ponto ou 
    # aresta-ponto. Assumimos o vértice inicialmente.
    separation = (pos - center).norm()
    
    # Agora verificamos cada face
    P0 = pos
    N = len(vertices)
    for idx in [(idx - 1) % N, (idx + 1) % N]:
        P = vertices[idx]
        v = center - P
        u = P0 - P
        L = u.norm()
        distance = abs(v.cross(u) / L)
        
        # Verifica se o ponto mais próximo se encontra no segmento
        if distance < separation and u.dot(v) < L**2:
            pos = P + (u.dot(v) / L**2) * u
            separation = distance
        
    # Verificamos se houve colisão na direção de menor separação
    delta = A.radius - separation
    normal = (pos - center).normalized()
    
    if delta > 0:
        return Collision(A, B, pos=pos, normal=normal, delta=delta)
    else:
        return None
    

@get_collision.overload([Circle, AABB])
def circle_aabb(A, B):
    '''Reutiliza a lógica de Circle/Poly para realizar a colisão com AABBs'''
    
    if shadow_x(A, B) < 0 or shadow_y(A, B) < 0:
        return None
    
    B_poly = Rectangle(bbox=B.bbox)
    col = circle_poly(A, B_poly)
    if col is not None:
        return Collision(A, B, pos=col.pos, normal=col.normal, delta=col.delta)
    else:
        return None


#
# Colisões recíprocas
#
@get_collision.overload([Poly, Circle])
def poly_circle(A, B):
    return circle_poly(B, A)

@get_collision.overload([Poly, AABB])
def poly_aabb(A, B):
    return aabb_poly(B, A)

@get_collision.overload([AABB, Circle])
def aabb_circle(A, B):
    return circle_aabb(B, A)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
