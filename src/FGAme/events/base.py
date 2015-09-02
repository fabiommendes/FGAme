# -*- coding: utf8 -*-
import six
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
        __marked_listen__
            Dicionário com todos os métodos que foram marcados com o decorador
            @listen durante a definição da classe.
    '''

    def __new__(cls, name, bases, ns):
        ns = cls._populate_namespace(name, bases, ns)
        return type.__new__(cls, name, bases, ns)

    @classmethod
    def _populate_namespace(cls, name, bases, ns):
        '''Retorna o namespace ns acrescentado dos métodos trigger_* e
        listen_* apropriados para a classe em questão'''

        ns = dict(ns)

        # Lê os sinais e monta um dicionário de sinais
        signals = {}
        for C in reversed(bases):
            signals.update(getattr(C, '__signals__', {}))
        for attr, value in ns.items():
            if isinstance(value, Signal):
                signals[attr] = value
        ns['__signals__'] = signals

        # Cria os métodos do tipo listen_* e tipo trigger_*
        for signal in signals.values():
            lname = 'listen_' + pyname(signal.name)
            tname = 'trigger_' + pyname(signal.name)
            ns['_' + lname] = signal._factory_listen_method()
            if lname not in ns:
                ns[lname] = ns['_' + lname]
            ns['_' + tname] = signal._factory_trigger_method()
            if tname not in ns:
                ns[tname] = ns['_' + tname]

        # Escaneia todos os métodos decorados com @listen
        listen = {}
        for C in reversed(bases):
            listen.update(getattr(C, '__marked_listen__', {}))
        for attr, value in ns.items():
            if hasattr(value, '_listen_args'):
                for name, args, kwds in getattr(value, '_listen_args'):
                    L = listen.setdefault(name, [])
                    L.append((attr, args, kwds))

        ns['__marked_listen__'] = listen

        # Atribui valores de slots, caso necessário
        if '__slots__' in ns:
            slots = list(ns['__slots__'])
            for signal_name, signal in signals.items():
                if not isinstance(signal, DelegateSignal):
                    slots.append('_%s_ctl' % signal_name)
                    slots.append('_%s_book' % signal_name)
            ns['__slots__'] = slots

        return ns

    @classmethod
    def decorate(cls, ev_type):
        '''Decora uma classe que não inclui EventDispatcher na hierarquia e
        insere métodos/propriedades etc para que ela se comporte como um
        membro de EventDispatcher.

        Esta função pode ser útil quando EventDispatcher não pode ser inserida
        na hierarquia de classes por um conflito de metaclasses ou por um
        conflito com o campo __slots__ que previne herança múltipla.

        O método __init__ é renomeado para _init_events para poder se tornar
        acessível aos membros da classe decorada.

        Observe que classes decoradas desta maneira não são subclasses de
        EventDispatcher. Deste modo, os mecanismos de criação e registro de
        novos sinais não funcionarão automaticamente. Caso uma sub-classe
        queira definir um novo sinal, será necessário decorá-la manualmente.
        '''

        ev_type._init_events = EventDispatcher.__init__
        ev_type.listen = EventDispatcher.listen
        ev_type.trigger = EventDispatcher.trigger

        # TODO: implementar @EventDispatcherMeta.decorate
        name = ev_type.__name__
        bases = ev_type.__bases__
        ns = dict(ev_type.__dict__)
        ns = cls._populate_namespace(name, bases, ns)

        # Remove read-only attributes
        blacklist = ['__doc__', '__dict__', '__weakref__']
        for k in blacklist:
            ns.pop(k, None)

        # Write new attributes
        for k, new in ns.items():
            old = getattr(ev_type, k, None)
            if old is not new:
                try:
                    setattr(ev_type, k, new)
                except AttributeError:
                    tname = ev_type.__name__
                    msg = 'could not write %s=%r for type %s' % (k, new, tname)
                    raise ValueError(msg)
        return ev_type


@six.add_metaclass(EventDispatcherMeta)
class EventDispatcher(object):

    '''Implementa o despachante de eventos da biblioteca FGAme.'''

    __slots__ = []

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
            marked_listen = self.__marked_listen__.get(signal.name, [])
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
