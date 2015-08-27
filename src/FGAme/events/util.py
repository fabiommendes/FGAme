from functools import partial


def pyname(value):
    '''Retorna versão do nome aceitável como nome de variável Python
    (e.g.: troca '-' por '_') e outras substituições.'''

    return value.replace('-', '_')


def wrap_handler(func, args, kwds, pre_args=0):
    '''Fixa os argumentos posicionais e keywords na função.
    Retorna uma função que sempre exige pre_args argumentos posicionais'''

    func_out = func

    if args and kwds:
        if pre_args == 0:
            func_out = partial(func, *args, **kwds)
        elif pre_args == 1:
            def func_out(x):
                return func(x, *args, **kwds)
        elif pre_args == 2:
            def func_out(x, y):
                return func(x, y, *args, **kwds)
        else:
            def func_out(*f_args):
                f_args += args
                return func(*f_args, **kwds)

    elif args:
        if pre_args == 0:
            func_out = partial(func, *args)
        elif pre_args == 1:
            def func_out(x):
                return func(x, *args)
        elif pre_args == 2:
            def func_out(x, y):
                return func(x, y, *args)
        else:
            def func_out(*f_args):
                f_args += args
                return func(*f_args)

    elif kwds:
        func_out = partial(func, **kwds)

    return func_out


def listen(name, *args, **kwds):
    '''Decorador que registra uma função como sendo um callback de um
    determinado sinal'''

    def decorator(func):
        try:
            L = func._listen_args
        except AttributeError:
            L = func._listen_args = []
        finally:
            L.append((name, args, kwds))
        return func

    return decorator


def signal(name, *filters, **kwds):
    '''Define um sinal.

    Possui a assinatura signal(nome, [arg1, ...,[ num_args]]), onde arg_i são
    strings com os nomes dos argumentos e o valor opcional num_args é um número
    representando o número de argumentos para o handler padrão.

    O tipo de sinal é escolhido automaticamente a partir dos argumentos:

    >>> signal('foo', num_args=1)
    Signal('foo', 1)

    >>> signal('foo', 'bar')
    FilteredSignal('foo', 0, filter_names=['bar'])

    >>> signal('foo', delegate_to='_foo_attr')
    DelegateSignal('foo', 0)
    '''

    from FGAme.events.signals import Signal, DelegateSignal, FilteredSignal

    # Extrai argumentos
    num_filters = len(filters)
    num_args = kwds.pop('num_args', 0)
    delegate_to = kwds.pop('delegate_to', None)
    if kwds:
        raise TypeError('invalid argument: %r' % kwds.popitem()[0])

    if delegate_to:
        if num_filters == 0:
            return DelegateSignal(name, delegate_to=delegate_to)
        else:
            return DelegateSignal(name,
                                  delegate_to=delegate_to,
                                  num_filters=num_filters,
                                  filter_names=filters)
    elif num_filters == 0:
        return Signal(name, num_args=num_args)
    elif num_filters == 1:
        return FilteredSignal(name, num_args=num_args, filter_names=filters)
    else:
        raise NotImplementedError('filtered signals with more than 1 argument')
