import functools
import six
from FGAme.draw import AABB
from FGAme.mathtools import asvector

try:
    import PIL.Image
except ImportError:
    from warnings import warn
    warn('PIL not found. FGAme will not be able to render images and textures')


if six.PY3:
    def lru_cache(func):
        return functools.lru_cache(maxsize=512)(func)
else:
    def lru_cache(func):
        D = {}

        @functools.wraps(func)
        def decorated(*args):
            try:
                return D[args]
            except KeyError:
                result = func(*args)
                while len(D) > 512:
                    D.popitem()
                return result
        return decorated


@lru_cache
def get_texture(path, theta=0, scale=1):
    if theta == 0 and scale == 1:
        return Texture(path)
    else:
        return get_texture(path).rotate(theta).rescale(scale)


class Texture(object):

    def __init__(self, path):
        self._pil = PIL.Image.open(path)
        self._pil.load()
        self.path = path

    def get_pil_data(self):
        '''Retorna um objeto do tipo PIL.Image.Image'''

        return self._pil

    def set_data(self, value):
        self.data = value

    def get_data(self, value):
        try:
            return self.data
        except AttributeError:
            raise RuntimeError('data attribute is not defined')

    @property
    def shape(self):
        return (self._pil.width, self._pil.height)

    @property
    def mode(self):
        return self._pil.mode


class Image(AABB):

    '''Define uma imagem/pixmap não-animado'''

    # manager = PyGameTextureManager()
    canvas_primitive = 'image'

    def __init__(self, path_or_texture, pos=(0, 0), reference='center'):
        if isinstance(path_or_texture, Texture):
            self.texture = path_or_texture
        else:
            self.texture = get_texture(path_or_texture)

        shape = asvector(self.texture.shape)
        if reference == 'center':
            pos = asvector(pos)
        elif reference == 'origin':
            pos = pos + self.shape / 2
        else:
            raise ValueError('invalid reference: %r' % reference)

        super(AABB, self).__init__(pos=pos, shape=shape)

    def draw(self, screen):
        screen.draw_image(self)
