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
:::::::::::::::::::::::::::::::::::::::::::::::::

    $ cd ~ $ hg clone https://bitbucket.org/pygame/pygame

E instale...
::::::::::::

    $ cd pygame $ python3 setup.py build $ python3 setup.py install --user

(Note que a opção --user é facultativa e diz para realizar a instalação apenas
para o usuário atual. Caso deseje fazer a instalação para todo o sistema, omita
esta opção e re-execute o último comando incluindo ``sudo`` no ínicio.)

Agora que o Pygame foi instalado, executamos o pip para instalar as outras
dependências
::::::::::::

    $ pip3 install smallvectors smallshapes pygeneric FGAme --user --pre -U

Para verificar que o FGAme foi instalado corretamente, execute os demos usando o
comando::

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

Os usuários de Windows devem baixar a versão de Python desejada (recomendamos a
versão 3.4) junto com as dependências compiladas para esta versão. Baixe e
instale os arquivos na ordem mesma ordem da lista indicada abaixo:

    * Python 3.4: `[download]`__
    * Python game para Python 3.4: `[download]`__
    * Cython: `[download]`__

.. __: https://www.python.org/downloads/
.. __: http://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame
.. __: http://www.lfd.uci.edu/~gohlke/pythonlibs/#cython

Lembre-se sempre de escolher a versão do Pygame e do Cython correspondente à
versão de Python que você utiliza e a arquitetura (x86 ou 64 bits, lembre-se
que processadores Intel de 64 bits pertencem à arquitetura amd64).

Durante a instalação do Python é conveniente acionar a opção
*"Add python.exe to PATH"*. Isto deixará o Python mais facilmente disponivel
para o terminal de comando. Caso você esqueceu desta opção ou está em uma
versão nova do Windows, é necessário executar os comandos a partir da pasta do
Python.

Primeiramente abra o terminal do Windows apertando ``Win+R`` e digitando
``cmd``. Dentro do comando, vá para a pasta onde o Python foi instalado
(normalmente C:\Python34\)::

    $ cd c:\python34
    $ python -m pip install six pygeneric smallvectors smallshapes FGAme

Para abrir o terminal, pressione ``Win+R`` para abrir a caixa de executar
programas e digite ``cmd``.


Desenvolvedores
===============

Caso você queira participar do desenvolvimento da FGAme, ou está matriculado na
disciplina de Física para jogos na faculdade UnB/Gama ;), é necessário utilizar
a versão de desenvolvimento do FGAme e das bibliotecas auxiliares
**smallvectors** e **smallshapes**. Todas estas bibliotecas estão presentes no
GitHub no endereços abaixo

    * `FGAme`__
    * `smallvectors`__
    * `smallshapes`__

Caso você não esteja familiarizado com o GIT e o github, este é um bom começo:
`GIT - Guia Prático`__.

.. __: https://github.com/fabiommendes/FGAme/
.. __: https://github.com/fabiommendes/smallvectors/
.. __: https://github.com/fabiommendes/smallshapes/ 
.. __: http://rogerdudler.github.io/git-guide/index.pt_BR.html/
