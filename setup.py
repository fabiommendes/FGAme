#-*- coding: utf8 -*-
import os
import sys
import setuptools
from setuptools import setup

#
# Read VERSION from file and write it in the appropriate places
#
AUTHOR = 'Fábio Macêdo Mendes'
BASE, _ = os.path.split(__file__)
with open(os.path.join(BASE, 'VERSION')) as F:
    VERSION = F.read().strip()
with open(os.path.join(BASE, 'src', 'FGAme', 'meta.py'), 'w') as F:
    F.write(
        '# Auto-generated file. Please do not edit\n'
        '__version__ = %r\n' % VERSION +
        '__author__ = %r\n' % AUTHOR)

VERSION_BIG = VERSION.rpartition('.')[0]
IS_PYPY = 'PyPy' in sys.version
setup_kwds = {}


###############################################################################
#                       Find and configure extensions
###############################################################################
def find_pyx():
    '''Return a list of all Cython scripts'''

    # Find files
    out = []
    for base, dirs, files in os.walk(os.path.join(os.getcwd(), 'src')):
        out.extend([os.path.join(base, f)
                    for f in files if f.endswith('.pyx')])

    # Remove cwd from path
    N = len(os.getcwd()) + 5
    out = [f[N:] for f in out]

    return out


def find_pure():
    '''Return a list of all .pxd files related to pure-python scripts'''

    # Find files
    out = []
    for base, dirs, files in os.walk(os.path.join(os.getcwd(), 'src')):
        out.extend([os.path.join(base, f)
                    for f in files if f.endswith('.pxd')])

    # Remove non-compilable files
    aux = []
    for f in out:
        with open(f) as F:
            line = F.readline()
        if line.startswith('#:'):
            if 'no-compile' in line:
                continue
        if os.path.exists(f[:-4] + '.py'):
            aux.append(f)
    out = aux

    # Remove cwd from path
    N = len(os.getcwd()) + 5
    out = [f[N:-4] + '.py' for f in out]

    return out


def get_extensions():
    '''Uses information on all pure-python scripts and all Cython scripts
    to create the extension objects'''

    from distutils.extension import Extension
    win_platforms = ['win32', 'cygwin']

    if IS_PYPY:
        return []

    exts = []
    for path in find_pyx() + find_pure():
        base, fname = os.path.split(path)
        ext_name = os.path.splitext(path)[0].replace(os.path.sep, '.')
        includes = ['src/%s' % base]
        if base != 'mathtools':
            includes.append('src/mathtools')

        ext = Extension(
            ext_name,
            ["src/%s" % path],
            libraries=(
                [] if sys.platform in win_platforms else ['m']),
            include_dirs=includes)

        exts.append(ext)

    return exts

###############################################################################
#                          Configure environment
###############################################################################

# Test if installation can compile extensions and configure them
# Currently only cpython accepts extensions
try:
    from Cython.Distutils import build_ext
except ImportError:
    # Ignore missing cython in alternative implementation
    if not (sys.platform.startswith('java') or sys.platform.startswith(
            'cli') or 'PyPy' in sys.version):
        raise
else:
    extensions = get_extensions()
    setup_kwds.update(
        cmdclass={
            "build_ext": build_ext},
        ext_modules=get_extensions())

##########################################################################
# Main configuration script
##########################################################################
setup(
    name='FGAme',
    version=VERSION,
    description='A game engine for 2D physics',
    author='Fábio Macêdo Mendes',
    author_email='fabiomacedomendes@gmail.com',
    url='https://github.com/fabiommendes/FGAme',
    long_description=open(os.path.join(BASE, 'README.txt')).read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],

    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    license='GPL',

    install_requires=[
        'pysdl2>=0.5', # or 'pygame>=1.9.*'
        'pillow',
        'six',
        'smallshapes>=%s' % VERSION_BIG,
        'smallvectors>=%s' % VERSION_BIG,
        'pygeneric>=0.1.1',
    ],
    # dependency_links=[
    #    'http://pygame.org/ftp/',
    #    'http://www.lfd.uci.edu/~gohlke/pythonlibs/',
    #],
    **setup_kwds
)
