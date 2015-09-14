# -*- coding: utf8 -*-

from . import Body

__all__ = ['Particle']

###############################################################################
# Objetos que obedecem à interface de "partícula" de física. Este objetos
# possuem grandezas lineares e parâmetros físicos associados à elas definidos.
# Objetos mais complexos (e.g., corpos rígidos) podem herdar dessa classe e
# implementar outras interfaces e atributos adicionais.
# se
# Apenas as propriedades físicas são definidas aqui. Cores, texturas, resposta
# a eventos do usuário, etc devem ser implementadas em sub-classes.
###############################################################################


class Particle(Body):

    '''Define uma partícula.


    Example
    -------

    Simula uma partícula em lançamento parabólico

    >>> p = Particle(vel=(8, 8))
    >>> for i in range(8):
    ...     print('%4.1f, %4.1f' % tuple(p.pos))
    ...     p.apply_accel((0, -8), dt=0.25)
     0.0,  0.0
     2.0,  1.5
     4.0,  2.5
     6.0,  3.0
     8.0,  3.0
    10.0,  2.5
    12.0,  1.5
    14.0,  0.0
    '''

    __slots__ = []


if __name__ == '__main__':
    import doctest
    doctest.testmod()
