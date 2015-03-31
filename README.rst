=====
FGAme
=====

FGAme é um motor de jogos 2D para Python utilizado na aula de Introdução à 
Física de Jogos na Faculdade UnB Gama. A FGAme tem como objetivos principais a simplicidade e 
modularidade: queremos desenvolver jogos rapidamente e conseguir trocar qualquer 
aspecto da simulação de física de maneira simples. Trata-se de
um motor de jogos didático cujo maior objetivo é o uso em sala de aula. 

Este não é (e provavelmente nunca será) um motor de alto desempenho. Ainda que
se tenha dado alguma atenção à otimização, esta não é uma prioridade do projeto.
Dito isto, computadores modernos são poderosos o suficiente para que, apesar das 
limitações do Python e desta biblioteca, serem capazes de simular muitas 
dezenas de polígonos e criar jogos interessantes baseados em física.

O foco da FGAme está na física e não na apresentação gráfica. Espere um motor 
de jogos bastante limitado no segundo quesito, mas relativamente versátil e 
muito simples de utilizar no primeiro.

Máquina virtual
===============

Caso você queira testar a FGAme mas não tem muita experiência em 
desenvolvimento de Python no Linux

Instalação
==========

FGAme é capaz de rodar em diversas plataformas. Ela funciona tanto em 
Python2 quanto em Python3 e utiliza algumas extensões escritas em Cython (que 
são traduzidas para C e posteriormente compiladas). Além disto, é necessário
instalar pelo menos um backend entre os suportados: pygame ou sdl2 (e 
futuramente kivy e possivelmente PyQT5 e pyglet). Recomendamos utilizar Python3
e pygame como uma opção inicial e os guias abaixo discutem como realizar este
tipo de instalação.

Linux
-----

Ubuntu
......

(Alguém confirme pois não utilizo o Ubuntu, e sim o Archlinux. Provavelmente
o nome dos pacotes está errado.)
No Ubuntu e similares, basta utilizar o comando apt-get para instalar as 
dependências necessárias. Depois instale a biblioteca utilizando o PIP. Comece 
executando o comando abaixo no terminal::

  $ sudo apt-get install python3-pygame python3-pip cython

Se quiser instalar algum dos outros backends, instale os pacotes apropriados::

  $ sudo apt-get install python3-kivy
  $ sudo apt-get install python3-sdl2

O FGAme está presente no PIP e pode ser instalado executando::

  $ sudo pip3 install FGAme

O PIP se encarrega de baixar, compilar e instalar a última versão disponível.

Archlinux
.........

Alguns dos pacotes necessários estão nos repositórios principais e alguns estão
disponíveis apenas no AUR. Certifique-se que a versão desejada do PIP e do 
Cython estão instaladas:: 

  # pacman -S python-pip cython
  
para Python 3 ou::

  # pacman -S python2-pip cython python2-pygame
  
para Python 2.

Apenas a versão compilada para Python 2 do Pygame está disponível nos 
repositórios principais. A versão de desenvolvimento do Pygame possui suporte 
para Python3 e pode ser instalada a partir do pacote ``python-pygame-hg`` no 
AUR. Ela deve ser instalada antes de proceder com a instalação da FGAme.

Finalmente, execute o PIP para compilar e instalar a FGAme::

   # pip install FGAme

(ou utilize o pip2, para Python2).

Instalando a partir do código fonte
...................................

É possível que um ou mais pacotes necessários para executar a FGAme não estejam 
disponíveis na sua distribuição. (Por exemplo, as versões mais antigas do Ubuntu
podem não possuir os pacotes necessários). Neste caso, é necessário instalar um 
ou mais pacotes a partir do código fonte. 

Fornecemos o caminho para as páginas de download de cada um dos pacotes 
necessários para executar a FGAme. Você deve possuir os pacotes de 
desenvolvimento instalados na sua máquina antes de continuar. Lembre-se de 
sempre priorizar os pacotes já disponíveis no gerenciador de pacotes da sua
distribuição e instale apenas aqueles que estão faltando.

  * Python3: https://www.python.org/downloads/
  * Cython: http://cython.org/release/Cython-0.22.tar.gz
  * Pygame: http://pygame.org/download.shtml
  * Kivy (opcional): http://kivy.org/#download
  * Sdl2 (opcional): https://bitbucket.org/marcusva/py-sdl2/downloads
  * FGAme: https://github.com/fabiommendes/FGAme
  
Em cada caso, consulte o arquivo README ou INSTALL para instruções de 
instalação. Na maior parte dos casos, basta descompactar o arquivo de código
fonte, entrar na pasta descomprimida e executar::
 
	# python setup.py build
	# sudo python setup.py install 

Windows
-------

Os usuários de Windows devem baixar a versão de Python desejada junto com os 
pacotes compilados para esta versão. Este guia fornece os endereços para o 
Python 3.4, mas o usuário pode instalar outra versão com mínimas modificações.
Baixe e instale os arquivos na ordem mesma ordem da lista indicada abaixo::

	* Python 3.4: https://www.python.org/ftp/python/3.4.3/python-3.4.3.msi
	* Pygame para Python3: http://www.lfd.uci.edu/~gohlke/pythonlibs/z94jfosk/pygame-1.9.2a0-cp34-none-win32.whl
	* GCC: 
	* Cython: http://www.lfd.uci.edu/~gohlke/pythonlibs/z94jfosk/Cython-0.22-cp34-none-win32.whl
	
As versões 64 bits estão disponíveis aqui::
	
	* `Link Python 3.4 <https://www.python.org/ftp/python/3.4.3/python-3.4.3.amd64.msi/>`
	* `Link Pygame para Python3 <http://www.lfd.uci.edu/~gohlke/pythonlibs/z94jfosk/pygame-1.9.2a0-cp34-none-win_amd64.whl/>`  
	* `Link Cython: <http://www.lfd.uci.edu/~gohlke/pythonlibs/z94jfosk/Cython-0.22-cp34-none-win_amd64.whl/>`


Agora execute o PIP no terminal do Windows::

	# pip install FGAme 

Para abrir o terminal, pressione ``Win+R`` para abrir a caixa de executar 
programas e digite ``cmd``.

Mac OS
------

Alguém com Mac pode ajudar aqui!

Android
-------

Provavelmente roda o usando o Pygame subset for android. Talvez precisamos de 
um guia mais detalhado que possa ser colocado aqui.

iOS
---

Ni puta idea! Supostamente pode ser instalado com o Kivy. É preciso terminar o
port e verificar como fazer o deploy para iOS. Alguém com experiência pode ajudar.


Orientação para estudantes
==========================

Qual plataforma escolher?
-------------------------






