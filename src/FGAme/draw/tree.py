class RenderTree(object):
    """Representa uma árvore de objetos que serão desenhados na tela

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
    """

    is_tree = True
    visible = True

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def __init__(self, parent=None):
        self._data = []
        self.parent = None

    def __contains__(self, obj):
        return any(obj in L for _, L in self._data)

    def __iter__(self):
        return self.walk()

    def __len__(self):
        return sum(len(layer) for layer in self._data)

    def __getitem__(self, idx):
        for i, obj in enumerate(self):
            if i == idx:
                return obj
        raise IndexError(idx)

    def add(self, obj, layer=0):
        """Adiciona um objeto ou um galho (outro elemento de RenderTree) na
        camada especificada"""

        for i, (layer_idx, data) in enumerate(list(self._data)):
            if layer == layer_idx:
                data.append(obj)
                break
            elif layer < layer_idx:
                self._data.insert(i, (layer, [obj]))
                break
        else:
            self._data.append((layer, [obj]))

    def remove(self, value):
        """Remove a primeira ocorrência de um valor."""

        for _, L in self._data:
            if value in L:
                L.remove(value)
                break
        else:
            raise ValueError('object %r not in RenderTree' % value)

    def remove_all(self, value):
        """Remove todas as ocorrências do valor dado."""

        for _, L in self._data:
            while value in L:
                L.remove(value)

    def count(self, value):
        """Count the number of occurrences of the given value"""

        count = 0
        for obj in self.walk():
            count += bool(obj == value)
        return count

    def walk(self, reverse=False):
        """Percorre sobre todos os objetos na ordem correta. Se reverse=True,
        percorre os objetos na ordem contrária.
        """

        if reverse:
            for _, L in reversed(self._data):
                for obj in reversed(L):
                    yield obj
        else:
            for _, L in self._data:
                for obj in L:
                    yield obj

    def iter_layers(self, skip_empty=True):
        """Itera sobre as camadas retornando a lista de objetos em cada
        camada"""

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
        """Retorna uma lista com os objetos da i-ésima camada"""

        for i, L in self._data:
            if i == idx:
                return L
        else:
            return []

    def screen_update(self, screen):
        """Percorre todos os objetos na árvore invocando o método 
        screen_update() o parâmetro de screen fornecido"""

        for obj in self.walk():
            drawable = obj.drawable
            try:
                handle = drawable.screen_handle
            except AttributeError:
                handle = drawable.screen_handle = screen.get_handle(drawable)
            screen.update_handle(handle, drawable)

    def draw(self, painter):
        """Percorre todos os objetos na árvore invocando o método
        `obj.paint(screen)`"""

        for obj in self.walk():
            if obj.visible:
                try:
                    obj.draw(painter)
                except Exception:
                    print('debug: error drawing %s' % obj)
                    raise

    def linearize(self, layer=0):
        """Retorna uma versão linearizada da árvore de renderização onde
        todos os objetos são recolocados na mesma camada"""

        data = (layer, list(self.walk()))
        new = RenderTree(parent=self.parent)
        new._data.append(data)
        return new


if __name__ == '__main__':
    import doctest

    doctest.testmod()
