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

        # Atualiza estado de jogo (ex: imove personagens, calcula pontos, danos,
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