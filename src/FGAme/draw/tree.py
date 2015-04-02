# -*- coding: utf8 -*-


class RenderTree(object):

    '''Representa uma árvore de objetos que serão desenhados na tela'''

    is_tree = True

    def __init__(self, parent=None):
        self._data = []
        self.parent = None

    def add(self, obj, layer=0):
        '''Adiciona um objeto ou um galho (outro elemento de RenderTree) na
        camada especificada'''

        for i, (layer_idx, data) in enumerate(list(self._data)):
            if layer == layer_idx:
                data.append(obj)
            elif layer < layer_idx:
                self._data.insert(i, (layer, [obj]))
                break
        else:
            self._data.append((layer, [obj]))

    # TODO: Mover objetos entre Layers ou modifica a ordem do objeto dentro de
    # um layer

    # Iteradores -------------------------------------------------------------
    def walk(self, reverse=False):
        '''Percorre sobre todos os objetos na ordem correta. Se reverse=True,
        percorre os objetos na ordem contrária.'''

        if reverse:
            for _, L in reversed(self._data):
                for obj in reversed(L):
                    yield obj
        else:
            for _, L in self._data:
                for obj in L:
                    yield obj

    def iter_layers(self, skip_empty=False):
        '''Itera sobre as camadas'''

        if skip_empty:
            for (_, L) in self._data:
                yield L

        else:
            idx = self._data[0][0]
            for i, L in self._data:
                if i == idx:
                    idx += 1
                    yield L
                else:
                    while idx < i:
                        idx += 1
                        yield []

    def get_layer(self, idx):
        '''Retorna uma lista com os objetos da i-ésima camada'''

        for i, L in self._data:
            if i == idx:
                return L
        else:
            return []

    def update(self, dt):
        for obj in self.walk():
            obj.update(dt)


###############################################################################
#                     Grupos e composições de objetos
###############################################################################
# TODO: fundir com RenderTree e colocar RenderTree na hierarquia de drawable
