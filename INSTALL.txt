Dependências
============

O FGAme depende do Cython para instalar as extensões compiladas e de algum
backend que pode ser o SDL2 (padrão) ou Pygame. Abaixo segue o link para a
página de cada um dos respectivos projetos.


*  Cython: http://cython.org (necessário para compilar as extensões)
*  SDL2: http://pysdl2.readthedocs.org/en/latest/
*  Pygame: http://pygame.org

Instalação
==========

A FGAme pode ser instalada utilizando a rotina padrão do Python. Descompacte o
pacote `.zip` e execute o comando abaixo a partir da pasta resultante::

    $ python setup.py build
    $ sudo python setup.py install

Se você quiser desenvolver em cima da árvore de código fonte aqui disponível, é
necessário compilar as extensões em Cython. Neste caso, execute::

    $ python setup.py build_ext --inplace

