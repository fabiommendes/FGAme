#-*- coding: utf8 -*-
'''
Benchmarks para FGAme
'''

import FGAme
import time
BASE_SIZE = 1000
BENCH_FUNCTIONS = []
try:
    range = xrange  # @ReservedAssignment @UndefinedVariable  
except NameError:
    pass


def bench(func):
    '''Decorador para ser aplicado nas funções de teste de benchmarks'''

    BENCH_FUNCTIONS.append(func)
    return func


def all(size=None):
    '''Executa todos os benchmarks no módulo'''

    for func in BENCH_FUNCTIONS:
        t0 = time.time()
        text = func.__doc__
        func_name = func.__name__
        func()
        t1 = time.time()
        print('%s: (%s) %.3f sec' % (func_name, text, t1 - t0))

#===============================================================================
# Vetores
#===============================================================================


@bench
def vector():
    '''Operações aritiméticas com vetores'''

    v = FGAme.Vec2(1.5, 1.5)
    for _ in range(BASE_SIZE * 1000):
        v = 2 * v - v


@bench
def ivector():
    '''Operações aritiméticas inplace com vetores'''

    v = FGAme.Vec2(1.5, 1.5)
    v2 = FGAme.mVec2(1.5, 1.5)
    for _ in range(BASE_SIZE * 1000):
        v2 += v


@bench
def vtuple():
    '''Operações aritiméticas vetores e tuplas'''

    v = FGAme.Vec2(1.5, 1.5)
    v2 = FGAme.mVec2(1.5, 1.5)
    for _ in range(BASE_SIZE * 1000):
        v2 += (1, 1)
        v += (1, 1)

if __name__ == '__main__':
    all()