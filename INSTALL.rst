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


Troubleshoot
------------

Windows users may find that these command will only works if typed from Python's
installation directory.

Some Linux distributions (e.g. Ubuntu) install Python without installing pip.
Please install it before. If you don't have root privileges, download the
get-pip.py script at https://bootstrap.pypa.io/get-pip.py and execute it as
``python get-pip.py --user``.