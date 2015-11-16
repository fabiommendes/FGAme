import itertools
from FGAme.events.util import pyname
from FGAme.events.signals import Signal, DelegateSignal


class EventDispatcherMeta(type):

    '''Meta-classe para EventDispatcher.

    Fabrica e registra automaticamente os métodos listen_* e trigger_*.
    Atualiza os __slots__ caso a classe filho os utilize. Finalmente salva
    algumas constantes úteis para a introspecção:

        __signals__
            Dicionário mapeando todos os nomes de sinais com os seus
            respectivos objetos.
        __autolisten__
            Dicionário com todos os métodos que foram marcados com o decorador
            @listen durante a definição da classe.
    '''

    def __new__(cls, name, bases, ns):
        # Cria dicionário de sinais
        signals = {}
        for C in reversed(bases):
            signals.update(getattr(C, '__signals__', {}))
        for attr, value in ns.items():
            if isinstance(value, Signal):
                signals[attr] = value
        ns['__signals__'] = signals
        
        # Modifica valores de slots, caso necessário
        if '__slots__' in ns:
            slots = list(ns['__slots__'])
            for signame, signal in signals.items():
                if not isinstance(signal, DelegateSignal):
                    slots.append('_%s_ctl' % signame)
                    slots.append('_%s_book' % signame)
            ns['__slots__'] = slots

        # Cria objeto
        new = type.__new__(cls, name, bases, ns)
        
        # Cria os métodos do tipo listen_* e tipo trigger_* 
        methods = itertools.chain(cls.triggers(new, signals.values()), 
                                  cls.listeners(new, signals.values()))
        for name, method in methods:
            if not hasattr(new, name):
                setattr(new, name, method)
            else:
                setattr(new, '_' + name, method)
        
        # Escaneia todos os métodos decorados com @listen
        new.__autolisten__ = cls.autolisten(new)
        signal_names = [sig.name for sig in new.__signals__.values()]
        delta = set(new.__autolisten__) - set(signal_names)
        if delta:
            fmt = new.__name__, delta.pop() 
            raise ValueError('invalid signal in %s class definition: %s' % fmt) 
        return new

    @staticmethod
    def triggers(cls, signals):
        for signal in signals:
            name = 'trigger_' + pyname(signal.name)
            yield name, signal._factory_trigger_method()
            
    @staticmethod
    def listeners(cls, signals):
        for signal in signals:
            name = 'listen_' + pyname(signal.name)
            yield name, signal._factory_listen_method()
            
    @staticmethod
    def autolisten(cls):
        listen = {}
        for C in reversed(cls.__bases__):
            listen.update(getattr(C, '__autolisten__', {}))
        
        for attr, value in vars(cls).items():
            if hasattr(value, '__autolisten__'):
                for name, args, kwds in getattr(value, '__autolisten__'):
                    L = listen.setdefault(name, [])
                    L.append((attr, args, kwds))
        
        return listen


class EventDispatcher(object, metaclass=EventDispatcherMeta):

    '''Implementa o despachante de eventos da biblioteca FGAme.'''

    __slots__ = ()

    def __init__(self):
        for signal in self.__signals__.values():
            ctl = signal.default_control(self)
            setattr(self, '_%s_ctl' % pyname(signal.name), ctl)
            if not isinstance(signal, DelegateSignal):
                setattr(self, '_%s_book' % pyname(signal.name), ctl._runner)

            # Registra os métodos criados pelo mecanismo on_signal...
            auto_method = getattr(self, 'on_' + pyname(signal.name), None)
            if auto_method is not None:
                kwargs = {'owner': self}
                if signal._num_filters == 0:
                    self.listen(signal.name, auto_method, **kwargs)
                else:
                    args = (None,) * signal._num_filters
                    args += (auto_method,)
                    self.listen(signal.name, *args, **kwargs)

            # Registra os métodos criados pelo mecanismo @listen
            marked_listen = self.__autolisten__.get(signal.name, [])
            for (func_name, args, kwargs) in marked_listen:
                handler = getattr(self, func_name)
                filters = (
                    args[:signal._num_filters]
                    or (None, ) * signal._num_filters
                )
                args = args[signal._num_filters:]
                args = filters + (handler,) + args
                kwargs = kwargs.copy()
                kwargs['owner'] = self
                self.listen(signal.name, *args, **kwargs)

    def trigger(self, signal, *args, **kwds):
        '''Aciona o sinal com os argumentos fornecidos.'''

        implementation = getattr(self, 'trigger_' + pyname(signal))
        return implementation(*args, **kwds)

    def listen(self, signal, *args, **kwds):
        '''Registra um handler para um determinado sinal.

        A assinatura correta para esta função depende do tipo de sinal
        considerado. Para sinais simples, basta utilizar::



            obj.listen(<nome do sinal>, <handler>)

        Sinais filtrados (aqueles que pedem um ou mais argumentos adicionais),
        devem ser registrados como::

            obj.listen(<nome do sinal>, <filtro>, <handler>)

        Opcionalmente, é possível acrescentar argumentos por nome ou posição
        que serão passados automaticamente para o handler quando o sinal for
        acionado.
        '''

        implementation = getattr(self, 'listen_' + pyname(signal))
        return implementation(*args, **kwds)

    def destroy_handlers(self, signal=None):
        '''Destroy todos os handlers associados ao sinal dado.

        Retorna um dicionário que mapeia o nome dos sinais à lista de handlers
        removidos.'''

        if signal is None:
            out = {}
            for signal in self.__signals__:
                handlers = self.destroy_handlers(signal)
                out.update(handlers)
            return out
        else:
            signalctl = getattr(self, signal)
            handlers = signalctl.remove(owner=self)
            return {signal: handlers}
