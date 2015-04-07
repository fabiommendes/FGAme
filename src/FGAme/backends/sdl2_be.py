from FGAme.backends.core import Canvas, InputListener
# import pygame
#import sdl2
#import sdl2.ext
#from sdl2.sdlgfx import *
#from sdl2 import *
import string
from math import trunc
import ctypes      

class SDLCanvas(Canvas):
    '''Implementa a interface Screen, utilizando a biblioteca Pygame'''

    def init(self):
        import sdl2
        import sdl2.sdlgfx as gfx
        self._window = sdl2.SDL_CreateWindow(b"FGAme App",
                              sld2.SDL_WINDOWPOS_CENTERED, sld2.SDL_WINDOWPOS_CENTERED,
                              width, height, sld2.SDL_WINDOW_SHOWN)
        self._renderer = sdl2.SDL_CreateRenderer(self._window, -1,
                                            sld2.SDL_RENDERER_ACCELERATED |
                                            sld2.SDL_RENDERER_PRESENTVSYNC)
        self._screen_rect = sdl2.SDL_Rect(x=0, y=0, w=width, h=height)
        R, G, B = self.background
        self._bg_color = (R << 24) + (G << 16) + (B << 8) + 255
        self.sdl2 = sdl2
        self.gfx = gfx
        self._LP_short = aapolygonRGBA.argtypes[1]
        
    def flip(self):
         self.sdl2.SDL_RenderPresent(self._renderer)

    def _map_point(self, point):
        x, y = point
        X, Y = self.width, self.height
        y = Y - y
        return (trunc(x), trunc(y))

    #===========================================================================
    # Desenho
    #===========================================================================
    def draw_circle(self, pos, radius, color='black', solid=True):
        x, y = self._map_point(pos)
        r = trunc(radius)
        color = Color(color)
        self.gfx.aacircleRGBA(self._renderer, x, y, r, *color)
        self.gfx.filledCircleRGBA(self._renderer, x, y, r, *color)

    def draw_poly(self, points, color='black', solid=True):
        points = [ self._map_point(pt) for pt in points ]
        N = len(points)
        X = [ x for (x, y) in points ]
        Y = [ y for (x, y) in points ]
        Xc = (ctypes.c_int16 * len(X))()
        Yc = (ctypes.c_int16 * len(Y))()
        for i in range(len(X)):
            Xc[i] = X[i]
            Yc[i] = Y[i]

        color = Color(color)
#        if aapolygonRGBA(self._renderer, Xc, Yc, len(X), R, G, B, alpha) != 0:
#            msg = SDL_GetError()
#            raise RuntimeError('SDL error: %s' % msg)
        if self.gfx.filledPolygonRGBA(self._renderer, Xc, Yc, len(X), *color) != 0:
            msg = self.sdl2.SDL_GetError()
            raise RuntimeError('SDL error: %s' % msg)

    def draw_rect(self, pos, shape, color='black', solid=True, alpha=255):
        R, G, B = color
        x, y = self._map_point(pos)
        w, h = map(int, shape)
        if boxRGBA(self._renderer, x, y - h, x + w, y, R, G, B, alpha) != 0:
            msg = SDL_GetError()
            raise RuntimeError('SDL error: %s' % msg)

    def clear_background(self, color=None):
        self.sdl2.SDL_RenderClear(self._renderer)
        if color is None:
            ret = boxColor(self._renderer, 0, self.height, self.width, 0, self._bg_color)
        else:
            R, G, B = color
            ret = boxRGBA(self._renderer, 0, self.height, self.width, 0, R, G, B, 255)

        if ret != 0:
            msg = self.sdl2.SDL_GetError()
            raise RuntimeError('SDL error: %s' % msg)        
        

class SDL2Input(Input):
    '''Objetos do tipo listener.'''

    #===========================================================================
    # Conversões entre strings e teclas
    #===========================================================================
#     # Setas direcionais
#     KEY_CONVERSIONS = {
#         'up': SDLK_UP, 'down': SDLK_DOWN, 'left': SDLK_LEFT, 'right': SDLK_RIGHT,
#         'return': SDLK_RETURN, 'space': SDLK_SPACE, 'enter': SDLK_RETURN,
#     }
# 
#     # Adiciona as letras e números
#     chars = '0123456789' + string.ascii_lowercase
#     for c in chars:
#         KEY_CONVERSIONS[c] = getattr(sdl2, 'SDLK_' + c)

    #===========================================================================
    # Laço principal de escuta de eventos
    #===========================================================================

    def query(self):
        for event in self.sdl2.ext.get_events():
            if event.type == self.sld2.SDL_QUIT:
                raise SystemExit
            elif event.type == self.sld2.SDL_KEYDOWN:
                self.on_key_down(event.key.keysym.sym)
            elif event.type == self.sld2.SDL_KEYUP:
                self.on_key_up(event.key.keysym.sym)
            elif event.type == self.sld2.SDL_MOUSEMOTION:
                # TODO: converter para coordenadas locais em screen
                #self.on_mouse_motion(event.pos)
                pass

        self.on_long_press()
