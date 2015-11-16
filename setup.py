#-*- coding: utf8 -*-
import os
import sys
import setuptools
import warnings
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

#
# Choose the default Python3 branch or the code converted by 3to2
#
PYSRC = 'src' if sys.version.startswith('3') else 'py2src'

#
# Cython stuff (for the future)
#
if 'PyPy' not in sys.version:
    try:
        from Cython.Build import cythonize
        from Cython.Distutils import build_ext
    except ImportError:
        warnings.warn('Please install Cython to compile faster versions of FGAme modules')
    else:
        try:
            setup_kwds.update(
                ext_modules=cythonize('src/generic/*.pyx'),
                cmdclass={'build_ext': build_ext})
        except ValueError:
            pass

#
# Configure backend
#
try:
    import pygame
    BACKEND = ''
except ImportError:
    BACKEND = 'pysdl2>=0.5'


#
# Main configuration script
#
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

    package_dir={'': PYSRC},
    packages=setuptools.find_packages(PYSRC),
    license='GPL',

    install_requires='''
        # cython>=0.21
        %s
        pillow
        six
        smallshapes>=%s
        smallvectors>=%s
        pygeneric>=0.1.1
    ''' % (BACKEND, VERSION_BIG, VERSION_BIG),
    zip_safe=False,
    **setup_kwds
)
