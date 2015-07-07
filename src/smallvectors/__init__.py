'''
============
Smallvectors
============

The ``smallvectors`` library provides efficient implementations (as far as
python goes) for vectors, matrices and other linear algebra constructs of
small dimensionality. This code is useable and stable, but it is still beta
and many classes may be not fully implemented or may not be optimized yet.
'''

from .sequence import seq
from .cartesian import *
from .vec2 import *
from .vec3 import *
from .vec4 import *
from .quaternion import *
from .vecutils import *
from .matrix import *
