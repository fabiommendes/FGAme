Dependências
============

O FGAme depende do Cython para instalar as extensões compiladas e de algum 
backend que pode ser o Pygame (padrão), Sdl2 ou Kivy. Abaixo segue o link
para a página de cada um dos respectivos projetos.

	* Pygame: http://pygame.org 
	* Sdl2: http://pysdl2.readthedocs.org/en/latest/
	* Kivy: http://kivy.org
	* Cython: http://cython.org (somente para compilar as extensões)

Instalação
==========

A FGAme pode ser instalada utilizando a rotina padrão do Python. Descompacte
o pacote `.zip` e execute o comando abaixo a partir da pasta resultante:

	$ python setup.py build
	$ sudo python setup.py install
	
Se você quiser desenvolver em cima da árvore de código fonte aqui disponível,
é necessário compilar as extensões em Cython. Neste caso, execute

	$ python setup.py build_ext --inplace

