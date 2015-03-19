#-*- coding: utf8 -*-
from FGAme.mathutils import Vector
from FGAme.draw import Color, color_property
from math import trunc

#===============================================================================
# Classe Screen genérica
#===============================================================================
class Screen(object):
    '''Classe que define a funcionalidade básica de todos os backends que 
    gerenciam a disponibilização de imagens na tela do computador.
    
    Existem dois modelos de renderização disponíveis
    
        * O modelo Canvas (ou tela) utiliza a metáfora de pintura, onde os
          pixels da tela são "pintados" a cada frame de renderização.
          
        * O modelo LiveTree delega a pintura para um backend mais básico que 
          determina o instante preciso do frame de renderização e quais partes
          da tela devem ser re-escritas com base numa árvore que guarda e 
          atualiza as funções de renderização.
    '''
    is_canvas = False
    background = color_property('background')

    def __init__(self, shape=(800, 600), pos=(0, 0), zoom=1, background=None):
        self.width, self.height = shape
        self.pos = Vector(*pos)
        self.zoom = zoom
        self.background = background
        self._direct = True
        self.init()

    def init(self):
        '''Executado ao fim da inicialização. Sub-classes podem sobrescrever
        este método ao invés do método __init__.'''
        
        pass
    
    def start(self):
        '''Deve ser chamado como primeira função para iniciar explicitamente a 
        tela e para abrir e mostrar a janela de jogo.'''
        
        pass

    @property
    def shape(self):
        return self.width, self.height

#===============================================================================
# Classe Canvas: backends baseados em renderização do tipo "pintura"
#===============================================================================
class Canvas(Screen):
    '''Sub-classes implementam a metáfora de "pintura" para a renderização das
    imagens.
    
    As sub-implementações devem saber como renderizar objetos geométricos 
    básicos como círculos, linhas, pontos, polígonos, etc.
    '''
    is_canvas = True
    
    def __init__(self, shape=(800, 600), pos=(0, 0), zoom=1, background=None):
        super(Canvas, self).__init__(shape, pos, zoom, background)
        self._drawing_funcs = {}
    
    def start(self):
        self.clear_background('white')
        self.flip()

    def flip(self):
        '''Transmite o buffer de pintura para a tela do computador'''
        
        raise NotImplementedError

    #===========================================================================
    # Context managers
    #===========================================================================
    def __enter__(self):
        if self.background is not None:
            self.clear_background(self.background)

    def __exit__(self, *args):
        self.flip()
        
    #===========================================================================
    # Objetos primitivos
    #===========================================================================
    def paint_circle(self, pos, radius, color='black', solid=True):
        '''Pinta um círculo especificando a posição do centro, seu raio e 
        opcionalmente a cor.
        
        Se a opção solid=True (padrão), desenha um círculo sólido. Caso 
        contrário, desenha apenas uma linha'''
        
        raise NotImplementedError

    def paint_poly(self, L_points, color='black', solid=True):
        raise NotImplementedError

    def paint_aabb(self, xmin, xmax, ymin, ymax, color='black', solid=True):
        dx, dy = xmax - xmin, ymax - ymin
        self.draw_rect((xmin, ymin), (dx, dy), color=color, solid=solid)

    def paint_rect(self, pos, shape, color='black', solid=True):
        x, y = pos
        w, h = shape
        self.draw_poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], color, solid)

    def paint_line(self, pt1, pt2, color='black', solid=True):
        raise NotImplementedError

    def clear_background(self, color=None):
        raise NotImplementedError
    
    #===========================================================================
    # Objetos derivados
    #===========================================================================
    def draw_tree(self, tree):
        '''Renderiza uma DrawingTree chamando a função correspondente para 
        desenhar cada objeto'''
        
        funcs = self._drawing_funcs
        for obj in tree.walk():
            try:
                draw_func = funcs[type(obj)]
            except KeyError:
                tt = type(obj)
                for T in tt.mro():
                    if T in funcs:
                        draw_func = funcs[tt] = funcs[T]
                        break
                else:
                    # Testa explicitamente
                    if getattr(tt, 'is_circle', False):
                        draw_func = funcs[tt] = self.draw_circle
                    elif getattr(tt, 'is_rect', False):
                        draw_func = funcs[tt] = self.draw_rect
                    elif getattr(tt, 'is_poly', False):
                        draw_func = funcs[tt] = self.draw_poly    
                    elif getattr(tt, 'is_tree', False):
                        draw_func = funcs[tt] = self.draw_tree
                    else:
                        raise TypeError('no method for drawing %s objects' % type(obj).__name__)
                    
            draw_func(obj)
            
    def draw_circle(self, circle):
        '''Desenha um círculo utilizando as informações de geometria, cor e 
        localização do objeto `circle` associado.
        
        Nota: diferentemente das funções do tipo paint_*, as funções do tipo
        draw_* adaptam automaticamente a renderização para os padrões de zoom e
        deslocamento da tela.'''
        
        if self._direct:
            self.paint_circle(circle.pos, circle.radius, circle.color, circle.solid)
        else:
            raise NotImplementedError
        
    def draw_rect(self, rect):
        '''Desenha um círculo utilizando as informações de geometria, cor e 
        localização do objeto `circle` associado.
        
        Nota: diferentemente das funções do tipo paint_*, as funções do tipo
        draw_* adaptam automaticamente a renderização para os padrões de zoom e
        deslocamento da tela.'''
        
        if self._direct:
            self.paint_rect(rect.pos, rect.shape, rect.color, rect.solid)
        else:
            raise NotImplementedError
        
    def draw_poly(self, poly):
        '''Desenha um círculo utilizando as informações de geometria, cor e 
        localização do objeto `circle` associado.
        
        Nota: diferentemente das funções do tipo paint_*, as funções do tipo
        draw_* adaptam automaticamente a renderização para os padrões de zoom e
        deslocamento da tela.'''
        
        if self._direct:
            self.paint_poly(poly.vertices, poly.color, poly.solid)
        else:
            raise NotImplementedError
        
