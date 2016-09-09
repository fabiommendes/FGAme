# -*- coding: utf8 -*-
'''
Re-define os objetos do módulo FGAme.physics e adiciona propriades extras de
renderização
'''

from __future__ import print_function
from FGAme import conf
from FGAme import physics
from FGAme.mathtools import asvector
from FGAme.util import lazy
from FGAme.draw import Color, colorproperty, Image
from FGAme.events import signal, EventDispatcher
from FGAme import draw

# Constantes
__all__ = ['AABB', 'Circle', 'Poly', 'RegularPoly', 'Rectangle']
black = Color('black')


class Body(physics.Body):
    long_press = signal(
        'long-press', 'key', delegate_to='_input')
    
    key_up = signal(
        'key-up', 'key', delegate_to='_input')
    
    key_down = signal(
        'key-down', 'key', delegate_to='_input')
    
    mouse_motion = signal(
        'mouse-motion', delegate_to='_input')
    
    mouse_button_up = signal(
        'mouse-button-up', 'button', delegate_to='_input')
    
    mouse_button_down = signal(
        'mouse-button-down', 'button', delegate_to='_input')
    
    mouse_long_press = signal(
        'mouse-long-press', 'button', delegate_to='_input')

    def __init__(self, *args, **kwds):
        # Extract visualization parameters
        image = {
            'image': kwds.pop('image', None)
            }
        for k in list(kwds):
            if k.startswith('image_'):
                image[k] = kwds.pop(k)
        self.color = kwds.pop('color', black)
        self.linecolor = kwds.pop('linecolor', None)
        self.linewidth = kwds.pop('linewidth', 1)
        self.visible = kwds.pop('visible', True)

        # Set the correct world
        self.world = kwds.pop('world', None)

        # Init physics object and visualization
        super(Body, self).__init__(*args, **kwds)
        self.__init_image(**image)



    def __init_image(self, image, image_offset=(0, 0), image_reference=None, **kwds):
        self._image = None
        self._drawshape = None
        
        if image is not None:
            # Get all image parameters
            img_kwds = {}
            for k, v in kwds.items():
                if k.startswith('image_'):
                    img_kwds[k[6:]] = v 
            
            if isinstance(image, str):
                image = Image(image, self.pos, **img_kwds)
            else:
                raise NotImplementedError
            self._image = image
            
            offset = asvector(image_offset)
            if image_reference in ['pos_ne', 'pos_nw', 'pos_se', 'pos_sw', 
                                   'pos_left', 'pos_right', 'pos_up', 'pos_down']:
                pos_ref = getattr(self, image_reference)
                pos_img_ref = getattr(image, image_reference)
                offset += pos_ref - pos_img_ref
            elif image_reference not in ['middle', None]:
                raise ValueError('invalid image reference: %r' % image_reference)
            image.offset = offset
        else:
            self._drawshape = self._init_drawshape(color=self.color or black, 
                                                   linecolor=self.linecolor, 
                                                   linewidth=self.linewidth)

    @lazy
    def _input(self):
        return conf.get_input()

    color = colorproperty('color')
    linecolor = colorproperty('linecolor')

    @property
    def image(self):
        img = self._image
        if img is None:
            return None
        img.pos = self.pos + img.offset
        return img

    @image.setter
    def image(self, value):
        if value is None:
            self._image = None
            return
        if isinstance(value, str):
            value = Image(value, self.pos)
        self._image = value

    @property
    def drawable(self):
        return self.image or self.drawshape
    
    @property
    def drawshape(self):
        if self._drawshape is None:
            return None
        self._drawshape.pos = self.pos
        return self._drawshape

    def show(self):
        '''Torna o objeto visível no mundo'''
        
        self.visible = True

    def hide(self):
        '''Desativa a renderização do objeto. O objeto ainda interage com os 
        outros objetos do mundo, somente não é mostrado na tela.'''
        
        self.visible = False

    def draw(self, screen):
        '''Desenha objeto em uma tela do tipo "canvas".'''
        
        img = self.image
        if img is not None:
            img.pos = self.pos + img.offset
            return img.draw(screen)
        else:
            return self.draw_shape(screen)

    def destroy(self):
        super(Body, self).destroy()
        self.world.remove(self)
    
    def _init_drawshape(self, color=None, linecolor=None, linewidth=1):
        bbox = self.bb
        cls = getattr(draw, type(bbox).__name__)
        return cls(*bbox, color=color, linecolor=linecolor, linewidth=linewidth)
        

class AABB(Body, physics.AABB):
    '''Objeto com a caixa de contorno de colisões dada por uma AABB.
    
    Objetos do tipo AABB não pode realizar rotações e possuem um momento
    de inércia infinito.
    '''

    def draw_shape(self, screen):
        if self._color is not None:
            color = self._color
            lw, lc = self.linewidth, self._linecolor
            screen.draw_aabb(self.aabb, color, lw, lc)

        elif self.linewidth:
            lw, lc = self.linewidth, self._linecolor
            screen.draw_aabb(self.aabb, black, lw, lc)

    @property
    def drawshape(self):
        if self._drawshape is None:
            return None
        self._drawshape.xmin = self.xmin
        self._drawshape.xmax = self.xmax
        self._drawshape.ymin = self.ymin
        self._drawshape.ymax = self.ymax
        return self._drawshape
    

class Circle(Body, physics.Circle):
    '''Objeto com a caixa de contorno circular.
    
    Círculos possuem rotação, apesar da mesma não ser renderizada na tela. Para
    criar um círculo irrotacional, é necessário iniciar com o momento de inércia
    infinito.'''

    def draw_shape(self, screen):
        if self._color is not None:
            color = self._color
            lw, lc = self.linewidth, self._linecolor
            screen.draw_circle(self.bb, color, lw, lc)

        elif self.linewidth:
            lw, lc = self.linewidth, self._linecolor
            screen.draw_circle(self.bb, black, lw, lc)


class Poly(Body, physics.Poly):
    '''Objeto com a caixa de contorno poligonal.
    
    Polígonos são as caixas de contorno mais versáteis que a FGAme suporta. 
    Observe que a poligonal deve ser convexa e definida no sentido anti-
    horário. Apesar da versatilidade, colisões do tipo polígono-polígono são 
    as mais caras de processar.'''

    def draw_shape(self, screen):
        if self._color is not None:
            color = self._color
            lw, lc = self.linewidth, self._linecolor
            screen.draw_poly(self.bb, color, lw, lc)

        elif self.linewidth:
            lw, lc = self.linewidth, self._linecolor
            screen.draw_poly(self.bb, black, lw, lc)
    
    def _init_drawshape(self, color=None, linecolor=None, linewidth=1):
        return draw.Poly(self.bb, color=color, linecolor=linecolor, 
                         linewidth=linewidth)
    

class Rectangle(Poly, physics.Rectangle):
    '''Semelhante a Poly, mas restrito a retângulos.
    
    Caso o usuário deseje trabalhar com retângulos, esta classe torna-se mais
    conveniente de trabalhar que a classe genérica Poly.'''


class RegularPoly(Poly, physics.RegularPoly):
    '''Semelhante a Poly, mas restrito a polígonos regulares.'''

    
class Group(Body, physics.Group):
    def draw(self, screen):
        for obj in self:
            obj.draw(screen) 
    
if __name__ == '__main__':
    x = AABB(shape=(100, 200), world=set())
    type(x)
    print(x.mass)
