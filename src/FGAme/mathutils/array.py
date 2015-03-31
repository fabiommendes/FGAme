from collections import MutableSequence
import operator
from FGAme.mathutils.arithmetic import mAbstractArray, mArithmetic

__all__ = ['Array']


class Array(mAbstractArray, mArithmetic, MutableSequence):

    '''Uma lista unidimensional de números que aceita operações matemáticas.

    Exemplos
    --------

    >>> a = Array([1, 2, 3, 4])
    >>> a
    Array([1, 2, 3, 4])

    Arrays aceitam métodos de listas

    >>> a.append(5)
    >>> a
    Array([1, 2, 3, 4, 5])

    Mas também aceitam operações matemáticas

    >>> a + 1
    Array([2, 3, 4, 5, 6])
    >>> a + [1, 0, 1, 0, 1]
    Array([2, 2, 4, 4, 6])

    Array são objetos mutáveis, de forma que operações inplace modificam os
    dados originais

    >>> b = a
    >>> a += 1
    >>> b
    Array([2, 3, 4, 5, 6])
    '''

    _out_transform = None
    _in_transform = float
    _scalar = (float, int)
    _container = (list, tuple)

    def __init__(self, data):
        self._data = list(map(float, data))

    def __repr__(self):
        tname = type(self).__name__
        data = ', '.join(str(x) if x != int(x) else str(int(x)) for x in self)
        return '%s([%s])' % (tname, data)

    def insert(self, idx, value):
        self._insert(idx, value)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    from nose import runmodule
    from FGAme.mathutils.unittests import aUnittest, TestCase

    class ArrayTester(aUnittest, TestCase):
        test_type = Array
        str_equality = True

        def names(self):
            new = self.test_type
            a = new([0, 1, 2])
            b = new([3, 4, 5])
            m = 2
            a_tuple = (0, 1, 2)
            a_list = [0, 1, 2]

            add_ab = new([3, 5, 7])
            mul_ab = new([0, 4, 10])
            sub_ab = new([-3, -3, -3])
            sub_ba = new([3, 3, 3])

            add_am = new([2, 3, 4])
            mul_am = new([0, 2, 4])
            div_am = new([0, 0.5, 1])
            div_mb = new([2 / 3., 0.5, 2. / 5])
            sub_am = new([-2, -1, 0])
            sub_ma = new([2, 1, 0])

            return locals()

    runmodule('__main__')
