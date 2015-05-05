cimport mathtools.mathfuncs as m
cimport cython

cdef class AABB:
    cdef public double xmax, xmin, ymax, ymin

    @cython.locals(xmax='double', xmin='double', ymax='double', ymin='double')
    cpdef bint _eq(self, object other)
