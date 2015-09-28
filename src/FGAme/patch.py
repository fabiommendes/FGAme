# -*- coding: utf8 -*-
'''
As funções no módulo patch permitem modificar o comportamento da FGAme de
maneira arbitrária. A maior parte das funções tem o caráter educativo e
permitem que estudantes na área de física para jogos reimplementem
pedaços específucis de um motor de jogo aproveitando o resto da infraestrutura
existente.

As funções neste módulo também servem para testar implementações alternativas
ou experimentais.
'''
from types import MethodType


def set_collision_class(cls):
    '''Define qual é a classe encarregada de resolver colisões no lugar de
    FGAme.physics.Collision.'''

    from FGAme.physics import collision_pairs
    collision_pairs.Collision = cls


def restore_collision_class():
    '''Restaura a classe de colisão para o valor padrão'''

    from FGAme.physics import Collision
    set_collision_class(Collision)


def set_resolve_collision(func):
    '''Decorador que determina qual é a função encarregada de resolver colisões
    entre duas partículas. A função recebe um objeto de colisão como argumento.

        >>> @set_resolve_collision
        ... def resolve(col):
        ...     A, B = col
        ...     print('collision with objects %s and %s' % (A, B))

    Note que é possível invocar a implementação original do método de colisão
    utilizando o método col.resolve().
    '''

    from FGAme.physics import Collision

    class PatchedCollision(Collision):

        def __init__(self, *args, **kwds):
            try:
                super(PatchedCollision, self).__init__(*args, **kwds)
            except AssertionError:
                pass

        def resolve(self):
            try:
                self.resolve = MethodType(Collision.resolve, self)
                func(self)
            finally:
                del self.resolve

    set_collision_class(PatchedCollision)


def restore_defaults():
    '''Restaura a FGAme para o comportamento padrão'''

    restore_collision_class()
