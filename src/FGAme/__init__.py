#-*- coding: utf8 -*-
'''
========
Tutorial
========

Exemplo básico
==============

Este tutorial explica como utilizar a FGAme para a criação de jogos ou
simulações de física simples. A FGAme é um motor de jogos com ênfase na
simulação de física. Todos os objetos, portanto, possuem propriedades físicas
bem definidas como massa, momento de inércia, velocidade, etc. A simulação da
física é feita, em grande parte, de modo automático. Você verá o quanto é
simples!

O primeiro passo é definir o palco que os objetos habitarão. Isto pode ser feito
criando um objeto da classe World().

>>> world = World()

A partir daí, podemos criar objetos e inserí-los na simulação

>>> obj1 = Circle(50)
>>> obj2 = Circle(50, color='red')
>>> world.add([obj1, obj2])

Para modificar as propriedades físicas dos objetos basta modificar diretamente
os atributos correspondentes. Para uma lista completa de atributos, consulte
o módulo ?Objects.

>>> obj1.mass = 10
>>> obj2.mass = 20
>>> obj1.pos = (150, 50)
>>> obj1.vel = (-100, 0)

As variáveis dinâmicas podem ser modificadas diretamente, mas sempre que
possível, devemos utilizar os  métodos que realizam os deslocamentos relativos
(ex.: .move(), .boost(), etc). Estes métodos são mais eficientes.

+----------+---------------+-------------------------------+---------+
| Variável | Deslocamentos | Descrição                     | Unidade |
+==========+===============+===============================+=========+
| pos      | move          | Posição do centro de massa    | px      |
+----------+---------------+-------------------------------+---------+
| vel      | boost         | Velocidade do centro de massa | px/s    |
+----------+---------------+-------------------------------+---------+
| theta    | rotate        | Ângulo de rotação             | rad     |
+----------+---------------+-------------------------------+---------+
| omega    | aboost        | Velocidade angular            | rad/s   |
+----------+---------------+-------------------------------+---------+

Aplicamos uma operação de `.move()` e movê-lo com relação à posição anterior.
Veja como fica a posiição final do objeto.

>>> obj1.move((150, 0)) # deslocamento com relação à posição inicial
>>> obj1.pos
Vector(300, 50)

Para iniciar a simulação, basta chamar o comando

>>> world.run() # doctest: +SKIP


Objetos dinâmicos
=================

Apesar do FGAme não fazer uma distinção explícita durante a criação, os objetos
no mundo podem ser do tipo dinâmicos, cinemáticos ou estáticos. Todos eles
participam das colisões normalmente, mas a resposta física pode ser diferente em
cada caso. Os objetos dinâmicos se movimentam na tela e respondem às forças
externas e de colisão. Os objetos cinemáticos se movimentam (usualmente em
movimento retilíneo uniforme), mas não sofrem a ação de nenhuma força. Já os
objetos estáticos permanecem parados e não respondem a forças.

A diferenciação é feita apenas pelo valor das massas e das velocidades.
Convertemos um objeto em cinemático atribuindo um valor infinito para a massa.
Um objeto será estático se tanto a massa quanto a velocidade forem nulas.

>>> obj2.mass = 'inf' # automaticamente se torna estático pois a velocidade é nula

O FGAme utiliza esta informação para acelerar os cálculos de detecção de colisão
e resolução de forças. As propriedades dinâmicas/estáticas dos objetos, no
entanto são inteiramente transparentes ao usuário.

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
métodos `.make_static()` (ou kinematic/dynamic) para controlar as propriedades
dinâmicas do objeto.

>>> obj2.make_static()

Já os métodos `.is_static()` (ou kinematic/dynamic) permitem investigar se um
determinado objeto satisfaz a alugma destas propriedades.

>>> obj2.is_dynamic()
False
>>> obj2.is_static()
True

Lembramos que as colisões são calculadas apenas se um dos objetos envolvidos for
dinâmico. Deste modo, quando dois objetos cinemáticos ou um objeto estático
e um cinemático se encontram, nenhuma força é aplicada e eles simplemente
atravessam um pelo outro.

Forças básicas
==============

Além das forças arbitrárias que podem atuar em qualquer objeto e dos impulsos
associados às colisões, existem algumas forças que podem ser definidas
globalmente no objeto World(). Trata-se da força da gravidade e das forças
viscosas para as velocidades lineares e angulares.

Na realidade, não definimos as forças diretamente, mas sim as acelerações que
elas provocam em cada objeto. São as constantes `gravity`, `damping` e
`adamping`. As forças são criadas a partir da fórmula

    F = obj.mass * (gravity - obj.vel * damping)

E o torque é gerado por

    tau = -obj.inertia * adamping *  obj.omega

Estas constantes podem ser definidas globalmente no objeto mundo ou
individualmente. Deste modo, é possível que algum objeto possua uma gravidade
diferente do resto do mundo. O mesmo se aplica às forças de amortecimento.

>>> world.gravity = (0, -50)
>>> world.adamping = 0.1

Todos objetos que não definirem explicitamente o valor destas constantes
assumirão os valores definidos no mundo no qual estão inseridos. Acrescentamos
um terceiro objeto com um valor de gravidade diferente do resto do mundo, para
demonstrar este conceito.

>>> obj3 = Circle(20, (0, -100), gravity=(20, 50), world=world, color='blue')

(Obs.: se o parâmetro world for fornecido, o objeto é adicionado
automaticamente durante a criação)

Interação com o usuário
=======================

Até agora vimos apenas como controlar os parâmetros de simulação física. É
lógico que em um jogo deve ser existir alguma forma de interação com o usuário.
Na FGAme, esta interação é controlada a partir da noção de eventos e callbacks.
É possível registrar funções que são acionadas sempre que um determinado evento
acontece. Eventos podem ser disparados pelo usuário (ex.: apertar uma tecla),
ou pela simulação (ex.: ocorrência de uma colisão).

Digamos que a simulação deva pausar ou despausar sempre que a tecla de espaço
for apertada. Neste caso, devemos ligar o evento "apertou a tecla espaço"
com a função `.toggle_pause()` do mundo, que alterna o estado de pausa da
simulação.

>>> world.listen('key-down', 'space', world.toggle_pause) # doctest: +SKIP

A tabela abaixo mostra os eventos mais comuns e a assinatura das funções de
callback

+----------------+-------------+---------------------------------------------------+
| Evento         | Argumento   | Descrição                                         |
+================+=============+===================================================+
| key-down       | tecla       | Chamado no frame que uma tecla é pressionada.     |
|                |             | O argumento pode ser um objeto 'tecla', que       |
|                |             | depende do back end utilizado ou uma string,      |
|                |             | que é portável para todos back ends.              |
|                |             |                                                   |
|                |             | A string corresponde à tecla escolhida. Teclas    |
|                |             | especiais podem ser acessadas pelos seus nomes    |
|                |             | como em 'space', 'up', 'down', etc.               |
|                |             |                                                   |
|                |             | Os callbacks do tipo 'key-down' são funções que   |
|                |             | não recebem nenhum argumento.                     |
+----------------+-------------+---------------------------------------------------+
| key-up         | tecla       | Como em 'key-down', mas é executado no frame em   |
|                |             | que a tecla é liberada pelo usuário.              |
+----------------+-------------+---------------------------------------------------+
| long-press     | tecla       | Semelhante aos anteriores, mas é executado em     |
|                |             | *todos* os frames em que a tecla se mantiver      |
|                |             | pressionada.                                      |
+----------------+-------------+---------------------------------------------------+
| mouse-motion   | nenhum      | Executado sempre que o ponteiro do mouse estiver  |
|                |             | presente na tela.                                 |
|                |             |                                                   |
|                |             | O callback é uma função que recebe um vetor com a |
|                |             | posição do mouse como primeiro argumento.         |
+----------------+-------------+---------------------------------------------------+
| mouse-click    | botão       | Como 'mouse-motion', mas só é executada após o    |
|                |             | clique. Deve ser registrada com 'left', 'right'   |
|                |             | 'middle' correspondendo a um dos 3 tipos de botão |
|                |             | do mouse.                                         |
|                |             |                                                   |
|                |             | O callback recebe apeans a posição do ponteiro    |
|                |             | como primeiro argumento.                          |
+----------------+-------------+---------------------------------------------------+

Simulação simples
=================

Uma simulação de física pode ser criada facilmente adicionando objetos à uma
instância da classe World(). O jeito mais recomendado, no entanto, é criar uma
subclasse pois isto incentiva o código a ficar mais organizado. No exemplo
abaixo, montamos um sistema "auto-gravitante" onde as duas massas estão presas
entre si por molas.


>>> class Gravity(World):
...     def __init__(self):
...         # Chamamos o __init__ da classe pai
...         super(Gravity, self).__init__()
...
...         # Criamos dois objetos
...         A = Circle(20, pos=pos.from_middle(100, 0), vel=(100, 300), color='red')
...         B = Circle(20, pos=pos.from_middle(-100, 0), vel=(-100, -300))
...         self.A, self.B = A, B
...         self.add([A, B])
...
...         # Definimos a força de interação entre ambos
...         K = self.K = A.mass
...         self.A.external_force = lambda t: -K * (A.pos - B.pos)
...         self.B.external_force = lambda t: -K * (B.pos - A.pos)


Agora que temos uma classe mundo definida, basta iniciá-la com o comando

>>> if __name__ == '__main__':
...     world = Gravity()
...     world.run() # doctest: +SKIP

Pronto! Agora você já sabe o básico para criar um jogo ou simulação
simples utilizando a FGAme. Nas próximas seções vamos revisar com mais
detalhes como a FGAme funciona e os princípios gerais de implementação e
organização de um motor de jogos orientado à física.

================================
Motores de jogos: uma introdução
================================

Os pioneiros não tinham esse luxo: cada novo jogo implementado envolvia 
programar como escrever os pixels na tela, como interagir com os dispositivos de
entrada do usuário, e todas estas operações básicas. Na medida que os 
computadores evoluíram, cada vez mais as tarefas comuns na implementação de 
jogos foram movidas para bibliotecas/frameworks especializados deixando os 
desenvolvedores muito mais focados nos aspectos criativos da construção do jogo. 
 
Um motor de jogo idealmente deve chegar neste ponto: o desenvolvedor só liga as
peças e define a lógica do jogo, mas sem se preocupar com os detalhes mais 
baixos da programação. Por isto, motores de jogos modernos podem se tornar 
componentes extremamente sofisticados que chegam literalmente a possuir milhões
de linhas de código.

A FGAme, obviamente, é um projeto muito simples nesta escala e foi desenvolvido
com o intuito muito mais pedagógico que comercial: os objetivos são ensinar 
conceitos de física para programadores e mostrar alguns princípios práticos de
desenvolvimento de motores para jogos (especialmente jogos voltados para física).

Começamos pincelando de forma geral o que um motor de jogos deve ser capaz de
fazer e como isso normalmente se configura em termos de arquitetura de software.

Desenhando na tela
==================

Um motor de jogos que se preze deve ser capaz de, no mínimo, capturar as 
entradas do usuário e desenhar os elementos de jogo na tela (e talvez coordenar
outras formas de saída tais como audio, respostas por vibração, etc).

De forma bem genérica, podemos pensar que a maioria dos jogos é implementada
da seguinte maneira::

    # Inicializa o estado do motor de jogos (configura hardware, lê arquivos
    # de configuração, savegames, etc)
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
auxílio da biblioteca SDL. Entender o funcionamento da SDL é interessante pois
vários jogos e motores de jogos são baseados nesta tecnologia e sua arquitetura
é bastante convencional.

#TODO: SDL

Veja como funciona na FGAme:

>>> from FGAme import init_canvas
>>> canvas = init_canvas(800, 600)   # doctest: +SKIP

Observe que a mesma variável canvas pode ser recuperada posteriormente 
utilizando a função .get_canvas() do objeto de configuração global

>>> canvas = conf.get_canvas()   # ==> objeto canvas defindo anteriormente

Este código criará uma janela de 800 x 600 pixels e retorna o objeto "canvas" 
que é utilizado para manipular e desenhar a tela.

O objeto canvas é implementado em analogia a uma tela de pintura: mas no caso
trata-se de uma tela de pixels. Ele possui vários métodos do tipo paint_* que
permitem pintar figuras geométricas específicas. Por exemplo, podemos desenhar
um círculo no meio da tela utilizando

>>> canvas.paint_circle(pos=(400, 300), radius=50, color='black')

Observe que as imagens não são atualizadas imediatamente. Isto ocorre porque a
imagem é armazenada temporariamente na memória RAM e só é enviada para a tela
quando exigimos esta operação explicitamente. Para isto, basta chamar o método 
flip() no fim da seção de desenho.

>>> canvas.flip()

Uma maneira conveniente de fazer isto, é utilizar o objeto canvas dentro de
um bloco with(). Ao final do bloco, a função flip() será chamada 
automaticamente.

>>> with canvas:
...     canvas.paint_circle(pos=(400, 300), radius=50, color='black')
...     canvas.paint_circle(pos=(400, 300), radius=30, color='white')
  
Agora vemos os dois círculos pintados na tela.

==========
Referência
==========

Objetos
=======

.. automodule:: FGAme.objects


Classe mundo e aplicações
=========================

.. automodule:: FGAme.world


Colisões
========

.. automodule:: FGAme.collision


Funções matemáticas
===================

.. automodule:: FGAme.mathutils


Tópicos avançados
=================

Anatomia de uma colisão
=======================



Loop principal
==============

'''
#===============================================================================
# Importa pacotes
#===============================================================================
from FGAme import mathutils as math
from FGAme.mathutils import Vector, Matrix
from FGAme import draw
from FGAme import bench
from FGAme.core import *
from FGAme.physics import *
from FGAme.app import *
from FGAme.orientation_objects import *

if __name__ == '__main__':
    import doctest
    doctest.testmod()