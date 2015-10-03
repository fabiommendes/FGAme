import ctypes
from math import trunc
import sys
from warnings import warn

import sdl2
import sdl2.ext as sdl2_ext
import sdl2.sdlgfx as gfx

from FGAme.core.screen import Canvas
from FGAme.input import Input
from FGAme.mainloop import MainLoop
from FGAme.draw import Color
from FGAme import conf

#
# Module constants
#
HAS_INIT_SDL_VIDEO = False


class SDL2Canvas(Canvas):

    '''Implementa a interface Screen, utilizando a biblioteca Pygame'''

    # Local class-based caches
    _gfx = gfx
    _sdl2 = sdl2

    def show(self):
        # Init video
        global HAS_INIT_SDL_VIDEO
        if not HAS_INIT_SDL_VIDEO:
            self._no_error(sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO))
        else:
            HAS_INIT_SDL_VIDEO = True

        # Create window
        self._window = self._no_null(
            sdl2.SDL_CreateWindow(
                b"FGAme Game",
                sdl2.SDL_WINDOWPOS_CENTERED,
                sdl2.SDL_WINDOWPOS_CENTERED,
                self.width,
                self.height,
                sdl2.SDL_WINDOW_SHOWN))
        self._surface = sdl2.SDL_GetWindowSurface(self._window)
        
        # Create a renderer
        # flags = sdl2.SDL_RENDERER_SOFTWARE
        # flags = sdl2.SDL_RENDERER_ACCELERATED
        # flags = sdl2.SDL_RENDERER_PRESENTVSYNC
        flags = sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC
        self._renderer = self._no_null(
            sdl2.SDL_CreateRenderer(self._window, -1, flags))

        # Create a rect instance that stores the window shape
        self._screen_rect = self._no_null(
            sdl2.SDL_Rect(x=0, y=0, w=self.width, h=self.height))

        # Saves background color
        if self.background is not None:
            R, B, G, A = Color(self.background)
            self._bg_color = (R << 24) + (G << 16) + (B << 8) + A
        else:
            self._bg_color = None
        self._LP_short = gfx.aapolygonRGBA.argtypes[1]

        # Flip image
        self.flip()

    def flip(self):
        sdl2.SDL_RenderPresent(self._renderer)

    def _map_point(self, point):
        x, y = point
        return (trunc(x), trunc(self.height - y))

    def _sdl_error(self):
        msg = sdl2.SDL_GetError()
        raise RuntimeError('SDL error: %s' % msg)

    def _no_error(self, value):
        if value != 0:
            msg = sdl2.SDL_GetError()
            msg = 'SDL error (%s): %s' % (value, msg)

            # TODO: Figure out what is the problem with PyPy and some GFX
            # functions. For now we are just ignoring errors and rendering
            # some figures improperly
            if 'PyPy' in sys.version:
                warn(msg)
            else:
                raise RuntimeError(msg)

    def _no_null(self, value):
        if not value:
            msg = sdl2.SDL_GetError()
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

    def draw_raw_texture(self, texture, pos=(0, 0)):
        try:
            sdl_texture = texture.data
        except AttributeError:
            pil_data = texture.get_pil_data()
            if pil_data.mode not in 'RGBA':
                pil_data = pil_data.convert('RGBA')
            sdl_texture = self.__convert_PIL_to_SDL(pil_data)
            texture.set_backend_data(sdl_texture)

        dx = texture.width 
        dy = texture.height
        x, y = pos
        y = self.height - y - dy
        rect_src = sdl2.SDL_Rect(0, 0, dx, dy)
        rect_dest = sdl2.SDL_Rect(int(x), int(y), dx, dy)
        sdl2.SDL_RenderCopy(
            self._renderer,  # renderer
            sdl_texture,     # source
            rect_src,        # source rect
            rect_dest,       # destination rect
        )
            

    def __convert_PIL_to_SDL(self, image):
        # Copied from sdl2.ext.image.load_image()
        # Thanks to Marcus von. Appen!
        endian = sdl2.endian
        mode = image.mode
        width, height = image.size
        rmask = gmask = bmask = amask = 0
        if mode in ("1", "L", "P"):
            # 1 = B/W, 1 bit per byte
            # "L" = greyscale, 8-bit
            # "P" = palette-based, 8-bit
            pitch = width
            depth = 8
        
        elif mode == "RGB":
            # 3x8-bit, 24bpp
            if endian.SDL_BYTEORDER == endian.SDL_LIL_ENDIAN:
                rmask = 0x0000FF
                gmask = 0x00FF00
                bmask = 0xFF0000
            else:
                rmask = 0xFF0000
                gmask = 0x00FF00
                bmask = 0x0000FF
            depth = 24
            pitch = width * 3
        
        elif mode in ("RGBA", "RGBX"):
            # RGBX: 4x8-bit, no alpha
            # RGBA: 4x8-bit, alpha
            if endian.SDL_BYTEORDER == endian.SDL_LIL_ENDIAN:
                rmask = 0x000000FF
                gmask = 0x0000FF00
                bmask = 0x00FF0000
                if mode == "RGBA":
                    amask = 0xFF000000
            else:
                rmask = 0xFF000000
                gmask = 0x00FF0000
                bmask = 0x0000FF00
                if mode == "RGBA":
                    amask = 0x000000FF
            depth = 32
            pitch = width * 4
        else:
            # We do not support CMYK or YCbCr for now
            raise TypeError("unsupported image format")

        pxbuf = image.tostring()
        surface = sdl2.SDL_CreateRGBSurfaceFrom(pxbuf, width, height,
                                                depth, pitch, rmask,
                                                gmask, bmask, amask)
        return sdl2.SDL_CreateTextureFromSurface(self._renderer, surface)
        

    
    
    def clear_background(self, color=None):
        renderer = self._renderer
        sdl2.SDL_RenderClear(renderer)

        ret = 0
        if color is None and self._bg_color is not None:
            ret = gfx.boxColor(
                renderer, 0, self.height, self.width, 0, self._bg_color)
        else:
            R, G, B, A = Color(color)
            ret = gfx.boxRGBA(
                renderer, 0, self.height, self.width, 0, R, G, B, A)

        if ret != 0:
            msg = sdl2.SDL_GetError()
            raise RuntimeError('SDL error: %s' % msg)


