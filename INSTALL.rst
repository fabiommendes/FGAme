=========================
Installation instructions
=========================

FGAme can be installed using pip::

    $ python3 -m pip install FGAme

This command will fetch the archive and its dependencies from the internet and
install them.

If you've downloaded the tarball, unpack it, and execute::

    $ python3 setup.py install

In either case, it is possible to perform local user installs by appending the
``--user`` option.

Docker
------

If you don't know what Docker_ is, you should check it out, it's great! If you're acquainted with it, just pull our image::

	$ docker pull gutioliveira/fgame

.. _Docker: https://www.docker.com/

Sometimes is necessary to disable access control to your xhost by using::

	$ xhost +

To run a container with our Docker image, use::

	$ docker run -ti -e DISPLAY=$DISPLAY -v /run/user/$UID/pulse/native:/home/developer/socket --name FGAme -v /tmp/.X11-unix:/tmp/.X11-unix gutioliveira/fgame /bin/bash

It's possible to map a folder from your environment to the container that will run FGAme, just add the flag below to the command above replacing the targetdirectory to a folder that you want to work in::

	$ -v targetdirectory:/code/yourproject

To start using FGAme, just type::

	$ python3 test.py

Debian
------

If you use Debian or Debian-based distributions like Ubuntu or Linux Mint, we show you how to install all the prerequisites to start using FGAme.

First, download and install all libraries needed by Pygame::

	$ sudo apt-get update
	$ sudo apt-get install -y python3-dev python3-numpy \ 
	libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev \
	libsmpeg-dev libsdl1.2-dev libportmidi-dev libswscale-dev \
	libavformat-dev libavcodec-dev libfreetype6-dev

Then install Mercurial, and clone Pygame repository::

	$ sudo apt-get -y install mercurial
	$ hg clone https://bitbucket.org/pygame/pygame

Build and Install Pygame::
	
	$ python3 pygame/setup.py build
	$ sudo python3 pygame/setup.py install

If you don't have pip3 or pil, install them::

	$ sudo apt-get -y install python3-pip
	$ sudo apt-get -y install python3-pil

Finally, install pgzero and FGAme::

	$ sudo pip3 install pgzero
	$ sudo python3 -m pip install FGAme


Troubleshoot
------------

Windows users may find that these command will only works if typed from Python's
installation directory.

Some Linux distributions (e.g. Ubuntu) install Python without installing pip.
Please install it before. If you don't have root privileges, download the
get-pip.py script at https://bootstrap.pypa.io/get-pip.py and execute it as
``python get-pip.py --user``.