class PyGameCanvas(Canvas):
    '''Implementa a interface Canvas utilizando a biblioteca pygame'''

    def init(self):
        import pygame
        self._screen = pygame.display.set_mode((self.width, self.height))
        self.pygame = pygame
        
    def flip(self):
        self.pygame.display.update()

    def _map_point(self, point):
        x, y = point
        X, Y = self.width, self.height
        return (trunc(x), trunc(Y - y))

    #===========================================================================
    # Desenho
    #===========================================================================
    def paint_circle(self, pos, radius, color='black', solid=True):
        pos = self._map_point(pos)
        color = Color(color)
        self.pygame.draw.circle(self._screen, color, pos, trunc(radius))

    def paint_poly(self, points, color='black', solid=True):
        points = [ self._map_point(pt) for pt in points ]
        color = Color(color)
        self.pygame.draw.polygon(self._screen, color.rgb, points)

    def paint_rect(self, pos, shape, color='black', solid=True):
        color = Color(color)
        x, y = self._map_point(pos)
        dx, dy = shape
        y -= dy/2
        x -= dx/2
        self.pygame.draw.rect(self._screen, color, (x, y, dx, dy))

    def paint_line(self, pt1, pt2, color='black', solid=True):
        raise NotImplementedError

    def clear_background(self, color=None):
        if color is None:
            if self.background is None:
                raise RuntimeError('background was not defined')
            self._screen.fill(self.background)
        else:
            self._screen.fill(Color(color))
        
class PyGameGFXCanvas(PyGameCanvas):
    '''Implementa a interface Canvas, utilizando a biblioteca Pygame e as 
    funções pygame.gfxdraw, ao invés das usuais pygame.draw'''

    def init(self):
        import pygame.gfxdraw
        self.gfx = pygame.gfxdraw
        super(PyGameGFXCanvas, self).init()

    def paint_circle(self, pos, radius, color='black', solid=True):
        x, y = self._map_point(pos)
        color = Color(color)
        self.gfx.aacircle(self._screen, x, y, trunc(radius), color)
        if solid:
            self.gfx.filled_circle(self._screen, x, y, trunc(radius), color)

    def draw_poly(self, points, color='black', solid=True):
        points = [ self._map_point(pt) for pt in points ]
        color = Color(color)
        self.pygame.gfxdraw.aapolygon(self._screen, points, color)
        if solid:
            self.pygame.gfxdraw.filled_polygon(self._screen, points, color)

