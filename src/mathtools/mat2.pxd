cimport cython
cimport mathfuncs as m
from vec2 cimport Vec2

@cython.freelist(8)
cdef class Mat2:
    cdef public double _a, _b, _c, _d
