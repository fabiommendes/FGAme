cimport cython
cimport mathfuncs as m

@cython.freelist(8)
cdef class Vec2:
    cdef readonly double x, y

    cpdef Vec2 _from_coords(Vec2 self, double x, double y)
    cpdef tuple as_tuple(self)
    cpdef double norm(self)
    cpdef double norm_sqr(self)
    cpdef Vec2 normalize(self)

cdef class VecSlot:
    cdef public object getter, setter
