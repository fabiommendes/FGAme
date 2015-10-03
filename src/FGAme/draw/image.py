'''
A FGAme possui um método de armazenar e acessar imagens
...

Imagens
=======

As imagens podem ser inicializadas facilmente a partir da classe Image(), 
bastando para isso especificar o caminho para o arquivo de imagem

>>> img = Image('chimp', pos=(400, 200), reference='bottom-left')


Isto criará uma imagem 

    
  
'''
import os
from FGAme.resources import resources
from FGAme.draw import AABB
from FGAme.mathtools import asvector
from FGAme.util import lru_cache
try:
    import PIL.Image
except ImportError:
    from warnings import warn
    warn('PIL not found. FGAme will not be able to render images and textures')

class Texture(object):
    '''Representa uma textura.'''

    def __init__(self, path):
        if not os.path.isabs(path):
            path = resources.find_image_path(path)
        self._pil = PIL.Image.open(path)
        self._pil.load()
        self.path = path
        
    @classmethod
    def from_image(cls, image):
        '''Load texture from image object'''
        
        if isinstance(image, PIL.Image.Image):
            return Texture.from_pil_image(image)
        else:
            raise TypeError('unsupported image: %r' % image)
    
    @classmethod
    def __from_pil_image(cls, image):
        new = object.__new__(cls)
        new._pil = image
        new.path = None
        return new
    
    @property
    def width(self):
        return self._pil.width
    
    @property
    def height(self):
        return self._pil.height

    @property
    def shape(self):
        return (self._pil.width, self._pil.height)

    @property
    def mode(self):
        return self._pil.mode

    def get_pil_data(self):
        '''Return the PIL.Image data for the Texture object'''

        return self._pil

    def set_backend_data(self, value):
        '''Saves the backend-specific representation of the texture'''
        
        self.data = value

    def get_backend_data(self, value):
        '''Returns the backend-specific representation of the texture'''
        try:
            return self.data
        except AttributeError:
            raise RuntimeError('data attribute is not defined')


class Image(AABB):

    '''Imagem/pixmap não-animado com uma posição dada no mundo.'''

    def __init__(
            self, path_or_texture, pos=(0, 0), 
            rect=None, bbox=None, 
            scale=1, resampling='nearest',
            reference=None):
        
        self.texture = get_texture(path_or_texture)
        self.__crop(rect, bbox)
        self.__rescale(scale, resampling)
        super(AABB, self).__init__(pos=pos, shape=self.texture.shape)
        
        if reference is not None:
            self.pos = pos - self.get_reference_point(reference)
            

    REFERENCE_NAMES = {
        'bottom-left': 'pos_sw',
        'bottom-right': 'pos_se',
        'top-left': 'pos_nw',
        'top-right': 'pos_ne',
        'bottom': 'pos_down',
        'top': 'pos_up',
        'down': 'pos_down',
        'up': 'pos_up',
        'left': 'pos_left',
        'right': 'pos_right',
        'center': 'pos',
    }
    for k, v in list(REFERENCE_NAMES.items()):
        if '-' in k:
            k = '-'.join(k.split('-')[::-1])
            REFERENCE_NAMES[k] = v
    del k, v
            
    def get_reference_point(self, ref):
        #TODO: move to HasAABB or something more generic
        point = getattr(self, self.REFERENCE_NAMES.get(ref, ref))
        return asvector(point)

    def draw(self, screen):
        screen.draw_image(self)

    def copy(self):
        new = super(Image, self).copy()
        new.texture = self.texture
        return new

    def crop(self, rect=None, bbox=None):
        '''Return a cropped copy of image to the specified `rect` or bounding 
        box `bbox`.'''
        
        new = self.copy()
        new.__crop(rect, bbox)
        return new 
    
    def rescale(self, scale, method=None):
        '''Return a rescaled copy of image.
        
        Accept one of the following methods: "nearest", "linear", "cubic", or 
        "lanczos". "fastest" is an alias to "nearest", which is indeed the 
        fastest method and "best" is an alias to "lanczos", which is slower but
        usually yields the results with least artifacts. 
        '''
        
        new = self.copy()
        new.__rescale(scale, method)
        return new

    #
    # Inplace modifiers
    #
    def __crop(self, rect, bbox):

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
        
    def __rescale(self, scale, resample):
        '''Rescale image to the given scale factor *inplace*'''
        
        if scale == 1:
            return
        
        default = 'nearest' if scale == int(scale) else 'linear'
        try:
            resample = dict(
                default=default,
                fastest=PIL.Image.NEAREST,
                nearest=PIL.Image.NEAREST,
                linear=PIL.Image.BILINEAR,
                bilinear=PIL.Image.BILINEAR,
                cubic=PIL.Image.BICUBIC,
                bicubic=PIL.Image.BICUBIC,
                lanczos=PIL.Image.LANCZOS,
                best=PIL.Image.LANCZOS,
            )[resample]
        except KeyError:
            raise ValueError('invalid sampling method: %r' % resample)
        
        shape = (self.texture._pil.width, self.texture._pil.height)
        shape = map(int, scale * asvector(shape))
        self.texture._pil = self.texture._pil.resize(shape, resample)
        
         

class TileSheet(object):
    def __init__(self, path_or_texture, shape, origin=(0, 0)):
        if isinstance(path_or_texture, Texture):
            self.texture = path_or_texture
        else:
            self.texture = get_texture(path_or_texture)

            
#
# Utility functions
#
def get_texture(texture_or_path, theta=0, scale=1):
    '''Return texture from path or object holding image data.'''
    
    if isinstance(texture_or_path, str):
        return __get_texture_from_path(texture_or_path)
    elif isinstance(texture_or_path, Texture):
        return texture_or_path
    else:
        return Texture.from_image(texture_or_path)

@lru_cache
def __get_texture_from_path(path):
    return Texture(path)

if __name__ == '__main__':
    import doctest
    doctest.testmod()