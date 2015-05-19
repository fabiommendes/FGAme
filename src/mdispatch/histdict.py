from collections import UserDict


class HistDict(UserDict):

    '''A dictionary that saves the history of all insertions and deletions.
    The history is stored in the ``.history`` attribute and consists of a
    list of tuples of (key, value) for insertions and (key,) for deletions.

    Example
    -------

    It can be used just as a regular dict

    >>> D = HistDict()
    >>> D['foo'] = 1
    >>> D['bar'] = 2
    >>> D['foo'] = 3; D
    HistDict({'bar': 2, 'foo': 3})

    However the history of insertions can be restored

    >>> D.history
    [('foo', 1), ('bar', 2), ('foo', 3)]

    And it accepts rolling back to previous states

    >>> D.rollback(1)
    HistDict({'bar': 2, 'foo': 1})

    Or can even condense the result of various changes to a dictionary that
    maps ``key: tuple-of-encountered-values``

    >>> D.condense()
    {'foo': (1, 3), 'bar': (2,)}

    Or iterate over all incarnations of a value

    >>> list(D.allitems())
    [('foo', 3), ('bar', 2), ('foo', 1)]
    '''

    def __init__(self, *args, **kwds):
        self.data = dict(*args, **kwds)
        self.history = []

    def __setitem__(self, key, value):
        self.data[key] = value
        self.history.append((key, value))

    def __delitem__(self, key):
        del self.data[key]
        self.history.append((key,))

    def __repr__(self):
        # Sort keys for representation in order to kelp with doctests ;)
        try:
            datarepr = ['%r: %r' % item for item in sorted(self.data.items())]
            datarepr = ', '.join(datarepr)
        except:
            # non-sortable types
            datarepr = str(self.data)[1:1]
        return '%s({%s})' % (type(self).__name__, datarepr)

    @classmethod
    def from_history(cls, history, raises=True):
        '''Returns a new HistDict from a history list'''

        D = HistDict()
        for item in history:
            if len(item) == 1:
                try:
                    del D[item[0]]
                except KeyError:
                    if raises:
                        raise
            else:
                k, v = item
                D[k] = v
        return D

    def remove_first(self, L, inplace=False):
        '''Return a new HistDict removing the first insertion of all keys in
        the list L.

        If the keys are repeated, it removes the number of insertions of key
        that appears in the list L
        '''

        history = list(self.history)
        for key in L:
            for i, item in enumerate(history):
                if len(item) == 2 and item[0] == key:
                    del history[i]
                    break

        out = self.from_history(history, raises=False)
        if inplace:
            self.data.clear()
            self.data.update(out.data)
            self.history = history
        else:
            return out

    def remove_last(self, L, inplace=False):
        '''Return a new HistDict removing the last insertion of all keys in
        the list L. Repetitions are handled in the same way as in
        remove_first()'''

        try:
            self.history.reverse()
            out = self.remove_first(L)
            out.history.reverse()
        finally:
            self.history.reverse()
            return out

        if inplace:
            self.data.clear()
            self.data.update(out.data)
            self.history = out.history
        else:
            return out

    def asdict(self):
        '''Return a copy as regular dictionary.'''

        return dict(self.data)

    def rollback(self, n=1, inplace=False):
        '''Return a dictionary that rolls back n steps of its change
        history.

        If inplace=True, perform changes inplace.
        '''

        if not inplace:
            out = self.copy()
            out.rollback(n, inplace=True)
            return out
        if n > 1:
            self.rollback(n - 1)
        if not self.history:
            raise ValueError('history is empty')

        last = self.history.pop()

        # Last modification was a deletion
        if len(last) == 1:
            key = last[0]
            for item in reversed(self.history):
                if item[0] == key:
                    self.data[key] = item[1]
                    break

        # Last modification was an insertion
        else:
            key = last[0]
            self.data[key]
            for item in reversed(self.history):
                if item[0] == key:
                    if len(item) == 2:
                        self.data[key] = item[1]
                    break

    def condense(self, reverse=False):
        '''Return a new dictionary that maps key: tuple_of_values, in which
        the tuple of values is a tuple of all values that were assigned to
        each key (and not explicitly deleted) in the same order of insertion.

        If reverse=True, creates the tuples in the reversed order.'''

        out = {}
        for item in self.history:
            if len(item) == 2:
                out.setdefault(item[0], []).append(item[1])
            else:
                out[item[0]].pop()

        if reverse:
            return {k: tuple(reversed(v)) for (k, v) in out.items()}
        else:
            return {k: tuple(v) for (k, v) in out.items()}

    def allitems(self):
        '''Iterate over all (key, value) pairs that were not explicitly
        deleted'''

        deleted = set()
        for item in reversed(self.history):
            k = item[0]
            if len(item) == 2:
                value = item[1]
                if k in deleted:
                    deleted.remove(k)
                else:
                    yield k, value
            else:
                deleted.add(k)

    def allvalues(self):
        '''Iterate over all values that were not explicitly deleted'''

        return (v for (k, v) in self.allitems())

    def allkeys(self):
        '''Iterate over all keys that were not explicitly deleted'''

        return (k for (k, v) in self.allitems())

    def copy(self):
        '''Return a copy of dictionary'''

        new = HistDict.__new__(type(self))
        new.data = dict(self.data)
        new.history = self.history[:]
        return new


if __name__ == '__main__':
    import doctest
    doctest.testmod()
