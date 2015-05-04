# -*- coding: utf8 -*-
'''
Abstract classes for representing Geometric figures
'''

import abc
import copy
import six


def not_implemented(self):
    '''Generic implementation for abstract attributes'''

    return NotImplemented


def attr_factory(name):
    '''Factory functin for the abstract fields of a geometric object'''

    func = copy.copy(not_implemented)
    func.__name__ = name
    return abc.abstractproperty(func)


###############################################################################
#                     Abstract base classes: definitions
###############################################################################

@six.add_metaclass(abc.ABCMeta)
class AbstractGeometry(object):

    '''Subclasshook checks if class has all fields defined in the metaclass.

    This can be easily tricked by dictionary classes, hence one may want to
    register classes explicitly.'''

    @classmethod
    def __subclasshook__(cls, other):
        for m in cls.__abstractmethods__:
            method = getattr(other, m, None)
            if not hasattr(method, '__get__'):  # look for a descriptor
                return False

        else:
            return True


class AbstractCircle(AbstractGeometry):

    '''A circle is defined as an object that has an radius and a `pos`
    attribute representing the center.'''

    radius = attr_factory('radius')
    pos = attr_factory('pos')


class AbstractAABB(AbstractGeometry):

    '''An abstract AABB must define xmin, xmax, ymin, ymax along with the
    bbox, rect, pos and shape attributes.'''

    pos = attr_factory('pos')
    shape = attr_factory('shape')
    bbox = attr_factory('bbox')
    rect = attr_factory('rect')
    xmin = attr_factory('xmin')
    ymin = attr_factory('ymin')
    xmax = attr_factory('xmax')
    ymax = attr_factory('ymax')


class AbstractPoly(AbstractGeometry):

    '''A polygon has a list of points in the `vertices` attribute.'''

    vertices = attr_factory('vertices')


if __name__ == '__main__':
    pass