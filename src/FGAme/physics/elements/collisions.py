from FGAme.physics.collision import Collision, get_collision, get_collision_aabb
from FGAme.physics.elements import PhysCircle, PhysAABB

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
