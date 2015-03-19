import os

if __name__ == '__main__':
    for dir in ['drawing', 'simulations', 'games']:
        os.chdir(dir)
        code = os.system('python _runall_.py')
        print(code)
        if code != 0:
            raise SystemExit(code)
        os.chdir('..')