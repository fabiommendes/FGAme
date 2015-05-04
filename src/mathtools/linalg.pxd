cimport cython
cdef extern from "math.h":
    double sin(double x)
    double cos(double x)
    double sqrt(double x)
    int ctrunc "trunc"(double x)


@cython.freelist(8)
cdef class Vec2:
    cdef public double _x, _y

    cpdef Vec2 _from_coords(Vec2 self, double x, double y)
    cpdef tuple as_tuple(self)
    cpdef double norm(self)
    cpdef double norm_sqr(self)
    cpdef Vec2 normalize(self)

cdef class mVec2(Vec2):
    pass

