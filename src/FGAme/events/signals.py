import weakref
from collections import namedtuple
from FGAme.events.util import pyname, wrap_handler

ControlElem = namedtuple('ControlElem', ['idx', 'owner', 'wrapped', 'handler',
                                         'args', 'kwargs'])


class Signal(object):

    '''Representa um sinal comum anunciado por um objeto.'''

    sig_args = ()

    def __init__(self, name, num_args=0):
        self.name = name
        self.num_args = num_args
        self._num_filters = 0
        self._ctl_name = '_%s_ctl' % pyname(self.name)

    def __get__(self, instance, cls=None):
        if instance is not None:
            return getattr(instance, self._ctl_name)
        else:
            return self

    def __set__(self, instance, value):
        raise AttributeError('not writable')

    def __repr__(self):
        tname = type(self).__name__
        return '%s(%r, %s)' % (tname, self.name, self.num_args)

    def default_control(self, owner):
        '''Retorna o objeto tipo SignalCtl apropriado para essa classe de
        sinais'''

        return SignalCtl(self, owner)

    ###########################################################################
    # Fábrica de funções para os métodos listen_<sinal> e trigger_<sinal>
    ###########################################################################

    def _factory_listen_method(self):
        signal = self  # não confundir com o self da função fabricada!

        def listen_method(self, *args, **kwargs):
            '''vsds %(signal)s'''

            # Confere argumentos de entrada
            args_ = kwargs.pop('args', None)
            kwargs_ = kwargs.pop('kwargs', None)
            owner = kwargs.pop('owner', None)
            if args_:
                args = args_
            if kwargs_:
                kwargs = kwargs_

            # Extrai os filtros, caso necessário
            filter_args = args[:signal._num_filters]
            try:
                handler = args[signal._num_filters]
            except IndexError:
                handler = None
            args = args[signal._num_filters + 1:]

            if args_ is not None and args:
                raise TypeError('cannot specify the args parameter and also '
                                'insert positional arguments')
            if kwargs_ is not None and kwargs:
                raise TypeError('cannot specify the kwargs parameter and also '
                                'insert keyword arguments')

            # Caso handler=None, estamos chamando o método listen na versão
            # de decorador
            if handler is None:
                def decorator(func):
                    args_ = filter_args + (func,)
                    kwargs_ = {'args': args, 'kwargs': kwargs, 'owner': owner}
                    return listen_method(self, *args_, **kwargs_)
                return decorator

            # Registra nas listas de controle
            wrapped = wrap_handler(
                handler, args, kwargs, pre_args=signal.num_args)
            ctl = getattr(self, '_%s_ctl' % pyname(signal.name))

            if signal._num_filters == 0:
                idx = len(ctl._data)
                elem = ControlElem(idx, owner, wrapped, handler, args, kwargs)
                ctl._runner.append(wrapped)
                ctl._data.append(elem)
                return idx

            elif signal._num_filters == 1:
                key = filter_args[0]
                ids = {}

                if key is None:
                    # Registra como handler de todas os filtros no livro
                    for k in ctl._runner:
                        if k is None:
                            continue
                        wrapped_i = wrap_handler(handler, (k,) + args, kwargs,
                                                 pre_args=signal.num_args)
                        ids[k] = listen_method(self, k, wrapped_i)

                    # Cria um elemento de controle substituindo o campo
                    # "wrapped" pelo dicionário das ids em cada filtro
                    control = ctl._data.setdefault(None, [])
                    book = ctl._runner.setdefault(None, [])
                    idx = len(control)
                    elem = ControlElem(idx, owner, ids, handler, args, kwargs)
                    control.append(elem)
                    book.append(
                        wrap_handler(
                            handler, args, kwargs, pre_args=signal.num_args))

                    return (None, idx)
                else:
                    try:
                        idx = len(ctl._data[key])
                    except KeyError:
                        ctl._data[key] = []
                        ctl._runner[key] = []

                        for ctl_e in ctl._data.get(None, []):
                            wrapped_i = wrap_handler(
                                ctl_e.handler, (key,) + ctl_e.args,
                                ctl_e.kwargs, signal.num_args)
                            ctl_e.wrapped[key] = listen_method(
                                self, key, wrapped_i)

                        idx = len(ctl._data[key])

                    elem = ControlElem(
                        idx, owner, wrapped, handler, args, kwargs)
                    ctl._runner[key].append(wrapped)
                    ctl._data[key].append(elem)
                    return key, idx

            else:
                book = ctl._runner[filter_args]
                control = ctl._data[filter_args]
            raise RuntimeError

        listen_method.__name__ = 'listen_' + pyname(signal.name)
        listen_method.__doc__ = listen_method.__doc__ % {'signal': signal.name}
        return listen_method

    def _factory_trigger_method(self):
        signal = self  # não confundir com o self da função fabricada!
        attr_name = pyname('_%s_book' % signal.name)

        # Especializamos para 0, 1 ou 2 argumentos por questões de performance
        if signal.num_args == 0:
            def trigger_method(self):
                book = getattr(self, attr_name)
                for wrapped_func in book:
                    wrapped_func()

        elif signal.num_args == 1:
            def trigger_method(self, arg):
                book = getattr(self, attr_name)
                for wrapped_func in book:
                    wrapped_func(arg)

        elif signal.num_args == 2:
            def trigger_method(self, arg1, arg2):
                book = getattr(self, attr_name)
                for wrapped_func in book:
                    wrapped_func(arg1, arg2)

        else:
            def trigger_method(self, *args):
                if len(args) != signal.num_args:
                    raise TypeError('expected %s arguments' % self.num_args)

                book = getattr(self, attr_name)
                for wrapped_func in book:
                    wrapped_func(*args)

        trigger_method.__name__ = 'trigger_' + pyname(signal.name)
        # trigger_method.__doc__ = trigger_method.__doc__ % \
        #                         {'signal': signal.name}
        return trigger_method


