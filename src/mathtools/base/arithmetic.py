# -*- coding: utf8 -*-

import operator

identity = lambda x: x


class AbstractArray(object):
    _out_transform = None
    _in_transform = None

    def _new(self, data, copy=True):
        '''Criar novo objeto a partir de uma sequencia data. Sequência expõe
        objetos publicamente visíveis'''

        T = self._in_transform
        new = object.__new__(type(self))
        if T is not None:
            new._data = [T(x) for x in data]
        else:
            new._data = list(data)
        return new

    def _new_raw(self, data, copy=True):
        '''Semelhante à _new, mas data contêm objetos utilizados na
        representação interna do objeto'''

        new = object.__new__(type(self))
        if copy:
            new._data = list(data)
        else:
            new._data = data
        return new

    def _aligned(self, other):
        '''Check se outro objeto é alinhável e retorna uma versão alinhada do
        mesmo (ou o próprio objeto, caso ele já esteja alinhado)'''

        if len(other) != len(self):
            raise ValueError('operands are not aligned')
        return other

    def __getitem__(self, i):
        return self._out_transform(self._data[i])

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        T = self._out_transform
        if T is not None:
            for x in self._data:
                yield T(x)
        else:
            for x in self._data:
                yield x

    def _iter_raw(self):
        return iter(self._data)

    def __eq__(self, other):
        if len(self) != len(other):
            return False

        if isinstance(other, type(self)):
            iself = self._iter_raw()
            iother = other._iter_raw()
        else:
            iself, iother = self, other
        return all(x == y for (x, y) in zip(iself, iother))

    def __nonzero__(self):
        return len(self) != 0


class mAbstractArray(AbstractArray):

    def __delitem__(self, i):
        del self._data[i]

    def __setitem__(self, i, value):
        self._data[i] = self._in_transform(value)

    def _insert(self, i, value):
        if self._in_transform is not None:
            self._data.insert(i, self._in_transform(value))
        else:
            self._data.insert(i, value)

    def _setitem_raw(self, i, value):
        self._data[i] = value


class Arithmetic(object):
    _scalar = None
    _container = None

    def _bin_op(self, other, op):
        '''Implementação genérica de um operador binário.

        Considera separadamente os casos onde os argumentos são iguais ao
        self, escalares ou vetoriais'''

        if isinstance(other, type(self)):
            iother = self._aligned(other)._iter_raw()
            iself = self._iter_raw()
            return self._new_raw(op(x, y) for (x, y) in zip(iself, iother))

        elif (self._scalar is not None
              and isinstance(other, self._scalar)):
            return self._new(op(x, other) for x in self)

        elif (self._container is not None
              and isinstance(other, self._container)):
            other = self._aligned(other)
            return self._new(op(x, y) for (x, y) in zip(self, other))

        else:
            raise TypeError

    def _rbin_op(self, other, op):
        '''Implementação genérica de um operador binário reverso.

        Considera separadamente os casos onde os argumentos são iguais ao
        self, escalares ou vetoriais'''

        if isinstance(other, type(self)):
            iother = self._aligned(other)._iter_raw()
            iself = self._iter_raw()
            return self._new_raw(op(y, x) for (x, y) in zip(iself, iother))

        elif (self._scalar is not None
              and isinstance(other, self._scalar)):
            return self._new(op(other, x) for x in self)

        elif (self._container is not None
              and isinstance(other, self._container)):
            other = self._aligned(other)
            return self._new(op(y, x) for (x, y) in zip(self, other))

        else:
            raise TypeError

    def __mul__(self, other):
        return self._bin_op(other, operator.mul)

    def __rmul__(self, other):
        return self._rbin_op(other, operator.mul)

    def __div__(self, other):
        return self._bin_op(other, operator.truediv)

    __truediv__ = __div__  # Python 3

    def __rdiv__(self, other):
        return self._rbin_op(other, operator.truediv)

    __rtruediv__ = __rdiv__  # Python 3

    def __add__(self, other):
        return self._bin_op(other, operator.add)

    def __radd__(self, other):
        return self._rbin_op(other, operator.add)

    def __sub__(self, other):
        return self._bin_op(other, operator.sub)

    def __rsub__(self, other):
        return self._rbin_op(other, operator.sub)

    def __neg__(self):
        return self._new(-u for u in self)


class mArithmetic(Arithmetic):

    def _ibin_op(self, other, op):
        '''Implementação inplace de um operador binário'''

        if isinstance(other, type(self)):
            iother = self._aligned(other)._iter_raw()
            iself = self._iter_raw()
            for i, (x, y) in enumerate(zip(iself, iother)):
                self._data[i] = op(x, y)

        elif (self._scalar is not None
              and isinstance(other, self._scalar)):
            other = (self._in_transform or identity)(other)
            for i, x in enumerate(self._iter_raw()):
                self._data[i] = op(x, other)

        elif (self._container is not None
              and isinstance(other, self._container)):
            T = self._in_transform or identity
            iother = iter(self._aligned(other))
            iself = self._iter_raw()
            for i, (x, y) in enumerate(zip(iself, iother)):
                self._data[i] = op(x, T(y))
        else:
            raise TypeError

    def __iadd__(self, other):
        self._ibin_op(other, operator.add)

    def __isub__(self, other):
        self._ibin_op(other, operator.sub)

    def __imul__(self, other):
        self._ibin_op(other, operator.mul)

    def __idiv__(self, other):
        self._ibin_op(other, operator.truediv)
