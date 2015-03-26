# -*- coding: utf8 -*-
'''
===================
Controle de eventos
===================

O controle de despacho de mensagens e eventos é centralizado na classe
EventDispatcher deste módulo. Ela controla a transmissão de "mensagens" ou
eventos entre objetos implementado o padrão "observador", onde um objeto pode
anunciar eventos e outros objetos podem se registrar a estes eventos e
responder apropriadamente quando estes eventos forem disparados.

Este mecanismo é utilizado para desacoplar o código de diferentes partes do
motor de jogos e é essencial para manter o código organizado e compreensivel.
Um exemplo típico da utilidade do despachante de eventos se dá na implementação
da resposta às entradas do usuário. Uma parte do motor de jogos deve ser
dedicada a ler os comandos de teclado, mouse, etc. Ao invés de responder
explicitamente à cada interação, o sistema de entrada simplesmente anuncia algo
do tipo: *a tecla
"p" foi pressionada*. Todos os objetos que estiverem registrados para ouvir
este evento serão notificados (e assim chamando a função de callback()
apropriada).

O sinais associados a cada objeto são definidos durante a criação da classe.
Vamos começar criando uma classe que define alguns sinais simples.

>>> class Foobar(EventDispatcher):
...     foo = Signal('foo')
...     bar = Signal('bar')

Um objeto da classe Foobar() pode disparar os sinais apropriados utilizando
os métodos `.trigger_foo()` ou `.trigger_bar()` ou simplesmente o método
genérico `.trigger('nome')`

>>> x = Foobar()
>>> x.trigger_foo()     # aciona o sinal foo
>>> x.trigger('bar')    # aciona o sinal bar

Os métodos `trigger_<nome do sinal>()` são ligeiramente mais eficientes e
são criados automaticamente pelo construtor das classes do tipo
EventDispatcher. Sub-classes podem personalizar esses métodos, mas é
potencialmente complicado difícil e raramente é necessário.

`x.trigger(...)` por enquanto não produz nenhum efeito pois não há objetos
ouvindo algum sinal de x. Podemos registrar o interesse em um determinado sinal
utilizando o método `x.listen()`, passando uma função que toma uma ação de
resposta a esses sinais.

>>> def handler(*args, **kwds):
...     print('called with args=%s, kwargs=%s' % (args, kwds))

Novamente, aqui existem duas interfaces análogas ao método trigger*()

>>> id1 = x.listen_foo(handler)
>>> id2 = x.listen('bar', handler)
...

Assim como antes, `.listen(nome, ...)` simplesmente chama a função
apropriada `.listen_nome(...)`. Isto pode ser utilizado em sub-classes para
personalizar o comportamento de como cada sinal é registrado ou executado.

O sinais disparados por `x` agora invocam a função `handler` definida
anteriormente.

>>> x.trigger_bar()
called with args=(), kwargs={}

Também podemos registrar as funções com argumentos adicionais que serão
repassados quando elas forem invocadas pelo disparo de um sinal.

>>> id3 = x.listen('foo', handler, 'pos_arg', kw_arg=None)

Primeiramente x.trigger_foo() invocará a função "handler" sem argumentos (como
acontecia anteriormente) e em seguida executará esta mesma função com os dois
argumentos adicionais registrados no bloco acima. Deste modo,

>>> x.trigger_foo()
called with args=(), kwargs={}
called with args=('pos_arg',), kwargs={'kw_arg': None}

Finalmente, o objeto x.foo (ou, analogamente, x.bar) permite controlar
explicitamente as funções registradas sob cada sinal e algumas
características de seu comportamento.

>>> x.foo.handlers                                         # doctest: +ELLIPSIS
[<function handler at 0x...>, <function handler at 0x...>]
>>> x.foo.handlers_full                                    # doctest: +ELLIPSIS
[(<function handler at 0x...>, (), {}), ...]
>>> x.foo.remove(handler=handler)

O último método, por exemplo, remove todas as respostas associadas ao sinal
"foo" implementadas pela função handler.

>>> x.trigger_foo()

É possível remover funções usando diversos critérios, mas o mais seguro é
utilizar o valor de saída do método `.listen()` que identifica cada função de
forma única.

>>> x.bar.remove(id=id2)
>>> x.trigger_bar()

Até aqui, consideramos apenas funções chamadas sem argumentos para responder
aos sinais. Sinais podem ser declarados com um segundo argumento `num_args`
para definir o número de argumentos que devem ser passados para os métodos
trigger*.

>>> class Foobar(EventDispatcher):
...     foo = Signal('foo', num_args=0)
...     bar = Signal('bar', num_args=1)

Neste caso, o sinal "foo" continua funcionando como anteriormente, mas o sinal
"bar" precisa de um argumento adicional.

>>> x = Foobar()
>>> id1 = x.listen('bar', handler)

Agora o sinal "bar" deve ser disparado com um argumento posicional

>>> x.trigger_bar(0)
called with args=(0,), kwargs={}

Disparar o sinal com o número errado de argumentos provoca um TypeError

>>> x.trigger_bar()
Traceback (most recent call last):
...
TypeError: trigger_method() missing 1 required positional argument: 'arg'

Caso se registre um método com argumentos posicionais, assumimos que estes
serão passados *após* os argumentos obrigatórios.

>>> id2 = x.listen('bar', handler, 1)
>>> x.trigger_bar(0)
called with args=(0,), kwargs={}
called with args=(0, 1), kwargs={}

Sinais filtrados
================

Até agora, o método trigger('sinal', *args) aceitam argumentos posicionais que
são passados diretamente para o argumento das funções do tipo "handler".
Sinais filtrados permitem passar argumentos para a função trigger que irão
determinar quais handlers serão chamados posteriormente.

Uma aplicação natural para essa idéia é o controle de eventos do teclado. Em
determinadas situações, um objeto pode querer ouvir todos os eventos de tecla
pressionada para, por exemplo, registrar o que o usuário digitou na tela.
Existem objetos, no entanto, que podem estar interessados apenas em algumas
combinações de teclas e desejam ouvir apenas teclas específicas. Sinais que
permitem fazer este tipo de distinção são aqui denominados sinais filtrados.

Considere o exemplo abaixo

>>> class Foobar(EventDispatcher):
...     foo = FilteredSignal('key-up')
>>> x = Foobar()

Agora devemos registrar os sinais de foo com um argumento adicional

>>> def handler(*args, **kwds):
...     print('called with args=%s, kwargs=%s' % (args, kwds))
>>> id1 = x.listen('key-up', '<return>', handler)
>>> id2 = x.listen('key-up', '<space>', handler, 'spaced')

Podemos disparar o evento especificando o filtro a ser aplicado

>>> x.trigger_key_up('<return>')
called with args=(), kwargs={}
>>> x.trigger_key_up('<space>')
called with args=('spaced',), kwargs={}

Se não houver nenhum handler registrado para aquele filtro, então nada acontece

>>> x.trigger_key_up('other')

É possível definir "handlers" que atuam em todas as chamadas do sinal 'key-up',
independentemente do segundo argumento. Neste caso, o segundo argumento é
passado para o "handler" que decide então que fazer. Para isto, basta invocar
a função listen com None como filtro.

>>> id3 = x.listen('key-up', None, handler)
>>> x.trigger_key_up('<return>')
called with args=(), kwargs={}
called with args=('<return>',), kwargs={}

Caso a função não tenha handlers registrados, somente estes handlers genéricos
serão executados

>>> x.trigger_key_up('other')
called with args=('other',), kwargs={}

Quando registramos um novo handler, a ordem de execução é mantida como se os
handlers genéricos já tivessem sido registrados anteriormente para todas as
combinações de filtros possíveis.

>>> id4 = x.listen('key-up', 'other', handler, foo='bar')
>>> x.trigger_key_up('other')
called with args=('other',), kwargs={}
called with args=(), kwargs={'foo': 'bar'}

Subclasses
==========

Subclasses de EventDispatcher podem implementar métodos que são registrados
automaticamente pelo mecanismo listen() durante a inicialização dos objetos.
Para isto, basta utilizar a convenção de nomer os métodos como
`on_<nome do sinal>()`.

>>> class Foobar(EventDispatcher):
...     foo = Signal('foo')
...     bar = FilteredSignal('bar')
...
...     def on_foo(self):
...         print('foo triggered!')
...
...     def on_bar(self, key):
...         print('bar triggered with %s!' % key)

Deste modo, os métodos on_foo e on_bar já estão registrados pelo construtor da
classe Foobar para ouvir os respectivos sinais.

>>> x = Foobar()
>>> x.trigger_foo()
foo triggered!
>>> x.trigger_bar(0)
bar triggered with 0!

Uma maneira alternativa de atingir um resultado semelhante é utilizar o
decorador @listen. Deste modo, podemos atribuir handlers à sinais de forma
explicita no tempo de construção da classe. Este método é um pouco mais
flexível que o on_<sinal>() pois permite especifica filtros para sinais
filtrados.

>>> class Foobar(EventDispatcher):
...     foo = Signal('foo')
...     bar = FilteredSignal('bar')
...     foobar = FilteredSignal('foobar')
...
...     @listen('foo')
...     def func1(self):
...         print('foo triggered!')
...
...     @listen('bar', 0)
...     @listen('bar', 1)
...     def func2(self):
...         print('bar triggered!')
...
...     @listen('foobar')
...     def func3(self, key):
...         print('foobar triggered with %s!' % key)



Agora o método func1() foi atribuído ao sinal 'foo' e o método func2() é
executado quando 'bar' é disparado com os valores 0 ou 1.

>>> x = Foobar()
>>> x.trigger_foo()
foo triggered!
>>> x.trigger_bar(0)
bar triggered!
>>> x.trigger_bar(2)
>>> x.trigger_foobar(3)
foobar triggered with 3!

Sinais delegados
================

As vezes é interessante expor um evento ao usuário mesmo quando a classe não
pode ser responsável por dispará-lo. Sinais delegados fazem justamente isso:
sempre que o usuário registrar um handler, ele delegará o registro para um
atributo específico da classe. Considere o exemplo mais concreto:

>>> class Foo(EventDispatcher):
...      do_foo = signal('do-foo', num_args=1)

A classe Foo é responsável por acionar os sinais 'do-foo'. Agora criamos uma
classe Bar que delega o sinal 'do-foo' para um atributo.

>>> class Bar(EventDispatcher):
...     def __init__(self, foo):
...         self._foo = foo
...
...     do_foo = signal('do-foo', delegate_to='_foo')

Agora criamos um objeto e registramos um handler

>>> foo = Foo()
>>> bar = Bar(foo)
>>> id1 = bar.listen('do-foo', handler)

Observe que bar não pode acionar diretamente o evento 'do-foo', mas temos que
fazer isto via o objeto originalmente responsável pelo evento

>>> bar.trigger_do_foo(0)
Traceback (most recent call last):
...
RuntimeError: signals can only be trigged by the owner

>>> foo.trigger_do_foo(0)
called with args=(0,), kwargs={}


Funções auxiliares
==================

Na maioria das vezes, não é necessário explicitar qual tipo de sinal deve ser
utilizado


'''

