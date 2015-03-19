import os
import importlib

def get_info():
    out = {}
    path, _ = os.path.split(__file__)
    for path in os.listdir(path):
        if path.endswith('_conf.py'):
            name, _, _ = path.rpartition('_')
            conf = importlib.import_module('FGAme.backends.%s_conf' % name)
            out[name] = dict(
                input=conf.input,
                screen=conf.screen,
                mainloop=conf.mainloop,
            )
    return out 

def get_screen(backend):
    pass

def get_input(backend):
    pass

def get_mainloop(backend):
    pass 

if __name__ == '__main__':
    print(get_info())