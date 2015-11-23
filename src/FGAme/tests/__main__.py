from pytest import main
from FGAme import conf

if __name__ == '__main__':
    conf.set_backend('empty')
    main('-q')
