# -*- coding: utf8 -*-


class RenderTree(object):

    '''Representa uma árvore de objetos que serão desenhados na tela

    Exemplos
    --------

    Inicializamos a árvore com alguns objetos. A string 'foo' foi colocado em
    uma camada superior e portanto será renderizada por último

    >>> tree = RenderTree()
    >>> tree.add('foo', 1)
    >>> tree.add('bar')
    >>> tree.add('blaz')

    Podemos navegar na árvore utilizando o iterador `walk()`

    >>> list(tree.walk())
    ['bar', 'blaz', 'foo']

    O método remove() permite remover objetos

    >>> tree.remove('bar');
    >>> 'bar' in tree, 'foo' in tree
    (False, True)
    '''

    is_tree = True

    def __init__(self, parent=None):
        self._data = []
        self.parent = None

    # Métodos mágicos #########################################################
    def __contains__(self, obj):
        return any(obj in L for _, L in self._data)

    def __iter__(self):
        return self.walk()

    # Controle de objetos #####################################################
    def add(self, obj, layer=0):
        '''Adiciona um objeto ou um galho (outro elemento de RenderTree) na
        camada especificada'''

        for i, (layer_idx, data) in enumerate(list(self._data)):
            if layer == layer_idx:
                data.append(obj)
                break
            elif layer < layer_idx:
                self._data.insert(i, (layer, [obj]))
                break
        else:
            self._data.append((layer, [obj]))

    def remove(self, obj):
        '''Remove um objeto da árvore de renderização'''

        for _, L in self._data:
            if obj in L:
                L.remove(obj)
                break
        else:
            raise ValueError('object %r not in RenderTree' % obj)

    # TODO: Mover objetos entre Layers ou modifica a ordem do objeto dentro de
    # um layer

    # Iteradores -------------------------------------------------------------
    def walk(self, reverse=False):
        '''Percorre sobre todos os objetos na ordem correta. Se reverse=True,
        percorre os objetos na ordem contrária.
        '''

        if reverse:
            for _, L in reversed(self._data):
                for obj in reversed(L):
                    yield obj
        else:
            for _, L in self._data:
                for obj in L:
                    yield obj

    def iter_layers(self, skip_empty=True):
        '''Itera sobre as camadas retornando a lista de objetos em cada
        camada'''

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
        '''Percorre todos os objetos na árvore invocando o método update()'''

        for obj in self.walk():
            obj.update(dt)

    def paint(self, screen):
        '''Percorre todos os objetos na árvore invocando o método
        `obj.paint(screen)`'''

        for obj in self.walk():
            obj.paint(screen)

    def linearize(self, layer=0):
        '''Retorna uma versão linearizada da árvore de renderização onde
        todos os objetos são recolocados na mesma camada'''

        data = (layer, list(self.walk()))
        new = RenderTree(parent=self.parent)
        new._data.append(data)
        return new

###############################################################################
#                     Grupos e composições de objetos
###############################################################################
# TODO: fundir com RenderTree e colocar RenderTree na hierarquia de drawable

if __name__ == '__main__':
    import doctest
    doctest.testmod()
