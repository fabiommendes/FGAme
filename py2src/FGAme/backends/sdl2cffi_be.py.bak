from math import trunc
import ctypes
import sdl
import sdl.sdlgfx as gfx
from FGAme.core.screen import Canvas
from FGAme.input import Input
from FGAme.mainloop import MainLoop
from FGAme.draw import Color

#
# Module constants
#
HAS_INIT_SDL_VIDEO = False


class SDL2Canvas(Canvas):

    '''Implementa a interface Screen, utilizando a biblioteca Pygame'''

    # Local class-based caches
    _gfx = gfx
    _sdl = sdl

    def show(self):
        # Init video
        global HAS_INIT_SDL_VIDEO
        if not HAS_INIT_SDL_VIDEO:
            self._no_error(sdl.SDL_Init(sdl.SDL_INIT_VIDEO))
        else:
            HAS_INIT_SDL_VIDEO = True

        # Create window
        self._window = self._no_null(
            sdl.SDL_CreateWindow(
                b"FGAme App",
                sdl.SDL_WINDOWPOS_CENTERED,
                sdl.SDL_WINDOWPOS_CENTERED,
                self.width,
                self.height,
                sdl.SDL_WINDOW_SHOWN))

        # Create a renderer
        flags = sdl.SDL_RENDERER_SOFTWARE
        self._renderer = self._no_null(
            sdl.SDL_CreateRenderer(self._window, -1, flags))

        # Create a rect instance that stores the window shape
        self._screen_rect = self._no_null(
            sdl.SDL_Rect(x=0, y=0, w=self.width, h=self.height))

        # Saves background color
        if self.background is not None:
            R, B, G, A = Color(self.background)
            self._bg_color = (R << 24) + (G << 16) + (B << 8) + A
        else:
            self._bg_color = None
        self._LP_short = gfx.aapolygonRGBA.argtypes[1]

    def flip(self):
        sdl.SDL_RenderPresent(self._renderer)

    def _map_point(self, point):
        x, y = point
        return (trunc(x), trunc(self.height - y))

    def _sdl_error(self):
        msg = sdl.SDL_GetError()
        raise RuntimeError('SDL error: %s' % msg)

    def _no_error(self, value):
        if value != 0:
            msg = sdl.SDL_GetError()
            raise RuntimeError('SDL error (%s): %s' % (value, msg))

    def _no_null(self, value):
        if not value:
            msg = sdl.SDL_GetError()
            raise RuntimeError('SDL error (%s): %s' % (value, msg))
        return value

    #
    # Desenho de figuras geométricas primitivas
    #
    def draw_raw_aabb_solid(self, aabb, color):
        Y = self.height
        R, G, B, A = color
        if gfx.boxRGBA(
                self._renderer,
                trunc(aabb.xmin),
                trunc(Y - aabb.ymax),
                trunc(aabb.xmax),
                trunc(Y - aabb.ymin),
                R, G, B, A) != 0:
            self._sdl_error()

    def draw_raw_circle_solid(self, circle, color):
        self._no_error(
            gfx.filledCircleRGBA(
                self._renderer,
                trunc(circle.x),
                trunc(self.height - circle.y),
                trunc(circle.radius), *color))

        self._no_error(
            gfx.aacircleRGBA(
                self._renderer,
                trunc(circle.x),
                trunc(self.height - circle.y),
                trunc(circle.radius), *color))

    def draw_raw_circle_border(self, circle, width, color):
        safe_operator = self._no_error
        x, y = trunc(circle.x), trunc(self.height - circle.y)
        renderer = self._renderer

        if width == 1:
            radius = trunc(circle.radius)
            safe_operator(gfx.aacircleRGBA(renderer, x, y, radius, *color))
        else:
            # Very ugly hack! can it be better?
            min_r = trunc(circle.radius - width / 2)
            max_r = trunc(circle.radius + width / 2)
            for r in range(min_r, max_r):
                safe_operator(gfx.aacircleRGBA(renderer, x, y, r, *color))

    def _get_poly_xy(self, poly):
        '''Implementação comum que cria lista de posições x e y para passsar
        para draw_raw_poly_solid e draw_raw_poly_border'''
        N = len(poly)
        height = self.height
        int16_array = ctypes.c_int16 * N
        Xc = int16_array()
        Yc = int16_array()
        for i, pt in enumerate(poly):
            Xc[i] = trunc(pt.x)
            Yc[i] = trunc(height - pt.y)
        return Xc, Yc

    def draw_raw_poly_solid(self, poly, color):
        N = len(poly)
        X, Y = self._get_poly_xy(poly)
        color = Color(color)
        self._no_error(
            gfx.aapolygonRGBA(
                self._renderer, X, Y, N, *color))
        self._no_error(
            gfx.filledPolygonRGBA(
                self._renderer, X, Y, N, *color))

    def draw_raw_segment(self, segment, width, color):
        height = self.height
        pt1, pt2 = segment
        if width == 1:
            self._no_error(
                gfx.aalineRGBA(
                    self._renderer,
                    trunc(pt1.x),
                    trunc(height - pt1.y),
                    trunc(pt2.x),
                    trunc(height - pt2.y),
                    *color))
        else:
            self._no_error(
                gfx.thickLineRGBA(
                    self._renderer,
                    trunc(pt1.x),
                    trunc(height - pt1.y),
                    trunc(pt2.x),
                    trunc(height - pt2.y),
                    trunc(width),
                    *color))

    def draw_raw_poly_border(self, poly, width, color):
        # TODO: desenhar linhas espessas
        N = len(poly)
        X, Y = self._get_poly_xy(poly)
        self._no_error(
            gfx.aapolygonRGBA(
                self._renderer, X, Y, N, *Color(color)))

    def clear_background(self, color=None):
        renderer = self._renderer
        sdl.SDL_RenderClear(renderer)

        ret = 0
        if color is None and self._bg_color is not None:
            ret = gfx.boxColor(
                renderer, 0, self.height, self.width, 0, self._bg_color)
        else:
            R, G, B, A = Color(color)
            ret = gfx.boxRGBA(
                renderer, 0, self.height, self.width, 0, R, G, B, A)

        if ret != 0:
            msg = sdl.SDL_GetError()
            raise RuntimeError('SDL error: %s' % msg)


class SDL2Input(Input):

    '''Objetos do tipo listener.'''

    #=========================================================================
    # Conversões entre strings e teclas
    #=========================================================================
# Setas direcionais
#     KEY_CONVERSIONS = {
#         'up': SDLK_UP, 'down': SDLK_DOWN, 'left': SDLK_LEFT, 'right': SDLK_RIGHT,
#         'return': SDLK_RETURN, 'space': SDLK_SPACE, 'enter': SDLK_RETURN,
#     }
#
# Adiciona as letras e números
#     chars = '0123456789' + string.ascii_lowercase
#     for c in chars:
#         KEY_CONVERSIONS[c] = getattr(sdl, 'SDLK_' + c)

    #
    # Laço principal de escuta de eventos
    #

    def poll(self):
        for event in sdl_ext.get_events():
            if event.type == sdl.SDL_QUIT:
                raise SystemExit
            elif event.type == sdl.SDL_KEYDOWN:
                self.on_key_down(event.key.keysym.sym)
            elif event.type == sdl.SDL_KEYUP:
                self.on_key_up(event.key.keysym.sym)
            elif event.type == sdl.SDL_MOUSEMOTION:
                # TODO: converter para coordenadas locais em screen
                # self.on_mouse_motion(event.pos)
                pass

        # self.on_long_press()


class SDL2MainLoop(MainLoop):

    '''The SDL2 main loop'''
