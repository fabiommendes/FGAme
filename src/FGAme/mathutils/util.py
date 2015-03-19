#-*- coding: utf8 -*-

#
# Importa todas as funções matemáticas do módulo math e acrescenta mais algumas
#
from math import *

def sign(x):
    '''Retorna -1 para um numero negativo e 1 para um número positivo'''

    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0
    
def shadow_x(A, B):
    '''Retorna o tamanho da sombra comum entre os objetos A e B no eixo x. 
    Caso não haja superposição, retorna um valor negativo que corresponde ao 
    tamanho do buraco'''

    return min(A.xmax, B.xmax) - max(A.xmin, B.xmin)

def shadow_y(A, B):
    '''Retorna o tamanho da sombra comum entre os objetos A e B no eixo y. 
    Caso não haja superposição, retorna um valor negativo que corresponde ao 
    tamanho do buraco'''

    return min(A.ymax, B.ymax) - max(A.ymin, B.ymin)
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()