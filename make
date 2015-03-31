#!/bin/sh

python2 setup.py build_ext --inplace;
python3 setup.py build_ext --inplace;
python2 setup.py build;
python3 setup.py build;

sudo rm /usr/lib/python2.7/site-packages/FGAme/ -Rfv
sudo rm /usr/lib/python3.4/site-packages/FGAme/ -Rfv

sudo python2 setup.py install;
sudo python3 setup.py install;

python2 -c "import FGAme.demos.simulations.embolo as game; game.Gas().run()";
python3 -c "import FGAme.demos.simulations.embolo as game; game.Gas().run()";

