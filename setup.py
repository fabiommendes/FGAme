# -*- coding: utf8 -*-
#
# This file were created by Python Boilerplate. Use boilerplate to start simple
# usable and best-practices compliant Python projects.
#
# Learn more about it at: http://github.com/fabiommendes/boilerplate/
#

import os
from setuptools import setup, find_packages


# Meta information
name = 'FGAme'
project = 'FGAme'
author = 'Fábio Macêdo Mendes'
version = open('VERSION').read().strip()
dirname = os.path.dirname(__file__)

# Save version and author to __meta__.py
file_name = os.path.join(dirname, 'src', project, '__meta__.py')
with open(file_name, 'w', encoding='utf-8') as F:
    F.write('__version__ = %r\n'
            '__author__ = %r\n' % (version, author))

setup(
    # Basic info
    name=name,
    version=version,
    author=author,
    author_email='fabiomacedomendes@gmail.com',
    url='',
    description='A short description for your project.',
    long_description=open('README.rst').read(),

    # Classifiers (see https://pypi.python.org/pypi?%3Aaction=list_classifiers)
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],

    # Packages and dependencies
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'smallshapes>=0.6',
        'smallvectors>=0.6',
        'colortools>=0.1.1',
        'pygame',
    ],
    extras_require={
        'dev': [
            'cython',
            'pytest',
            'python-boilerplate',
        ],
    },

    # Other configurations
    zip_safe=False,
    platforms='any',
)
