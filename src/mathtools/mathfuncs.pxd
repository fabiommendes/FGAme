#: no-compile

cdef extern from "math.h":
    double csin "sin"(double x)
    double ccos "cos"(double x)
    double csqrt "sqrt"(double x)
    int ctrunc "trunc"(double x)

cpdef inline double sin(double x):
    return csin(x)

cpdef inline double cos(double x):
    return ccos(x)

cpdef inline double sqrt(double x):
    return csqrt(x)

cpdef inline int trunc(double x):
    return ctrunc(x)
