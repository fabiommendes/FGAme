# -*- coding: utf8 -*-


class RenderTree(object):

    '''Representa uma árvore de objetos que serão desenhados na tela'''

    is_tree = True

    def __init__(self, parent=None):
        self._data = [[]]
        self.parent = None

    def add(self, obj, layer=0):
        '''Adiciona um objeto ou um galho (outro elemento de RenderTree) na
        camada especificada'''

        if layer >= len(self._data):
            for _ in range(len(self._data) - layer + 1):
                self._data.append([])
        self._data[layer].append(obj)

    # TODO: Mover objetos entre Layers ou modifica a ordem do objeto dentro de
    # um layer

    # Iteradores -------------------------------------------------------------
    def walk(self, reverse=False):
        '''Percorre sobre todos os objetos na ordem correta. Se reverse=True,
        percorre os objetos na ordem contrária.'''

        if reverse:
            for L in reversed(self._data):
                for obj in reversed(L):
                    yield obj
        else:
            for L in self._data:
                for obj in L:
                    yield obj

    def iter_layers(self):
        '''Itera sobre as camadas'''

        return iter(self._data)

    def get_layer(self, idx):
        '''Retorna uma lista com os objetos da i-ésima camada'''

        return self._data[idx]

    def update(self, dt):
        for obj in self.walk():
            obj.update(dt)


###############################################################################
#                     Grupos e composições de objetos
###############################################################################
# TODO: fundir com RenderTree e colocar RenderTree na hierarquia de drawable

class Group(object):

    '''Define um grupo de objetos desenháveis'''

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