class FilteredSignal(Signal):

    '''Implementa um sinal filtrado: ou seja, um sinal que assume um segundo
    argumento e dispacha apenas os handlers registrados para aquele argumento.

    Útil para eventos do tipo key-press onde podemos acionar os handlers
    seletivamente de acordo com a tecla pressionada.
    '''

    def __init__(self, name, num_args=0, filter_names=None):
        super(FilteredSignal, self).__init__(name, num_args)
        self._num_filters = 1
        self._filter_names = filter_names or (None,) * self._num_filters

    def default_control(self, owner):
        return SignalCtlMulti(self, owner)

    def _factory_trigger_method(self):
        signal = self  # não confundir com o self da função fabricada!
        attr_name = pyname('_%s_book' % signal.name)

        # Especializamos para 0, 1 ou 2 argumentos por questões de performance
        if signal.num_args == 0:
            def trigger_method(self, key):
                book = getattr(self, attr_name)
                kbook = book.get(key, None)
                if kbook is not None:
                    for wrapped_func in kbook:
                        wrapped_func()
                else:
                    gen_book = book.get(None, None)
                    if gen_book is not None:
                        for func in gen_book:
                            func(key)

        elif signal.num_args == 1:
            def trigger_method(self, key, arg):
                book = getattr(self, attr_name)
                kbook = book.get(key, None)
                if kbook is not None:
                    for wrapped_func in kbook:
                        wrapped_func(arg)
                else:
                    gen_book = book.get(None, None)
                    if gen_book is not None:
                        for func in gen_book:
                            func(key, arg)

        else:
            def trigger_method(self, key, *args):
                if len(args) != signal.num_args:
                    raise TypeError('expected %s arguments' % self.num_args)

                book = getattr(self, attr_name)
                kbook = book.get(key, None)
                if kbook is not None:
                    for wrapped_func in kbook:
                        wrapped_func(*args)
                else:
                    gen_book = book.get(None, None)
                    if gen_book is not None:
                        for func in gen_book:
                            func(key, *args)

        trigger_method.__name__ = 'trigger_' + pyname(signal.name)
        # trigger_method.__doc__ = (trigger_method.__doc__
        #                            % {'signal': signal.name})
        return trigger_method

    def __repr__(self):
        names = ''
        if self._filter_names:
            names = ', filter_names=%s' % list(self._filter_names)
        tname = type(self).__name__
        return '%s(%r, %s%s)' % (tname, self.name, self.num_args, names)


