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
def get_texture_from_path(path, theta=0, scale=1):
    '''Initializes texture from path'''
    if theta == 0 and scale == 1:
        return Texture(path)
    else:
        return get_texture(path).rotate(theta).rescale(scale)
    
def get_texture(texture_or_path, theta=0, scale=1):
    if isinstance(texture_or_path, str):
        return get_texture_from_path(texture_or_path, theta, scale)
    elif theta == 0 and scale == 1:
        return texture_or_path
    else:
        return texture_or_path.rotate(theta).scale(scale)

class Texture(object):

    def __init__(self, path):
        self._pil = PIL.Image.open(path)
        self._pil.load()
        self.path = path

    @property
    def width(self):
        return self._pil.width
    
    @property
    def height(self):
        return self._pil.height

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

    def __init__(self, path_or_texture, pos=(0, 0), 
                 rect=None, bbox=None, 
                 scale=1):
        self.texture = get_texture(path_or_texture)
        self.__crop(rect, bbox)
        self.__rescale(scale)
        super(AABB, self).__init__(pos=pos, shape=self.texture.shape)

    def draw(self, screen):
        screen.draw_image(self)

    def __crop(self, rect=None, bbox=None):
        '''Crop image to the specified rect or bounding box *inplace*'''

        # No-OP
        if rect is None and bbox is None:
            return
                
        if rect:
            xmin, ymin, dx, dy = rect
            xmax = xmin + dx
            ymax = ymin + dy
        elif bbox:
            xmin, xmax, ymin, ymax = bbox
        else:
            raise TypeError('rect or bbox must be specified')
        
        left, right = map(int, [xmin, xmax])
        if ymin <= 0 and ymax < 0:
            upper, lower = map(int, [-ymin, -ymax])
        else:
            H = self.height
            upper, lower = map(int, [H - ymax, H - ymin])

        img = self.texture._pil.crop([left, upper, right, lower])
        self.texture._pil = img
        
    def __rescale(self, scale):
        '''Rescale image to the given scale factor *inplace*'''
        
        if scale == 1:
            return
        
        shape = (self.texture._pil.width, self.texture._pil.height)
        shape = map(int, scale * asvector(shape))
        self.texture._pil = self.texture._pil.resize(shape)
        
         

class TileSheet(object):
    def __init__(self, path_or_texture, shape, origin=(0, 0)):
        if isinstance(path_or_texture, Texture):
            self.texture = path_or_texture
        else:
            self.texture = get_texture(path_or_texture)

            