from functools import partial
from collections import namedtuple
from FGAme.util import six

ControlElem = namedtuple('ControlElem', ['idx', 'owner', 'wrapped', 'handler',
                                         'args', 'kwargs'])


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


###############################################################################
#                          Classes de sinais
###############################################################################


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

    def default_control(self):
        '''Retorna o objeto tipo SignalCtl apropriado para essa classe de
        sinais'''

        return SignalCtl(self)

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
                handler,
                args,
                kwargs,
                pre_args=signal.num_args)
            ctl = getattr(self, '_%s_ctl' % pyname(signal.name))

            if signal._num_filters == 0:
                idx = len(ctl._control)
                elem = ControlElem(idx, owner, wrapped, handler, args, kwargs)
                ctl.book.append(wrapped)
                ctl._control.append(elem)
                return idx

            elif signal._num_filters == 1:
                key = filter_args[0]
                ids = {}

                if key is None:
                    # Registra como handler de todas os filtros no livro
                    for k in ctl.book:
                        if k is None:
                            continue
                        wrapped_i = wrap_handler(handler, (k,) + args, kwargs,
                                                 pre_args=signal.num_args)
                        ids[k] = listen_method(self, k, wrapped_i)

                    # Cria um elemento de controle substituindo o campo
                    # "wrapped" pelo dicionário das ids em cada filtro
                    control = ctl._control.setdefault(None, [])
                    book = ctl.book.setdefault(None, [])
                    idx = len(control)
                    elem = ControlElem(idx, owner, ids, handler, args, kwargs)
                    control.append(elem)
                    book.append(
                        wrap_handler(
                            handler,
                            args,
                            kwargs,
                            pre_args=signal.num_args))

                    return (None, idx)
                else:
                    try:
                        idx = len(ctl._control[key])
                    except KeyError:
                        ctl._control[key] = []
                        ctl.book[key] = []

                        for ctl_e in ctl._control.get(None, []):
                            wrapped_i = wrap_handler(
                                ctl_e.handler,
                                (key,
                                 ) + ctl_e.args,
                                ctl_e.kwargs,
                                signal.num_args)
                            ctl_e.wrapped[key] = listen_method(
                                self,
                                key,
                                wrapped_i)

                        idx = len(ctl._control[key])

                    elem = ControlElem(
                        idx,
                        owner,
                        wrapped,
                        handler,
                        args,
                        kwargs)
                    ctl.book[key].append(wrapped)
                    ctl._control[key].append(elem)
                    return key, idx

            else:
                book = ctl.book[filter_args]
                control = ctl._control[filter_args]
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

    def default_control(self):
        return SignalCtlMulti(self)

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


