#-*- coding: utf8 -*-
from FGAme.mathutils import pi
from FGAme.physics import get_collision, Object, Collision
from FGAme.util import lazy
from FGAme.draw import CircleEcho

class Circle(Object):
    '''Define um círculo e implementa a detecção de colisão comparando a 
    distância entre os centros com a soma dos raios.'''

    def __init__(self, radius, *args, **kwds):
        world = kwds.pop('world', None)
        self._radius = float(radius)
        super(Circle, self).__init__(*args, **kwds)
        self.radius = self._radius  # recalcula a AABB de acordo com o raio
        if world is not None:
            world.add(self)

    def __repr__(self):
        tname = type(self).__name__
        vel = ', '.join('%.1f' % x for x in self.vel)
        pos = ', '.join('%.1f' % x for x in self.pos)
        return '%s(pos=(%s), vel=(%s), radius=%.1f)' % (tname, pos, vel, self.radius)

    def draw(self, screen):
        '''Desenha objeto na tela'''

        screen.draw_circle(self.pos, self.radius, color=self.color)
        
    def get_primitive_drawable(self, color='black', lw=0, solid=True):
        return CircleEcho(self, color=color, lw=lw, solid=solid)

    @lazy
    def area(self):
        return pi * self._radius ** 2

    @lazy
    def ROG_sqr(self):
        return self._radius ** 2 / 2

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

        # Atualiza a caixa de contorno
        x, y = self._pos
        self._xmin = x - value
        self._xmax = x + value
        self._ymin = y - value
        self._ymax = y + value

    def scale(self, scale, update_physics=False):
        self.radius *= scale
        if update_physics:
            self.mass *= scale ** 2
            self.inertia *= scale ** 2

#===============================================================================
# Implementa colisões
#===============================================================================
@get_collision.dispatch(Circle, Circle)
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


if __name__ == '__main__':
    from doctest import testmod
    testmod()