class PyGameGLCanvas(PyGameCanvas):
    '''Implementa a interface Screen, utilizando a biblioteca Pygame'''

    def __init__(self, w, h, *args, **kwds):
        kwds['set_mode_args'] = [HWSURFACE|OPENGL|DOUBLEBUF]
        super(PyGameGLScreen, self).__init__(w, h, *args, **kwds)

    def show(self):
        pygame.display.flip()

    def draw_circle(self, pos, radius, color=(0, 0, 0), solid=True):
        x, y = self._map_point(pos)
        #pygame.gfxdraw.aacircle(self._screen, x, y, trunc(radius), color)
        #if solid:
        #    pygame.gfxdraw.filled_circle(self._screen, x, y, trunc(radius), color)

    def draw_poly(self, points, color=(0, 0, 0), solid=True):
        points = [ self._map_point(pt) for pt in points ]
        #pygame.gfxdraw.aapolygon(self._screen, points, color)
        #if solid:
        #    pygame.gfxdraw.filled_polygon(self._screen, points, color)

    def draw_rect(self, pos, shape, color=(0, 0, 0), solid=True):
        Screen.draw_rect(self, pos, shape, color, solid)

    def clear(self, color=None):
        R, G, B = color or self.background
        glClearColor(R/255., G/255., B/255., 0.0)
        
class SDL2Canvas(Canvas):
    '''Implementa a interface Screen, utilizando a biblioteca Pygame'''

    def init(self):
        import sdl2
        import sdl2.sdlgfx as gfx
        self._window = sdl2.SDL_CreateWindow(b"FGAme App",
                              SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              width, height, SDL_WINDOW_SHOWN)
        self._renderer = sdl2.SDL_CreateRenderer(self._window, -1,
                                            SDL_RENDERER_ACCELERATED |
                                            SDL_RENDERER_PRESENTVSYNC)
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
        SDL_RenderClear(self._renderer)
        if color is None:
            ret = boxColor(self._renderer, 0, self.height, self.width, 0, self._bg_color)
        else:
            R, G, B = color
            ret = boxRGBA(self._renderer, 0, self.height, self.width, 0, R, G, B, 255)

        if ret != 0:
            msg = SDL_GetError()
            raise RuntimeError('SDL error: %s' % msg)        
        
class PyGletCanvas(Canvas):
    '''Implementa a interface Screen, utilizando a biblioteca Pygame'''

    def __init__(self, width, height, **kwds):
        global WINDOW
        
        super(PyGletScreen, self).__init__(width, height, **kwds)
        self._window = pyglet.window.Window(width, height)
        WINDOW = self._window

    def show(self):
        self._window.flip()

    def _map_point(self, point):
        x, y = super(PyGletScreen, self)._map_point(point)
        X, Y = self.width, self.height
        x += 0.5 * X
        y = 0.5 * Y - y
        return (trunc(x), trunc(y))

    #===========================================================================
    # Desenho
    #===========================================================================
    def draw_circle(self, pos, radius, color=(0, 0, 0), solid=True):
        pos = self._map_point(pos)
        #pygame.draw.circle(self._screen, color, pos, trunc(radius))

    def draw_poly(self, points, color=(0, 0, 0), solid=True):
        points = [ self._map_point(pt) for pt in points ]
        #pygame.draw.polygon(self._screen, color, points)

    def draw_rect(self, pos, shape, color=(0, 0, 0), solid=True):
        x, y = self._map_point(pos)
        dx, dy = shape
        dx = trunc(dx * self.zoom)
        dy = trunc(dy * self.zoom)
        y -= dy
        #pygame.draw.rect(self._screen, color, (x, y, dx, dy))
        pyglet.graphics.draw(2, pyglet.gl.GL_POINTS,
                             ('v2i', (10, 15, 30, 35))
        )

    def draw_line(self, pt1, pt2, color=(0, 0, 0), solid=True):
        raise NotImplementedError

    def clear(self, color=None):
        #color = color or self.background
        #self._screen.fill(color)
        self._window.clear()
        R, G, B = self.background
        pyglet.gl.glClearColor(R / 255., G / 255., B / 255., 1)

        win = self._window
        verts = [ (win.width * 0.9, win.height * 0.9),
                  (win.width * 0.5, win.height * 0.1),
                  (win.width * 0.1, win.height * 0.9), ]
        colors = [ (255, 000, 000),
                   (000, 255, 000),
                   (000, 000, 255), ]
        glBegin(GL_TRIANGLES)
        for idx in range(len(verts)):
            glColor3ub(*colors[idx])
            glVertex2f(*verts[idx])
        glEnd()        
        

# Mapeia cada backend em sua respectiva classe ---------------------------------
SCREEN_MAP = dict(
    pygame=PyGameCanvas,
    pygamegfx=PyGameGFXCanvas,
)