###############################################################################
#                     Atributos de controle de sinais
###############################################################################

class SignalCtl(object):

    '''A classe SignalCtl implementa uma interface para gerenciar os handlers
    registrados para um determinado sinal'''

    def __init__(self, signal):
        self._signal = signal
        self._control = []
        self.book = []

    @property
    def name(self):
        return self._signal.name

    @property
    def handlers(self):
        return [ctl.handler for ctl in self._control if ctl is not None]

    @property
    def handlers_full(self):
        return [(ctl.handler, ctl.args, ctl.kwargs)
                for ctl in self._control if ctl is not None]

    @property
    def owners(self):
        return [ctl.owner for ctl in self._control if ctl is not None]

    def remove(self, **kwds):
        if len(kwds) != 1:
            raise TypeError('must specify exactly one criteria')

        key, value = kwds.popitem()
        if key == 'id':
            i = value
            wrapped = self._control[i].wrapped
            w_idx = [i for i, w in enumerate(self.book) if w is wrapped]
            if len(w_idx) > 1:
                raise NotImplementedError

            del self.book[w_idx[0]]
            self._control[i] = None

        elif key == 'handler':
            for i, ctl in enumerate(self._control):
                if ctl.handler == value:
                    self.remove(id=i)

        elif key == 'owner':
            for i, ctl in enumerate(self._control):
                if ctl.owner == value:
                    self.remove(id=i)

        else:
            raise TypeError('invalid argument: %s' % key)


