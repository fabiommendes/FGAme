'''
Algumas funções úteis relacionadas com a física.
'''
from FGAme.mathtools import null2D


def aslist(args):
    N = len(args)
    if N == 1:
        return args[0]
    elif N == 0:
        raise TypeError('must give at least one argument')
    else:
        return args


def center_of_mass(*args):
    '''Calcula o centro de massa dos argumentos.

    Cada argumento deve ser um objeto com os parâmetros `mass` e `pos`

    Example
    -------

    >>> from FGAme.physics import Body
    >>> b1 = Body(pos=(0, 30), mass=1)
    >>> b2 = Body(pos=(10, 0), mass=3)
    >>> center_of_mass(b1, b2)
    Vec(7.5, 7.5)
    '''

    Rcm = null2D
    M = 0

    for obj in aslist(args):
        Rcm += obj.pos * obj.mass
        M += obj.mass

    return Rcm / M


def mass(*args):
    '''Calcula a soma das massas dos argumentos'''

    return sum(obj.mass for obj in aslist(args))


def inertia(*args, pos=None):
    '''Calcula o momento de inércia total dos argumentos.

    O argumento opcional `pos` descreve o ponto de referência para o cálculo
    do centro de inércia. O comportamento padrão é utilizar o centro de massa.

    Example
    -------

    >>> from FGAme.physics import Body
    >>> b1 = Body(pos=(0, 2), mass=1, inertia=2)
    >>> b2 = Body(pos=(1, 0), mass=3, inertia=1)
    >>> inertia(b1, b2)
    6.75
    '''

    args = aslist(args)
    if pos is None:
        pos = center_of_mass(args)

    inertia = 0
    for obj in args:
        inertia += obj.mass * (obj.pos - pos).norm_sqr() + obj.inertia
    return inertia


def momentumP(*args):
    '''Calcula o momentum linear total de todos os objetos fornecidos.

    O momentum linear total de um grupo de objetos consiste na soma do momentum
    de cada objeto.'''

    return sum((obj.momentumP() for obj in aslist(args)), null2D)


def momentumL(*args, pos=None):
    '''Calcula o momentum angular total de todos os objetos dados.

    O argumento opcional `pos` descreve o ponto de referência para o cálculo
    do momentum linear. O comportamento padrão é utilizar o centro de massa.

    O momentum angular total de um grupo de objetos consiste na soma do
    momentum de cada objeto.'''

    args = aslist(args)
    if pos is None:
        pos = center_of_mass(args)
    return sum((obj.momentumL(pos) for obj in args), null2D)


def energyK(*args):
    '''Calcula a energia cinética total dos objetos dados. Inclui a
    componente linear e a componente angular da energia.'''

    return sum(obj.energyK() for obj in aslist(args))


def linearK(*args):
    '''Calcula a componente linear da energia cinética dos objetos dados.

    A componente linear corresponde aos termos do tipo $m v^2 / 2$.'''

    return sum(obj.energyK() for obj in aslist(args))


def angularK(*args):
    '''Calcula a componente angular da energia cinética dos objetos dados.

    A componente linear corresponde aos termos do tipo $I \omega^2 / 2$,
    onde I representa o momento de inércia com relação ao centro de massa.'''

    return sum(obj.energyK() for obj in aslist(args))


def energyU(*args):
    '''Calcula a energia potencial total dos objetos dados.'''

    # TODO: incluir energia de interação entre as partículas
    return sum(obj.energyU() for obj in aslist(args))


def energy(*args):
    '''Calcula a energia total dos objetos dados.'''

    return energyK(*args) + energyU(*args)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
