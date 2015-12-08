=======
URITool
=======

This is a small utility to retrieve data from the URI online judge website. This
is aimed at teachers who want to use URI in the classroom but require more
flexibility than what is provided by the "URI Academic" tool. I created this
script mainly because "Academic" were not working properly with for Python 3
submissions.


Installation
============

It requires Python 3 and the lxml library. You may want to install both using your
distribution tools (e.g., ``apt-get install python3-lxml``) or rely on pip to
download all dependencies. The command bellow should download and install
URITool in your system::

    $ sudo python3 -m pip install uritool

Ubuntu/Debian follow the unhelpful policy of not packaging either pip or ensurepip
modules with the default installation. You may need to ``apt-get install python3-pip``
before installing URITool.

This package should work on Windows and MacOSX, but I never tested.


Usage
=====

This is a command line tool that have very few options for retrieving submissions
from your students. It follows standard POSIX arguments, including ``uritool -h``
or  ``uritool --help`` for displaying some helpful messages.

It's all for now folks ;-)