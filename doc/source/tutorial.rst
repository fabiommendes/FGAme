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

O primeiro passo é definir o palco que os objetos habitarão. Isto pode ser feito
instanciando um objeto da classe :class:`World`.

    >>> world = World()

A partir daí, podemos criar objetos e inserí-los na simulação

    >>> obj1 = Circle(50) >>> obj2 = Circle(50, color='red') >>>
    world.add([obj1, obj2])

Para modificar as propriedades físicas dos objetos basta modificar diretamente
os atributos correspondentes. Uma lista completa de atributos pode ser
encontrada no módulo :mod:`FGAme.objects`.

    >>> obj1.mass = 10 >>> obj2.mass = 20 >>> obj1.pos = (150, 50) >>>
    obj1.vel = (-100, 0)

As variáveis dinâmicas podem ser modificadas diretamente, mas sempre que
possível, devemos utilizar os  métodos que realizam os deslocamentos relativos
(ex.: `.move()`, `.boost()`, etc). Estes métodos geralmente são mais eficientes
e seguros.

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

    >>> obj1.move(150, 0)  # deslocamento com relação à posição inicial >>>
    obj1.pos Vec(300, 50)

Para iniciar a simulação, basta chamar o comando

    >>> world.run()                                            # doctest:
    +SKIP


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

    >>> obj2.mass = 'inf' # automaticamente se torna estático pois a
    velocidade ...                   # é nula


O FGAme utiliza esta informação para acelerar os cálculos de detecção de colisão
e resolução de forças. As propriedades dinâmicas/estáticas dos objetos, no
entanto são inteiramente transparentes ao usuário.

Vale observar que a condição de dinâmico vs. estático pode ser atribuída
independentemente para as variáveis lineares e angulares. No segundo caso, o
controle é feito pelo valor do momento de inércia no atributo `.inertia` do
objeto. Para transformar um objeto dinâmico em inteiramente estático, seria
necessário fazer as operações

    >>> obj2.mass = 'inf' >>> obj2.inertia = 'inf' >>> obj2.vel
    *= 0 >>> obj2.omega *= 0

De modo mais simples, podemos fazer todas as operações de uma vez utilizando os
métodos `.make_static()` (ou kinematic/dynamic).

    >>> obj2.make_static()

Já os métodos `.is_static()` (ou kinematic/dynamic) permitem investigar se um
determinado objeto satisfaz a alugma destas propriedades.

    >>> obj2.is_dynamic() False >>> obj2.is_static() True

Outra alternativa é simplesmente criar o objeto com um valor infinito para a
massa

    >>> obj3 = Circle(10, pos=(300, 300), mass='inf') >>> world.add(obj3)

Lembramos que as colisões são calculadas apenas se um dos objetos envolvidos for
dinâmico. Deste modo, quando dois objetos cinemáticos ou um objeto estático e
um cinemático se encontram, nenhuma força é aplicada e eles simplemente
atravessam um pelo outro.


Aplicando forças
================

Forças externas
---------------

A FGAme se preocupa em calcular automaticamente as forças que surgem devido à
colisão, atrito, vínculos, etc. Em alguns casos, no entanto, o usuário pode
querer especificar uma força externa arbitrária que é aplicada a cada frame em
um determinado objeto.

Isto pode ser feito salvando qualquer função do tempo no atributo especial
:meth:`Body.force` dos objetos físicos. Esta força será recalculada a cada
frame em função do tempo (e implicitamente também pode depender de outras
variáveis como posição, velocidade, etc).

    >>> def gravity_force(t): ...     return Vec(0, -100) >>> obj3.force =
    gravity_force

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

Estas constantes podem ser definidas globalmente num objeto do tipo ``World`` ou
individualmente caso um objeto queira ter um comportamento diferente do global.

    >>> world.gravity = (0, -50) >>> world.adamping = 0.1 >>> obj2.gravity =
    (0, 50)  # objeto 2 cai para cima!

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

            # Definimos uma margem de 10px de espessura que os objetos não
            # conseguem atravessar
            self.add_bounds(width=10)

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
ocorre. Eventos podem ser disparados pelo usuário (ex.: apertar uma tecla), ou
pela simulação (ex.: ocorrência de uma colisão).

Digamos que a simulação deva pausar ou despausar sempre que a tecla de espaço
for apertada. Neste caso, devemos ligar o evento "apertou a tecla espaço" com a
função `.toggle_pause()` do mundo, que alterna o estado de pausa da simulação.

    >>> on_key_down('space', world.toggle_pause)               # doctest:
    +SKIP

A tabela abaixo mostra os eventos mais comuns e a assinatura das funções de
callback

.. |kd| replace:: ``key-down``
.. |ku| replace:: ``key-up``
.. |lp| replace:: ``long-press``
.. |mm| replace:: ``mouse-motion``
.. |md| replace:: ``mouse-button-down``
.. |mu| replace:: ``mouse-button-up``
.. |ml| replace:: ``mouse-long-press``

