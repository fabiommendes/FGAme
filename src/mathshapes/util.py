# -*- coding: utf8 -*-
import cython


def pyinject(globals, name=None):
    '''Decorador que injeta a implementação fornecida na classe com o nome
    dado. Se o nome não for fornecido, assume que a implementação está em
    ClassNameInject, e a classe pública é ClassName.

    O dicionário `globals()` deve sempre ser fornecido como primeiro argumento.

    Exemplo
    -------

    >>> class Foo:
    ...    def bar(self):
    ...        print('original bar')


    >>> @pyinject(globals())
    ... class FooInject:
    ...     def bar(self):
    ...        print('redefined bar')

    No exemplo acima, o método `bar()` da classe `Foo` é redefinido.
    `pyinject()` é útil no contexto em que `Foo` é definido como uma classe
    cdef do Cython utilizando "pure python mode". Neste caso, a implementação
    pode ser injetada somente se o código estiver rodando no modo interpretado,
    mas mantêm a implementação original quando for compilar para Cython (a
    sintaxe do Cython não permite operar no sentido oposto, que talvez pareça
    mais natural).
    '''
    def decorator(cls):
        if name is None:
            if not cls.__name__.endswith('Inject'):
                print(cls.__name__)
                raise ValueError('class name must end with Inject')
        old = globals[cls.__name__[:-6]]

        if not cython.compiled:
            for k, v in cls.__dict__.items():
                if k in ['__module__', '__doc__', '__weakref__', '__dict__']:
                    continue
                if k == '__hash__' and v is None:
                    continue
                setattr(old, k, v)
        return None

    return decorator


#
# Printing functions
#
def tp_print(x):
    '''Mesmo que type(x).__name__'''

    return type(x).__name__


def num_print(x):
    '''Representação do número como string'''

    if int(x) == x:
        return str(int(x))
    else:
        return '%.1s' % x


def pt_print(pt):
    '''Representação de ponto (ou sequência de números) como string'''

    return '(%s)' % (', '.join(map(num_print, pt)))


#
# Conversion of arguments
#
def args_to_vec2(x_or_delta, y):
    '''Convert the sequence of arguments (x_or_delta, y) to a proper vector'''

    try:
        vec2 = Vec2  # @UndefinedVariable
    except NameError:
        from mathtools import Vec2
        vec2 = globals()['Vec2'] = Vec2

    if y is None:
        if isinstance(x_or_delta, vec2):
            return x_or_delta
        else:
            return vec2.from_seq(x_or_delta)
    else:
        return vec2(x_or_delta, y)