class SignalCtlMulti(SignalCtl):

    '''Gerencia handlers de sinais filtrados'''

    # TODO: talvez implementar como um dicionario de SignalCtl

    def __init__(self, signal):
        super(SignalCtlMulti, self).__init__(signal)
        self.book = {}
        self._control = {}


###############################################################################
#              Classe mãe para objetos que aceitam event dispatch
###############################################################################


class EventDispatcherMeta(type):

    '''Meta-classe para EventDispatcher.

    Fabrica e registra automaticamente os métodos liste_* e trigger_*. Salva
    algumas constantes úteis obtidas por introspecção e  Além disto, atualiza
    os __slots__ caso a classe filho os utilize.'''

    def __new__(cls, name, bases, ns):
        ns = cls._populate_namespace(name, bases, ns)
        return type.__new__(cls, name, bases, ns)

    @classmethod
    def _populate_namespace(cls, name, bases, ns):
        ns = dict(ns)

        # Lê os sinais e monta um dicionário de sinais
        signals = {}
        for C in reversed(bases):
            signals.update(getattr(C, '_signals', {}))
        for attr, value in ns.items():
            if isinstance(value, Signal):
                signals[attr] = value
        ns['_signals'] = signals

        # Cria os métodos do tipo listen_* e tipo trigger_*
        for signal in signals.values():
            lname = 'listen_' + pyname(signal.name)
            tname = 'trigger_' + pyname(signal.name)
            if lname not in ns:
                ns[lname] = ns['_' + lname] = signal._factory_listen_method()
            if tname not in ns:
                ns[tname] = ns['_' + tname] = signal._factory_trigger_method()

        # Escaneia todos os métodos decorados com @listen
        listen = {}
        for C in reversed(bases):
            signals.update(getattr(C, '_listen', {}))
        for attr, value in ns.items():
            if hasattr(value, '_listen_args'):
                for name, args, kwds in getattr(value, '_listen_args'):
                    L = listen.setdefault(name, [])
                    L.append((attr, args, kwds))

        ns['_listen'] = listen

        # Atribui valores de slots, caso necessário
        if '__slots__' in ns:
            slots = list(ns['__slots__'])
            for signal in signals:
                slots.append('_%s_ctl' % signal)
                slots.append('_%s_book' % signal)
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
        ev_type._listen = EventDispatcher.listen
        ev_type._trigger = EventDispatcher.trigger

        # TODO: implementar @EventDispatcherMeta.decorate
        return ev_type


@six.add_metaclass(EventDispatcherMeta)
class EventDispatcher(object):

    '''Implementa o despachante de eventos da biblioteca FGAme.'''

    __slots__ = []

    def __init__(self):
        for signal in self._signals.values():
            ctl = signal.default_control()
            setattr(self, '_%s_ctl' % pyname(signal.name), ctl)
            if not isinstance(signal, DelegateSignal):
                setattr(self, '_%s_book' % pyname(signal.name), ctl.book)

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
            for (func_name, args, kwargs) in self._listen.get(signal.name, []):
                handler = getattr(self, func_name)
                filters = args[
                    :signal._num_filters] or (
                    None,
                ) * signal._num_filters
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


###############################################################################
#                    Funções úteis e decoradores
###############################################################################

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

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
