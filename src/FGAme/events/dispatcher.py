from FGAme.events.base import EventDispatcher
from FGAme.events.util import pyname, signal
from FGAme.events.signals import DelegateSignal


class GlobalEventDispatcher(EventDispatcher):

    '''
    Classe cria uma única instância em FGAme.dispatcher que controla os eventos
    globais da FGAme.
    '''
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            new = object.__new__(cls)
            new.__init__()
            new._delegate_idx = 0
            new._delegates = {}
            return new
        else:
            return cls.__instance

    def new_signal(self, name, *filters, **kwds):
        '''Cria um novo sinal para o evento global.

        Possui uma assinatura variável onde o tipo de sinal é escolhido
        automaticamente a partir dos argumentos

        signal('foo', num_args=1)
            Sinal simples chamado 'foo' com apenas 1 argumento.

        signal('foo', 'bar')
            Sinal filtrado chamado 'foo' que requer um argumento extra 'bar'

        signal('foo', delegate_to=obj)
            Delega sinal 'foo' para o objeto fornecido em *delegate_to*
        '''

        cls = type(self)
        attr = pyname(name)

        # Organiza delegações e salva delegado em atributo
        if 'delegate_to' in kwds:
            delegate_obj = kwds['delegate_to']
            try:
                delegate_attr = self._delegates[id(delegate_obj)]
            except KeyError:
                delegate_attr = '_delegate_%s' % self._delegate_idx
                self._delegates[id(delegate_obj)] = delegate_attr
                self._delegate_idx += 1
            setattr(self, delegate_attr, delegate_obj)
            kwds['delegate_to'] = delegate_attr

        # Cria sinal
        signal_obj = signal(name, *filters, **kwds)
        if name in cls.__signals__:
            raise ValueError('global signal already exists: %r' % name)
        cls.__signals__[attr] = signal_obj
        setattr(cls, pyname(name), signal_obj)

        # Cria os métodos do tipo listen_<> e tipo trigger_<>
        lname = 'listen_' + attr
        tname = 'trigger_' + attr
        listen_method = signal_obj._factory_listen_method()
        trigger_method = signal_obj._factory_trigger_method()
        setattr(cls, lname, listen_method)
        setattr(cls, tname, trigger_method)

        # Inicializa SignalCtl
        ctl = signal_obj.default_control()
        setattr(self, '_%s_ctl' % attr, ctl)
        if not isinstance(signal, DelegateSignal):
            setattr(self, '_%s_book' % attr, ctl._runner)


dispatcher = GlobalEventDispatcher()
