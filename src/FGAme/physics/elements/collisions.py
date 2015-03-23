from FGAme.mathutils import Vector, dot, area, center_of_mass, clip, pi

from FGAme.physics.collision import (
    Collision, get_collision, get_collision_aabb
)
from FGAme.physics.elements import (
    PhysCircle, PhysAABB, PhysPoly, PhysRectangle
)

u_x = Vector(1, 0)
DEFAULT_DIRECTIONS = [u_x.rotated(n * pi / 12) for n in
                      [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11]]


###############################################################################
# Colisões entre figuras primitivas simples
###############################################################################

get_collision[PhysAABB, PhysAABB] = get_collision_aabb


@get_collision.dispatch(PhysCircle, PhysCircle)
def circle_collision(A, B):
    '''Testa a colisão pela distância dos centros'''

    delta = B.pos - A.pos
    if delta.norm() < A.radius + B.radius:
        n = delta.normalized()
        D = A.radius + B.radius - delta.norm()
        pos = A.pos + (A.radius - D / 2) * n
        return Collision(A, B, pos=pos, n=n)
    else:
        return None

###############################################################################
# Colisões de polígonos
###############################################################################


@get_collision.dispatch(PhysPoly, PhysPoly)
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
        A_coords = [round(dot(pt, u), 6) for pt in A.vertices]
        B_coords = [round(dot(pt, u), 6) for pt in B.vertices]
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
    return Collision(A, B, col_pt, norm, min_shadow)


@get_collision.dispatch(PhysPoly, PhysAABB)
def get_collision_poly_aabb(A, B):
    '''Implementa a colisão entre um polígono arbitrário e uma caixa AABB'''

    B_poly = PhysRectangle(bbox=B.bbox, density=B.density)
    col = get_collision_poly(A, B_poly)
    if col is not None:
        col.objects = (A, B)
        return col


@get_collision.dispatch(PhysAABB, PhysPoly)
def get_collision_aabb_poly(A, B):
    '''Implementa a colisão entre um polígono arbitrário e uma caixa AABB'''

    A_poly = PhysRectangle(bbox=A.bbox, density=A.density)
    col = get_collision_poly(A_poly, B)
    if col is not None:
        col.objects = (A, B)
        return col