+--------+-----------+---------------------------------------------------+
| Evento | Argumento | Descrição                                         |
+========+===========+===================================================+
| |kd|   | tecla     | Chamado no frame que uma tecla é pressionada.     |
|        |           | O argumento pode ser um objeto 'tecla', que       |
|        |           | depende do back end utilizado ou uma string,      |
|        |           | que é portável para todos back ends.              |
|        |           |                                                   |
|        |           | A string corresponde à tecla escolhida. Teclas    |
|        |           | especiais podem ser acessadas pelos seus nomes    |
|        |           | como em 'space', 'up', 'down', etc.               |
|        |           |                                                   |
|        |           | Os callbacks do tipo 'key-down' são funções que   |
|        |           | não recebem nenhum argumento.                     |
+--------+-----------+---------------------------------------------------+
| |ku|   | tecla     | Como em 'key-down', mas é executado no frame em   |
|        |           | que a tecla é liberada pelo usuário.              |
+--------+-----------+---------------------------------------------------+
| |lp|   | tecla     | Semelhante aos anteriores, mas é executado em     |
|        |           | *todos* os frames em que a tecla se mantiver      |
|        |           | pressionada.                                      |
+--------+-----------+---------------------------------------------------+
| |mm|   | nenhum    | Executado sempre que o ponteiro do mouse estiver  |
|        |           | presente na tela.                                 |
|        |           |                                                   |
|        |           | O callback é uma função que recebe um vetor com a |
|        |           | posição do mouse como primeiro argumento.         |
+--------+-----------+---------------------------------------------------+
| |md|   | botão     | Semelhante aos eventos de 'key-down', 'key-up' e  |
| |mu|   |           | 'long-press'. Deve ser registrada com 'left',     |
| |ml|   |           | 'right', 'middle', 'wheel-up' ou 'wheel-down'.    |
|        |           |                                                   |
|        |           | A grande diferença está em que o callback recebe  |
|        |           | a posição do ponteiro do mouse como primeiro      |
|        |           | argumento.                                        |
|        |           |                                                   |
+--------+-----------+---------------------------------------------------+

Um método prático de definir associar um método de uma classe a um evento
especifico é utilizar o decorador ``@listen``. Funciona de maneira semelhante
às funções :func:`on_key_down`, :func:`on_key_up`, etc, mas exige um sinal como
primeiro argumento.

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


Pronto! Agora você já sabe o básico para criar um jogo ou simulação simples
utilizando a FGAme. Nas próximas seções vamos revisar com mais detalhes como a
FGAme funciona e os princípios gerais de implementação e organização de um
motor de jogos orientado à física.


Exemplo: interação com o mouse
------------------------------

Vamos modificar o exemplo anterior para que seja possível adicionar novos
círculos utilizando o mouse. Queremos definir a posição inicial no instante em
que o botão esquerdo do mouse é clicado e a velocidade seria dada pela posição
relativa quando o usuário soltar o botão. Podemos dividir este procedimento em
3 etapas:

Frame em que o botão é pressionado:
    Acrescenta o círculo e pausa a simulação
Enquanto o botão é pressionado:
    Desenha uma linha na tela ligando o centro do círculo ao ponto atual.
Após o usuário soltar o botão:
    Calcula a velocidade a partir da linha e remove-a do mundo. Restaura a
    simulação.

Podemos implementar cada uma destas etapas ouvindo os eventos
``mouse-button-down``, ``mouse-long-press`` e ``mouse-button-up``,
respectivamente. O primeiro evento, que consiste em pausar a simulação e
acrescentar o círculo pode ser implementado como::

    class GravityWorld(World):
        ...

        @listen('mouse-button-down', 'left')
        def add_circle(self, pos):
            self.pause()
            self.circle = Circle(20, pos=pos, color='random')
            self.line = draw.Segment(pos, pos)
            self.add([self.circle, self.line])

Observe que a função add_circle() possui um argumento adicional `pos` que
determina a posição do cursor do mouse na tela. Isto difere um pouco dos
eventos ``key-up`` e ``key-down`` que não pedem argumentos adicionais.

Pausamos a simulação com o método :meth:`FGAme.World.pause` e posteriormente
criamos os atributos ``circle`` e ``line`` para armazenar o círculo recém
criado e a linha que define o vetor de velocidade. Note que criamos o segmento
de reta a partir da classe :cls:`FGAme.draw.Segment`. Todos os objetos
definidos no módulo :mod:`FGAme.draw` definem uma interface de renderização mas
não participam da física. Isto é útil para desenhar elementos gráficos do jogo
sem se preocupar que eles possam sair por aí colidindo com os outros objetos na
tela. O módulo :mod:`FGAme.draw` possui classes correspondentes à todos os
objetos físicos definidos em :mod:`FGAme`, além de algumas outras classes
adicionais.

Note que é necessário adicionar a linha e o círculo ao mundo com o método
:meth:`FGAme.World.add` para que sejam mostrados na tela e possam interagir com
os outros objetos físicos.

Esta função implementa a lógica de pausar a simulação e acrescentar o círculo
quando o clique inicia. Note que após soltar o mouse, a simulação permanece
parada. Devemos ouvir o ``mouse-long-press`` para atualizar a linha e o
``mouse-button-up`` para continuar a simulação.

::

    class GravityWorld(World):
        ...
        @listen('mouse-long-press', 'left')
            def set_circle_velocity(self, pos):
                self.line.end = pos


        @listen('mouse-button-up', 'left')
            def launch_circle(self, pos):
                self.unpause()
                self.remove(self.line)
                self.circle.vel = 4 * self.line.direction


O handler de ``mouse-long-press`` simplesmente atualiza a posição do ponto final
da linha na tela. Quando o usuário larga o botão, executamos o evento
``mouse-button-up``, que despausa a simulação, remove a linha e define a
velocidade do círculo como sendo proporcional ao vetor de direção do segmento
de reta.
