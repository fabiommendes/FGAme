import os

if __name__ == '__main__':
    for file in ['pong']:
        
        code = os.system('python %s.py' % file)
        if code != 0:
            raise SystemExit(code)