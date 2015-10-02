import os
try:
    import PIL
except ImportError:
    PIL = None


class TextureManager(object):
    EXTENSIONS = ['png', 'gif', 'bmp', 'jpg', 'jpeg']

    def __init__(self, path=None):
        self._images = {}
        self._pillow = {}
        if path is None:
            path = get_default_image_path()
        self._path = os.path.abspath(path)

    def save_image(self, name, image):
        self._images[name] = image

    def get_image(self, name):
        try:
            return self._images[name]
        except KeyError:
            path = self.find_image_path(name)
            self._images[name] = img = self.image_from_path(path)
            return img

    def discard_image(self, name):
        if name in self._images:
            del self._images[name]
        if name in self._pillow:
            del self._pillow[name]

    def clear(self):
        self._images.clear()
        self._pillow.clear()

    def find_image_path(self, name):
        return os.path.join(self._path, name)

    # Funções para subclasses #################################################
    def image_from_path(self, path):
        img = PIL.Image.open(path)
        return self.import_image(img)

    def import_image(self, img):
        return img

    def export_image(self, img):
        return img

    # Transformações ##########################################################
    # Utilizam a biblioteca pillow, caso não exista suporte nativo às funções
    # utilizadas na biblioteca
    def mirror(self, name_or_img, horizontal=True):
        pass

    def slice(self, name_or_img, rect):
        pass

    def rescale(self, name_or_img, factor):
        pass

    def irotate(self, name_or_img, factor):
        pass

    def invert(self, name_or_img):
        pass

    # Informações sobre a imagem ##############################################
    def get_shape(self, img):
        raise NotImplementedError


###############################################################################
#                                Funções úteis
###############################################################################
def get_default_image_path():
    '''Retorna o caminho para a pasta /images/ abaixo do caminho do script
    principal em execução'''

    # script_path = sys.modules['__main__'].__file__
    # base_path = os.path.split(script_path)[0]
    # path = os.path.join(base_path, 'images')
    return ''


class PyGameTextureManager(TextureManager):

    def image_from_path(self, path):
        import pygame
        return pygame.image.load(path)

    def get_shape(self, img):
        x, y, width, height = img.get_rect()
        return width, height
