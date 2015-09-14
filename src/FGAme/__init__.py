# -*- coding: utf8 -*-
'''
==========
Instalação
==========

O FGAme utiliza os mecanismos usuais para a instalação de qualquer programa em
Python. A grande dificuldade, talvez, seja instalar algumas bibliotecas
externas necessárias e realizar a compilação de módulos, em especial no
ambiente Windows.

Temos a seguinte lista de dependências:

* cython >= 0.22
* six
* smallvectors (versão de desenvolvimento)
* smallshapes (versão de desenvolvimento)
* pygeneric (versão de desenvolvimento)
* pygame (no futuro: ou sdl2, ou kivy, ou pyglet)

Todas estas bibliotecas, incluindo o FGAme, possuem suporte para Python2 e
Python3. Caso você não tenha nenhum motivo particular para escolher entre uma
das duas versões do Python, escolha a última, que é mais moderna e bem
suportada.

Linux
=====

No Ubuntu e similares, basta utilizar o comando apt-get para instalar as
dependências necessárias. Depois instale a FGAme e dependências utilizando o
Pip. Comece executando os comandos abaixo no terminal::

    $ sudo apt-get install python3-pip cython3 mercurial python3-numpy
    $ sudo apt-get install libsdl*-dev

Agora baixe a versão de desenvolvimento do Pygame
::

    $ cd ~
    $ hg clone https://bitbucket.org/pygame/pygame

E instale...
::

    $ cd pygame
    $ python3 setup.py build
    $ python3 setup.py install --user

(Note que a opção --user é facultativa e diz para realizar a instalação apenas
para o usuário atual. Caso deseje fazer a instalação para todo o sistema, omita
esta opção e re-execute o último comando incluindo ``sudo`` no ínicio.)

Agora que o Pygame foi instalado, executamos o pip para instalar as outras
dependências
::

    $ pip3 install smallvectors smallshapes pygeneric FGAme --user --pre -U

Para verificar que o FGAme foi instalado corretamente, execute os demos
usando o comando::

    $ python3 -m FGAme.demos

Bom jogo!


Outras distribuições
--------------------

A primeira parte do procedimento de instalação varia de uma distribuição para
outra.

Manjaro/Arch
    O pygame para Python3 está disponível no AUR. Execute o comando

    ::

        $ sudo pacman -S python-pip cython
        $ yaourt -S python-pygame

    e depois prossiga na instalação a partir do comando ``pip install ...``


Windows
=======

Os usuários de Windows devem baixar a versão de Python desejada (recomendamos
a versão 3.4) junto com as dependências compiladas para esta versão.
Baixe e instale os arquivos na ordem mesma ordem da lista indicada abaixo:

    * Python 3.4: `[download]`__
    * Python game para Python 3.4: `[download]`__
    * Cython: `[download]`__

.. __: https://www.python.org/downloads/
.. __: http://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame
.. __: http://www.lfd.uci.edu/~gohlke/pythonlibs/#cython

Lembre-se sempre de escolher a versão do Pygame e do Cython correspondente
à versão de Python que você utiliza e a arquitetura (x86 ou 64 bits, lembre-se
que processadores Intel de 64 bits pertencem à arquitetura amd64).

Durante a instalação do Python é conveniente acionar a opção *"Add python.exe to
PATH"*. Isto deixará o Python mais facilmente disponivel para o terminal de
comando. Caso você esqueceu desta opção ou está em uma versão nova do Windows,
é necessário executar os comandos a partir da pasta do Python.

Primeiramente abra o terminal do Windows apertando ``Win+R`` e digitando
``cmd``. Dentro do comando, vá para a pasta onde o Python foi instalado
(normalmente C:\Python34\)::

    $ cd c:\python34
    $ python -m pip install six pygeneric smallvectors smallshapes FGAme

Para abrir o terminal, pressione ``Win+R`` para abrir a caixa de executar
programas e digite ``cmd``.


Desenvolvedores
===============

Caso você queira participar do desenvolvimento da FGAme, ou está matriculado
na disciplina de Física para jogos na faculdade UnB/Gama ;), é necessário
utilizar a versão de desenvolvimento do FGAme e das bibliotecas auxiliares
*smallvectors* e *smallshapes*. Todas estas bibliotecas estão presentes no
GitHub no endereços abaixo

* `FGAme <https://github.com/fabiommendes/FGAme/>`_
* `smallvectors <https://github.com/fabiommendes/smallvectors/>`_
* `smallshapes <https://github.com/fabiommendes/smallshapes/>`_

Caso você não esteja familiarizado com o GIT e o github, este é um bom
começo: `GIT - Guia Prático <http://rogerdudler.github.io/git-guide/index.pt_BR.html/>`_.


===============
Tutorial Rápido
===============

Exemplo básico
==============

Este tutorial explica como utilizar a FGAme para a criação de jogos ou
simulações de física simples. A FGAme é um motor de jogos com ênfase na
simulação de física. Todos os objetos, portanto, possuem propriedades físicas
bem definidas como massa, momento de inércia, velocidade, etc. A simulação da
física é feita, em grande parte, de modo automático.

O primeiro passo é definir o palco que os objetos habitarão. Isto pode ser
feito instanciando um objeto da classe :class:`World`.

    >>> world = World()

A partir daí, podemos criar objetos e inserí-los na simulação

>>> obj1 = Circle(50)
>>> obj2 = Circle(50, color='red')
>>> world.add([obj1, obj2])

Para modificar as propriedades físicas dos objetos basta modificar diretamente
os atributos correspondentes. Uma lista completa de atributos pode ser
encontrada no módulo :mod:`FGAme.objects`.

>>> obj1.mass = 10
>>> obj2.mass = 20
>>> obj1.pos = (150, 50)
>>> obj1.vel = (-100, 0)

As variáveis dinâmicas podem ser modificadas diretamente, mas sempre que
possível, devemos utilizar os  métodos que realizam os deslocamentos relativos
(ex.: `.move()`, `.boost()`, etc). Estes métodos geralmente são mais
eficientes e seguros.

.. |move| replace:: :meth:`Body.move`
.. |boost| replace:: :meth:`Body.boost`
.. |rotate| replace:: :meth:`Body.rotate`
.. |aboost| replace:: :meth:`Body.aboost`

+----------+---------------+-------------------------------+---------+
| Variável | Deslocamentos | Descrição                     | Unidade |
+==========+===============+===============================+=========+
| pos      | |move|        | Posição do centro de massa    | px      |
+----------+---------------+-------------------------------+---------+
| vel      | |boost|       | Velocidade do centro de massa | px/s    |
+----------+---------------+-------------------------------+---------+
| theta    | |rotate|      | Ângulo de rotação             | rad     |
+----------+---------------+-------------------------------+---------+
| omega    | |aboost|      | Velocidade angular            | rad/s   |
+----------+---------------+-------------------------------+---------+

Aplicamos uma operação de `.move()` para movê-lo com relação à posição
anterior. Veja como fica a posição final do objeto.

>>> obj1.move(150, 0)  # deslocamento com relação à posição inicial
>>> obj1.pos
Vec(300, 50)

Para iniciar a simulação, basta chamar o comando

>>> world.run()                                                # doctest: +SKIP


Objetos dinâmicos
=================

Apesar do FGAme não fazer uma distinção explícita durante a criação, os objetos
no mundo podem ser do tipo dinâmicos, cinemáticos ou estáticos. Todos eles
participam das colisões normalmente, mas a resposta física pode ser diferente
em cada caso. Os objetos dinâmicos se movimentam na tela e respondem às forças
externas e de colisão. Os objetos cinemáticos se movimentam (usualmente em
movimento retilíneo uniforme), mas não sofrem a ação de forças. Já os objetos
estáticos simplesmente permanecem parados.

A diferenciação é feita apenas pelo valor das massas e das velocidades.
Convertemos um objeto em cinemático atribuindo um valor infinito para a massa.
Um objeto será estático se a massa for infinita e a velocidade nula.

>>> obj2.mass = 'inf' # automaticamente se torna estático pois a velocidade
...                   # é nula

O FGAme utiliza esta informação para acelerar os cálculos de detecção de
colisão e resolução de forças. As propriedades dinâmicas/estáticas dos objetos,
no entanto são inteiramente transparentes ao usuário.

Vale observar que a condição de dinâmico vs. estático pode ser atribuída
independentemente para as variáveis lineares e angulares. No segundo caso, o
controle é feito pelo valor do momento de inércia no atributo `.inertia` do
objeto. Para transformar um objeto dinâmico em inteiramente estático, seria
necessário fazer as operações

>>> obj2.mass = 'inf'
>>> obj2.inertia = 'inf'
>>> obj2.vel *= 0
>>> obj2.omega *= 0

De modo mais simples, podemos fazer todas as operações de uma vez utilizando os
métodos `.make_static()` (ou kinematic/dynamic).

>>> obj2.make_static()

Já os métodos `.is_static()` (ou kinematic/dynamic) permitem investigar se um
determinado objeto satisfaz a alugma destas propriedades.

>>> obj2.is_dynamic()
False
>>> obj2.is_static()
True

Outra alternativa é simplesmente criar o objeto com um valor infinito para a
massa

>>> obj3 = Circle(10, pos=(300, 300), mass='inf')
>>> world.add(obj3)

Lembramos que as colisões são calculadas apenas se um dos objetos envolvidos
for dinâmico. Deste modo, quando dois objetos cinemáticos ou um objeto estático
e um cinemático se encontram, nenhuma força é aplicada e eles simplemente
atravessam um pelo outro.


Aplicando forças
================

Forças externas
---------------

A FGAme se preocupa em calcular automaticamente as forças que surgem devido à
colisão, atrito, vínculos, etc. Em alguns casos, no entanto, o usuário pode
querer especificar uma força externa arbitrária que é aplicada a cada frame
em um determinado objeto.

Isto pode ser feito salvando qualquer função do tempo no atributo especial
:meth:`Body.force` dos objetos físicos. Esta força será recalculada a cada
frame em função do tempo (e implicitamente também pode depender de outras
variáveis como posição, velocidade, etc).

>>> def gravity_force(t):
...     return Vec(0, -100)
>>> obj3.force = gravity_force

Agora o círculo ``obj3`` é influenciado por uma força gravitacional. Existem
várias forças já implementadas e vários métodos mais avançados de manipular o
atributo ``.force`` que podem ser encontrados no módulo :mod:`FGAme.physics`.


Forças elementares
------------------

O método mostrado para definir forças externas na seção anterior é bastante
poderoso, mas talvez seja um bocado inconveniente para definir forças globais
como é o caso da gravidade. Normalmente queremos aplicar a gravidade à todos
(ou quase todos) objetos do mundo simultaneamente e o método descrito
anteriormente seria bastante inconveniente. A FGAme permite configurar as
forças de gravidade e forças viscosas lineares e angulares de maneira global.

Na realidade, não definimos as forças diretamente, mas sim as acelerações que
elas provocam em cada objeto. São as constantes `gravity`, `damping` e
`adamping`. As forças são criadas a partir da fórmula::

    F = obj.mass * (gravity - obj.vel * damping)

E o torque é gerado por::

    tau = -obj.inertia * adamping *  obj.omega

Estas constantes podem ser definidas globalmente num objeto do tipo ``World``
ou individualmente caso um objeto queira ter um comportamento diferente do
global.

>>> world.gravity = (0, -50)
>>> world.adamping = 0.1
>>> obj2.gravity = (0, 50)  # objeto 2 cai para cima!

Todos objetos que não definirem explicitamente o valor destas constantes
assumirão os valores definidos no mundo no qual estão inseridos.


Simulação simples
=================

Uma simulação de física pode ser criada facilmente adicionando objetos a uma
instância da classe World(). O jeito mais recomendado, no entanto, é criar uma
subclasse pois isto melhora a organização do código e a sanidade do
desenvolvedor. No exemplo abaixo, montamos um sistema "auto-gravitante" onde as
duas massas estão presas entre si por molas

::

    from FGAme import *

    class GravityWorld(World):

        def init(self):
            # Criamos dois objetos
            A = Circle(20, pos=pos.from_middle(100, 0), vel=(100, 300),
                       color='red')
            B = Circle(20, pos=pos.from_middle(-100, 0), vel=(-100, -300))
            self.A, self.B = A, B
            self.add([A, B])

            # Definimos a força de interação entre ambos
            K = self.K = A.mass
            self.A.force = lambda t: -K * (A.pos - B.pos)
            self.B.force = lambda t: -K * (B.pos - A.pos)

            # Redefinimos a constante de amortecimento
            self.damping = 0.5

Agora que temos uma classe mundo definida, basta iniciá-la com o comando

::

    if __name__ == '__main__':
        world = GravityWorld()
        world.run()


Interação com o usuário
=======================

Até agora vimos apenas como controlar os parâmetros de simulação física. É
lógico que em um jogo deve ser existir alguma forma de interação com o usuário.
Na FGAme, esta interação é controlada a partir da noção de eventos e callbacks.
É possível registrar funções que são acionadas sempre que um determinado evento
ocorre. Eventos podem ser disparados pelo usuário (ex.: apertar uma tecla),
ou pela simulação (ex.: ocorrência de uma colisão).

Digamos que a simulação deva pausar ou despausar sempre que a tecla de espaço
for apertada. Neste caso, devemos ligar o evento "apertou a tecla espaço"
com a função `.toggle_pause()` do mundo, que alterna o estado de pausa da
simulação.

>>> on_key_down('space', world.toggle_pause)               # doctest: +ELLIPSIS
(...)

A tabela abaixo mostra os eventos mais comuns e a assinatura das funções de
callback

.. |kd| replace:: ``key-down``
.. |ku| replace:: ``key-up``
.. |lp| replace:: ``long-press``
.. |mm| replace:: ``mouse-motion``
.. |md| replace:: ``mouse-button-down``
.. |mu| replace:: ``mouse-button-up``
.. |ml| replace:: ``mouse-long-press``

+-------------+-----------+---------------------------------------------------+
| Evento      | Argumento | Descrição                                         |
+=============+===========+===================================================+
| |kd|        | tecla     | Chamado no frame que uma tecla é pressionada.     |
|             |           | O argumento pode ser um objeto 'tecla', que       |
|             |           | depende do back end utilizado ou uma string,      |
|             |           | que é portável para todos back ends.              |
|             |           |                                                   |
|             |           | A string corresponde à tecla escolhida. Teclas    |
|             |           | especiais podem ser acessadas pelos seus nomes    |
|             |           | como em 'space', 'up', 'down', etc.               |
|             |           |                                                   |
|             |           | Os callbacks do tipo 'key-down' são funções que   |
|             |           | não recebem nenhum argumento.                     |
+-------------+-----------+---------------------------------------------------+
| |ku|        | tecla     | Como em 'key-down', mas é executado no frame em   |
|             |           | que a tecla é liberada pelo usuário.              |
+-------------+-----------+---------------------------------------------------+
| |lp|        | tecla     | Semelhante aos anteriores, mas é executado em     |
|             |           | *todos* os frames em que a tecla se mantiver      |
|             |           | pressionada.                                      |
+-------------+-----------+---------------------------------------------------+
| |mm|        | nenhum    | Executado sempre que o ponteiro do mouse estiver  |
|             |           | presente na tela.                                 |
|             |           |                                                   |
|             |           | O callback é uma função que recebe um vetor com a |
|             |           | posição do mouse como primeiro argumento.         |
+-------------+-----------+---------------------------------------------------+
| |md|        | botão     | Semelhante aos eventos de 'key-down', 'key-up' e  |
| |mu|        |           | 'long-press'. Deve ser registrada com 'left',     |
| |ml|        |           | 'right', 'middle', 'wheel-up' ou 'wheel-down'.    |
|             |           |                                                   |
|             |           | A grande diferença está em que o callback recebe  |
|             |           | a posição do ponteiro do mouse como primeiro      |
|             |           | argumento.                                        |
|             |           |                                                   |
+-------------+-----------+---------------------------------------------------+

Um método prático de definir associar um método de uma classe a um evento
especifico é utilizar o decorador ``@listen``. Funciona de maneira semelhante
às funções :func:`on_key_down`, :func:`on_key_up`, etc, mas exige um sinal
como primeiro argumento.

::

    class GravityWorld(World):
        ...

        @listen('key-down', 'space')
        def toggle(self):
            self.toggle_pause()

        @listen('long-press', 'right')
        def move_right(self):
            self.A.move(5, 0)

        @listen('long-press', 'left')
        def move_left(self):
            self.A.move(-5, 0)

        @listen('long-press', 'up')
        def move_up(self):
            self.A.move(0, 5)

        @listen('long-press', 'down')
        def move_down(self):
            self.A.move(0, -5)


Pronto! Agora você já sabe o básico para criar um jogo ou simulação
simples utilizando a FGAme. Nas próximas seções vamos revisar com mais
detalhes como a FGAme funciona e os princípios gerais de implementação e
organização de um motor de jogos orientado à física.

=======================
Tutorial avançado: Pong
=======================



================================
Motores de jogos: uma introdução
================================

Foi-se o tempo em que os jogos cairam na categoria de programação heróica: os
pioneiros precisavam implementar todas as funcionalidades básicas, tais como
escrever os pixels na tela, interagir com os dispositivos de entrada, controle
do tempo, drivers de dispositivo, etc. Na medida que os computadores evoluíram,
cada vez mais as tarefas comuns na implementação de jogos foram movidas para
bibliotecas/frameworks especializados deixando os desenvolvedores muito mais
focados nos aspectos criativos.

Um motor de jogo idealmente deve chegar neste ponto: o desenvolvedor liga as
peças e define a lógica do jogo, mas sem se preocupar com os detalhes mais
baixos da implementação. Por isto, motores de jogos modernos podem se tornar
componentes extremamente sofisticados que chegam literalmente a possuir milhões
de linhas de código.

A FGAme, obviamente, é um projeto muito simples e foi desenvolvido com um
intuito muito mais pedagógico que comercial: os objetivos principais são
ensinar conceitos de física para programadores, mostrar alguns princípios
práticos de desenvolvimento de motores para jogos (especialmente jogos voltados
para física) e servir como um motor de fácil utilização para a criação de jogos
educativos.

Começamos pincelando de forma geral o que um motor de jogos deve ser capaz de
fazer e como isso normalmente se configura em termos de arquitetura de
software.

Desenhando na tela
==================

Um motor de jogos que se preze deve ser capaz de, no mínimo, capturar as
entradas do usuário e desenhar os elementos de jogo na tela (e talvez coordenar
outras formas de saída tais como audio, rede, acelerômetros, etc).

De forma bem genérica, podemos pensar que a maioria dos jogos é implementada
da seguinte maneira::

    # Inicializa o estado do aplicativo (configura hardware, lê arquivos de
    # configuração, savegames, etc)
    inicializa()

    while True:
        # Obtêm as entradas do usuário tais como cliques do mouse, teclas
        # digitadas, etc.
        lê_inputs()

        # Atualiza estado de jogo (ex: move personagens, calcula pontos, danos,
        # colisões, etc)
        atualiza_frame()

        # Redesenha algum pedaço da tela que precise de atualização
        # (possivelmente controla outros sub-sistemas como sons, rede, etc)
        desenha()

Vamos começar então com o mais básico possível, que é criar um "quase-jogo" que
simplesmente desenha alguns objetos simples na tela. A FGAme pode utilizar
vários métodos diferentes de renderização, mas por padrão, isto é feito com
auxílio do SDL no C via a biblioteca **pygame**. Entender o funcionamento da
SDL é importante para o desenvolvedor avançado pois vários jogos e motores de
jogos são baseados nesta tecnologia e sua arquitetura é bastante convencional.
Como se trata de um tópico sofisticado e queremos evitar a linguagem C/C++,
vamos pular esta parte.

O primeiro passo da nossa tarefa é iniciar o a tela. Isto é feito criando um
objeto do tipo "Screen" que guarda as informações básicas sobre a renderização
e é capaz de modificar os pixels na tela.

>>> from FGAme import conf
>>> screen = conf.init_screen(800, 600)                        # doctest: +SKIP

Observe que a mesma variável pode ser recuperada posteriormente utilizando a
função `conf.get_screen()`.

>>> screen = conf.get_screen()        # ==> objeto screen defindo anteriormente

Este código inicializa uma janela de 800 x 600 pixels e retorna o objeto
"screen" que é utilizado para manipular e desenhar a tela. A janela é iniciada
escondida. Podemos pedir explicitamente para mostrá-la, fazendo com que uma
janela em branco apareça (e logo suma!)

>>> screen.show()                                              # doctest: +SKIP

O objeto screen é implementado em analogia a uma tela de pintura: mas no caso
trata-se de uma tela de pixels. O método draw() desenha figuras geométricas ou
imagens. Para pintar um círculo, por exemplo, criamos um objeto do
tipo :cls:`FGAme.draw.Circle` e depois chamamos o método apropriado

>>> from FGAme import draw
>>> circle = draw.Circle(100, color='red')
>>> screen.draw(circle)

Observe que as imagens não são atualizadas imediatamente. Isto ocorre porque a
imagem é armazenada temporariamente na memória do computador e só é enviada
para a tela quando exigimos esta operação explicitamente. Para isto, basta
chamar o método flip() no fim da seção de desenho.

>>> screen.flip()                                              # doctest: +SKIP

Uma maneira conveniente de fazer isto, é utilizar o objeto scren dentro de
um bloco with(). Ao final do bloco, a função flip() será chamada
automaticamente.

>>> c1 = draw.Circle(50, pos=(400, 300), color='black')
>>> c2 = draw.Circle(30, pos=(400, 300), color='white')
>>> with screen.autoflip():                                    # doctest: +SKIP
...     screen.draw(c1)
...     screen.draw(c2)

Agora vemos os dois círculos pintados na tela.

==========
Referência
==========

Módulos da FGAme
================

Configuração (FGAme.conf)
-------------------------

.. automodule:: FGAme.conf
    :members:
    :member-order: bysource

Objetos e mundo
---------------


Física e colisões
-----------------


Funções matemáticas
-------------------


Tópicos avançados
=================

Eventos
-------

.. automodule:: FGAme.events
    :members: EventDispatcher, signal, listen


Anatomia de uma colisão
-----------------------

Loop principal
--------------

'''

from FGAme.meta import __version__, __author__
from FGAme import conf
from FGAme import mathtools as math
from FGAme.input import *
from FGAme.mathtools import Vec, pi
from FGAme import draw
from FGAme.events import listen, signal, EventDispatcher
from FGAme.core import *
from FGAme import physics
from FGAme.physics import *
from FGAme.world import World
from FGAme.objects import *
from FGAme.app import *
from FGAme.extra.orientation_objects import *
from FGAme.mainloop import *
del MainLoop

if __name__ == '__main__':
    import doctest
    doctest.testmod()
