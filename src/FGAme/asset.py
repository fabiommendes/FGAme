import os

from lazyutils import lazy

import FGAme
from FGAme.utils import snake_case


class Asset:
    """
    Generic asset
    """

    extensions = ['']

    @lazy
    def file_type(self):
        return snake_case(type(self).__name__)

    def __init__(self, name, file_type=None, extensions=None):
        self.name = name
        if file_type is not None:
            self.file_type = file_type
        self.extensions = list(extensions or self.extensions)
        try:
            self.path = self.best_path()
        except ValueError:
            self.path = None
        self.is_valid = self.path is not None

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self.name)

    def paths(self):
        """
        Iterate over all possible paths that may contain the asset.
        """

        name = os.path.join(*self.name.split('/'))
        for directory in self.directories():
            for ext in self.extensions:
                path = os.path.join(directory, name + ext)
                yield path

    def directories(self):
        """
        Iterate over all possible directories that may contain the asset.
        """

        base = os.path.abspath('assets')
        yield os.path.join(base, self.file_type)

        glob = os.path.dirname(FGAme.__file__)
        yield os.path.join(glob, 'assets', self.file_type)

    def best_path(self):
        """
        Return the full path to filename with the highest priority.
        If no suitable files were found, raises a ValueError.
        """

        for path in self.paths():
            if os.path.exists(path):
                return path
        raise ValueError('no file found for asset %r' % self.name)

    def open(self, mode='rb', encoding=None):
        """
        Return an open file descriptor.
        """

        return open(self.path, mode=mode, encoding=encoding)

    def __enter__(self):
        self.__file = F = self.open()
        return F.__enter__()

    def __exit__(self, *args):
        self.__file.__exit__(*args)