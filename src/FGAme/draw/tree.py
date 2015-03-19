#-*- coding: utf8 -*-
class RenderTree(object):
    '''Representa uma árvore de objetos que serão desenhados na tela'''

    is_tree = True

    def __init__(self, parent=None):
        self._data = [[]]
        self.parent = None

    def add(self, obj, layer=0):
        '''Adiciona um objeto na camada especificada'''

        if layer >= len(self._data):
            for i in range(len(self._data) - layer + 1):
                self._data.append([])
        self._data[layer].append(obj)

    # TODO: Mover objetos entre Layers ou modifica a ordem do objeto dentro de
    # um layer

    # Iteradores ---------------------------------------------------------------
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

    def get_layer(self, i):
        '''Retorna uma lista com os objetos da i-ésima camada'''

        return self._data[idx]