class DelegateSignal(Signal):

    '''Delega o sinal para um atributo da classe.

    Sinais deste tipo não podem ser emitidos diretamente, mas é possível
    registrar handlers que serão encaminhados para o método listen do atributo
    responsável por gerenciar o despacho de eventos'''

    def __init__(self, name, delegate_to, num_filters=0, filter_names=None):
        super(DelegateSignal, self).__init__(name)
        self.delegate_to = delegate_to
        self._num_filters = num_filters
        self._filter_names = filter_names

    def _factory_listen_method(self):
        signal = self

        def listen_method(self, *args, **kwds):
            kwds.setdefault('owner', self)
            delegate_to = getattr(self, signal.delegate_to)
            return delegate_to.listen(signal.name, *args, **kwds)

        return listen_method

    def _factory_trigger_method(self):

        def trigger_method(self, *args):
            raise RuntimeError('signals can only be trigged by the owner')

        return trigger_method

    def __get__(self, instance, cls=None):
        if instance is not None:
            owner = getattr(instance, self.delegate_to)
            return getattr(owner, self._ctl_name)
        else:
            return self


###############################################################################
#                           Controle de sinais
###############################################################################
class SignalCtl(object):

    '''A classe SignalCtl implementa uma interface para gerenciar os handlers
    registrados para um determinado sinal'''

    def __init__(self, signal, instance):
        self.signal = signal
        self._data = []
        self._runner = []
        #self._instance = weakref.ref(instance)
        self._instance = instance

    @property
    def instance(self):
        # return self._instance()
        return self._instance

    @property
    def name(self):
        return self.signal.name

    @property
    def handlers(self):
        return [ctl.handler for ctl in self._data if ctl is not None]

    @property
    def handlers_full(self):
        return [(ctl.handler, ctl.args, ctl.kwargs)
                for ctl in self._data if ctl is not None]

    @property
    def owners(self):
        return [ctl.owner for ctl in self._data if ctl is not None]

    def remove(self, *args, **kwds):
        '''Remove handlers baseado em algum critério.

        Assinaturas
        -----------

        obj.remove(id=<handler_id>) ou obj.remove(<handler_id>)
            Remove handler especificando a id retornada pelo método listen()

        obj.remove(handler=<handler function>)
            Remove handler a partir da função handler registrada no método
            listen(). Esta opção remove todos os handlers associados à função
            dada, mesmo que registrados com argumentos diferentes

        obj.remove(owner=<owner>)
            Remove todos os handlers associados ao dono fornecido. Esta função
            é útil em delegações em que os handlers podem ser criados por
            vários objetos diferentes.
        '''

        if not args:
            key, value = kwds.popitem()
        elif len(args) == 1:
            key, value = 'id', args[0]
        else:
            raise TypeError('wrong number of positional arguments')
        if kwds:
            raise TypeError('must specify exactly one criteria')

        removed = []

        if key == 'id':
            idx = value
            wrapped = self._data[idx].wrapped
            w_idx = [i for i, w in enumerate(self._runner) if w is wrapped]
            if len(w_idx) > 1:
                raise NotImplementedError

            del self._runner[w_idx[0]]
            removed.append(self._data[idx])
            self._data[idx] = None

        elif key == 'handler':
            for i, ctl in enumerate(self._data):
                if ctl.handler == value:
                    removed_obj = self.remove(id=i)
                    removed.extend(removed_obj)

        elif key == 'owner':
            for i, ctl in enumerate(self._data):
                if ctl.owner == value:
                    removed_obj = self.remove(id=i)
                    removed.extend(removed_obj)

        else:
            raise TypeError('invalid argument: %s' % key)

        return removed

    def restore(self, L):
        '''Restaura uma lista de sinais removidas pelo método remove()'''

        for ctl_elem in L:
            if self._data[ctl_elem.idx] is not None:
                raise RuntimeError(
                    'restoring handler that were not removed or '
                    'were already restored')
            else:
                self._data[ctl_elem.idx] = ctl_elem
                self._runner.append(ctl_elem.wrapped)

    def listen(self, *args, **kwds):
        '''Registra um callback para o sinal'''

        return self.instance.listen(self.name, *args, **kwds)

    def trigger(self, *args, **kwds):
        '''Emite um sinal'''

        return self.instance.trigger(self.name, *args, **kwds)

    #
    # Magic methods
    #
    def __contains__(self, handler):
        return handler in self._data


class SignalCtlMulti(SignalCtl):

    '''Gerencia handlers de sinais filtrados'''

    # TODO: talvez implementar como um dicionario de SignalCtl

    def __init__(self, signal, owner):
        super(SignalCtlMulti, self).__init__(signal, owner)
        self._runner = {}
        self._data = {}
