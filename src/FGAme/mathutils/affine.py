import operator

__all__ = ['Array']


class Affine(object):

    '''Representa uma transformação afim (transformação linear + translação)
    '''

    def __init__(self, data):
        self._data = list(map(float, data))

    def _new(self, data):
        return self.__class__(data)

    def _isnumber(self, obj):
        return isinstance(obj, (int, float))

    def _aligned(self, obj):
        try:
            if len(obj) != len(self):
                raise ValueError('objects have different lengths')
            else:
                return obj
        except TypeError:
            return self._aligned(list(obj))

    def __repr__(self):
        tname = type(self).__name__
        data = ', '.join(str(x) if x != int(x) else str(int(x)) for x in self)
        return '%s([%s])' % (tname, data)

    def __iter__(self):
        return iter(self._data)

    def __delitem__(self, i):
        del self._data[i]

    def __getitem__(self, i):
        return self[i]

    def __setitem__(self, i, value):
        self.data[i] = float(value)

    def __len__(self):
        return len(self._data)

    def insert(self, idx, value):
        self._data.insert(idx, float(value))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
