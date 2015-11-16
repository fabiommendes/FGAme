from pytest import main
from FGAme import conf


conf.set_backend('empty')
main('-q --doctest-modules')
