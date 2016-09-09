#!/bin/sh
python2 setup.py clean &&
     rm py2src -rf &&
     cp src py2src -r &&
     sh 3to2.sh &&
     echo "\n\nend 3to2\n\n" &&
     python2 setup.py install --user &&
     FGAME_BACKEND=empty py.test-2.7 py2src/FGAme/tests/ &&
     python2 -m FGAme.demos &&
     python2 py2src/FGAme/demos/test_demos.py
