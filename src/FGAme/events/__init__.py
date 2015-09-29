# -*- coding: utf-8 -*-
'''
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
do tipo: *a tecla "p" foi pressionada*. Todos os objetos que estiverem
registrados para ouvir este evento serão notificados (e assim chamando a função
de callback() apropriada).

O sinais associados a cada objeto são definidos durante a criação da classe.
Vamos começar criando uma classe que define alguns sinais simples.

>>> class Foobar(EventDispatcher):
...     foo = signal('foo')
...     bar = signal('bar')

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
>>> x.foo.remove(handler=handler)                          # doctest: +ELLIPSIS
[...]

O último método, por exemplo, remove todas as respostas associadas ao sinal
"foo" implementadas pela função handler.

>>> x.trigger_foo()

É possível remover funções usando diversos critérios, mas o mais seguro é
utilizar o valor de saída do método `.listen()` que identifica cada função de
forma única. O método remove() sempre retorna uma lista com todos os handlers
removidos.

>>> rm_list = x.bar.remove(id=id2)
>>> x.trigger_bar()

Como podemos ver, a lista está vazia e x.trigger_bar() não produz nada. É
possível reintroduzir todos estes handlers usando o método .restore() do sinal.

>>> x.bar.restore(rm_list)
>>> x.trigger_bar()
called with args=(), kwargs={}


Até aqui, consideramos apenas funções chamadas sem argumentos para responder
aos sinais. Sinais podem ser declarados com um segundo argumento `num_args`
para definir o número de argumentos que devem ser passados para os métodos
trigger*.

>>> class Foobar(EventDispatcher):
...     foo = signal('foo', num_args=0)
...     bar = signal('bar', num_args=1)

Neste caso, o sinal "foo" continua funcionando como anteriormente, mas o sinal
"bar" precisa de um argumento adicional.

>>> x = Foobar()
>>> id1 = x.listen('bar', handler)

Agora o sinal "bar" deve ser disparado com um argumento posicional

>>> x.trigger_bar(0)
called with args=(0,), kwargs={}

Disparar o sinal com o número errado de argumentos provoca um TypeError

>>> x.trigger_bar()                         # doctest: +IGNORE_EXCEPTION_DETAIL
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
...     foo = signal('key-up', 'key')
>>> x = Foobar()

Agora devemos registrar os sinais de foo com um argumento adicional 'key'

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
...     foo = signal('foo')
...     bar = signal('bar', 'key')
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
...     foo = signal('foo')
...     bar = signal('bar', 'key')
...     foobar = signal('foobar', 'key')
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

Criamos um objeto e registramos um handler

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

A principal vantagem de delegar um sinal está no processo de destruição do
mesmo. Se chamarmos a função destroy_handlers() do objeto bar, todos os sinais
atribuídos a ele serão limpados, inclusive aqueles delegados para ``foo``. Isto
permite um controle mais granular sobre quem possui a referência sobre cada
sinal.pyname

>>> bar.destroy_handlers()                                 # doctest: +ELLIPSIS
{...}
>>> foo.do_foo.handlers
[]
'''

__package__ = 'FGAme.events'
if __name__ == '__main__':
    import FGAme


from .util import listen, signal
from .base import EventDispatcher, EventDispatcherMeta
from .dispatcher import dispatcher

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
