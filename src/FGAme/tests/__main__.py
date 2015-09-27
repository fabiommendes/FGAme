'''
Loads all tests in module and run
'''

from smallvectors.tests import *
from FGAme.tests import *
import FGAme as mod_current

from unittest2 import main
import doctest
import sys
from FGAme import conf
conf.set_backend()
print('Starting tests using backend: %s' % conf.get_backend())


def load_tests(loader, tests, ignore):
    prefix = mod_current.__name__

    # Find doctests
    for modname, mod in sys.modules.items():
        if modname.startswith(prefix + '.') or modname == prefix:
            try:
                tests.addTests(doctest.DocTestSuite(mod))
            except ValueError:  # no docstring
                pass

    return tests

main()