class SDL2Input(Input):

    '''Objetos do tipo listener.'''

    # Keyboard key codes
    _key_transformations = {}
    _key_conversions = {}
    for attr in dir(sdl2):
        if attr.startswith('SDLK_'):
            value = getattr(sdl2, attr)
            name = attr[5:].lower()
            name = _key_transformations.get(name, name)
            _key_conversions[value] = name
    del name, value, attr

    # Mouse buttons
    _mouse_conversions = {
        sdl2.mouse.SDL_BUTTON_LEFT: 'left',
        sdl2.mouse.SDL_BUTTON_MIDDLE: 'middle',
        sdl2.mouse.SDL_BUTTON_RIGHT: 'right',
        sdl2.mouse.SDL_BUTTON_X1: 'wheel-up',
        sdl2.mouse.SDL_BUTTON_X2: 'wheel-down'
    }

    def poll(self):
        key_get = self._key_conversions.get
        mouse_button_get = self._mouse_conversions.get
        window_height = conf.get_resolution()[1]

        for event in sdl2_ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                raise SystemExit
            elif event.type == sdl2.SDL_KEYDOWN:
                self.process_key_down(key_get(event.key.keysym.sym))
            elif event.type == sdl2.SDL_KEYUP:
                self.process_key_up(key_get(event.key.keysym.sym))
            elif event.type == sdl2.SDL_MOUSEMOTION:
                event = event.motion
                x = event.x
                y = window_height - event.y
                self.process_mouse_motion((x, y))
            elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                event = event.button
                x = event.x
                y = window_height - event.y
                button = mouse_button_get(event.button)
                self.process_mouse_button_up(button, (x, y))
            elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                event = event.button
                x = event.x
                y = window_height - event.y
                button = mouse_button_get(event.button)
                self.process_mouse_button_down(button, (x, y))

        self.process_long_press()
        self.process_mouse_longpress()


class SDL2MainLoop(MainLoop):

    '''The SDL2 main loop'''
