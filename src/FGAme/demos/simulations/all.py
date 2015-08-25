import os

if __name__ == '__main__':
    for file in ['aabb_friction', 'adamp', 'gas_aabbs', 'embolo',
                 'poly_simple', 'poly_simple2', 'gas_polys']:

        code = os.system('python %s.py' % file)
        if code != 0:
            raise SystemExit(code)
