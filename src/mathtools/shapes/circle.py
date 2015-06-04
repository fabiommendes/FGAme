# -*- coding: utf8 -*-
from mathtools import dot, Vec2, pi


class Circle(object):

    '''Representa um círculo com raio e centro dados.

    Exemplos
    --------

    >>> C = Circle(50, (50, 0))
    '''

    __slots__ = ['radius', 'pos']

    def __init__(self, radius, pos=(0, 0)):
        self.radius = radius
        self.pos = Vec2(*pos)

    def __repr__(self):
        s_center = '%.1f, %.1f' % self.center
        return 'Circle(%.1f, (%s))' % (self.radius, s_center)

    def area(self):
        return pi * self.radius * self.radius

    def ROG_sqr(self):
        return self.radius * self.radius / 2

    def ROG(self):
        return self.radius / sqrt(2)

    # Métodos utilizado pelo SAT ##############################################
    def directions(self, n):
        '''Retorna a lista de direções exaustivas para o teste do SAT
        associadas ao objeto.

        A rigor esta lista é infinita para um círculo. Retornamos uma lista
        vazia de forma que somente as direções do outro objeto serão
        consideradas'''

        return []

    def shadow(self, n):
        '''Retorna as coordenadas da sombra na direção n dada.
        Assume n normalizado.'''

        p0 = dot(self.pos, n)
        r = self.radius
        return (p0 - r, p0 + r)

    # Cálculo de distâncias ###################################################
    def distance_center(self, other):
        '''Retorna a distância entre centros de dois círculos.'''

        pass

    def distance_circle(self, other):
        '''Retorna a distância para um outro círculo. Zero se eles se
        interceptam'''

        pass

    # Pontos de interceptação #################################################
    def intersects_circle(self, other):
        '''Retorna True se o círculo intercepta outro círculo ou False, caso
        contrário'''

    def intersects_point(self, point, tol=1e-6):
        '''Retorna True se o ponto está na fronteira do círculo dada a margem
        de tolerância tol.'''

        pass

    # Contêm ou não figuras geométricas #######################################
    def contains_circle(self, other):
        '''Retorna True se o círculo intecepta outro círculo ou False, caso
        contrário'''

    def contains_point(self, point):
        '''Retorna True se o círculo intecepta outro círculo ou False, caso
        contrário'''

if __name__ == '__main__':
    import doctest
    doctest.testmod()
