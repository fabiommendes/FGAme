#-*- coding: utf8 -*-
#===============================================================================
# Objetos desenháveis
#===============================================================================
class Drawable(object):
    '''Classe pai para todos os objetos que podem ser desenhados na tela'''

    # Constantes da classe -----------------------------------------------------
    __slots__ = []

    # Funções que modificam o objeto selecionado -------------------------------
    def scale(self, value):
        raise NotImplementedError

    def rotate(self, theta, axis=None):
#        if axis is None:
#            if theta:
#                raise NotImplementedError
#        else:
#            delta = self._pos - axis
#            self.rotate(theta)
#            self.move(delta.rotated(theta))
        pass

    def move(self, delta):
#        if delta[0] or delta[1]:
#            self._pos += delta
#            self._cache = None
        pass

    # Copia objetos e retorna versões transformadas dos mesmos -----------------
    def copy(self):
        '''Retorna uma cópia do objeto'''
        cls = type(self)
        new = object.__new__(cls)
        new.__dict__.update(self.__dict__)
        return new

    def scaled(self, value):
        '''Retorna uma versão modificada por um fator de escala igual a `value`'''
        new = self.copy()
        new.scale(value)
        return new

    def rotated(self, theta, axis=None):
        '''Retorna uma cópia do objeto rotacionada pelo ângulo fornecido em 
        torno do eixo fornecido (ou o centro do objeto)'''
        new = self.copy()
        new.rotate(theta, axis)
        return new

    def moved(self, delta):
        '''Retorna uma cópia do objeto deslocada por um fator delta'''
        new = self.copy()
        new.move(delta)
        return new

class Group(Drawable):
    def __init__(self, members):
        self.members = list(members)

    def add(self, member):
        self.members.append(member)

    def rotate(self, theta, axis=None):
        super(Group, self).rotate(theta, axis)
        for member in self.members:
            member.rotate(theta, member.pos)

    def scale(self, scale):
        if scale != 1:
            super(Group, self).scale(scale)
            for member in self.members:
                member.scale(scale)
                if member.pos[0] or member.pos[1]:
                    member.move((scale - 1) * member._pos)

    def as_poly(self):
        return TypeError

    def as_vertices(self, relative=False, scaled=True):
        raise TypeError
