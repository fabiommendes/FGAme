import os

if __name__ == '__main__':
    for file in ['raw_circles', 'raw_shapes']:
        
        code = os.system('python %s.py' % file)
        if code != 0:
            raise SystemExit(code)