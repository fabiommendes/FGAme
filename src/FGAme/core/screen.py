# -*- coding: utf8 -*-

from FGAme.mathutils import Vector
from FGAme.draw import color_property

###############################################################################
#                          Classe Screen genérica
###############################################################################


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

    def init(self):
        '''Deve ser chamado como primeira função para iniciar explicitamente a
        tela e para abrir e mostrar a janela de jogo.'''

        pass

    def show(self):
        '''Deve ser chamado como primeira função para iniciar explicitamente a
        tela e para abrir e mostrar a janela de jogo.'''

    @property
    def shape(self):
        return self.width, self.height


###############################################################################
#     Classe Canvas: backends baseados em renderização do tipo "pintura"
###############################################################################


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

    def init(self):
        pass

    def show(self):
        self.clear_background('white')
        self.flip()

    def flip(self):
        '''Transmite o buffer de pintura para a tela do computador'''

        raise NotImplementedError

    # Context managers ########################################################

    def __enter__(self):
        if self.background is not None:
            self.clear_background(self.background)

    def __exit__(self, *args):
        self.flip()

    # Objetos primitivos ######################################################

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

    def paint_rect(self, rect, color='black', solid=True):
        x, y, w, h = rect
        self.paint_poly(
            [(x, y), (x + w, y), (x + w, y + h), (x, y + h)], color, solid)

    def paint_line(self, pt1, pt2, color='black', solid=True):
        raise NotImplementedError

    def clear_background(self, color=None):
        raise NotImplementedError

    # Objetos derivados #######################################################

    def draw_tree(self, tree):
        '''Renderiza uma DrawingTree chamando a função correspondente para
        desenhar cada objeto'''

        for obj in tree.walk():
            try:
                method = 'draw_' + obj.canvas_primitive
                func = getattr(self, method)
            except AttributeError:
                tt = type(obj).__name__
                raise ValueError("don't know how to draw %s" % tt)
            else:
                func(obj)

    def draw_circle(self, circle):
        '''Desenha um círculo utilizando as informações de geometria, cor e
        localização do objeto `circle` associado.

        Nota: diferentemente das funções do tipo paint_*, as funções do tipo
        draw_* adaptam automaticamente a renderização para os padrões de zoom e
        deslocamento da tela.'''

        if self._direct:
            self.paint_circle(circle.pos, circle.radius,
                              circle.color, True)
        else:
            raise NotImplementedError

    def draw_aabb(self, aabb):
        '''Desenha um círculo utilizando as informações de geometria, cor e
        localização do objeto `circle` associado.

        Nota: diferentemente das funções do tipo paint_*, as funções do tipo
        draw_* adaptam automaticamente a renderização para os padrões de zoom e
        deslocamento da tela.'''

        if self._direct:
            self.paint_rect(aabb.rect, aabb.color, True)
        else:
            raise NotImplementedError

    def draw_poly(self, poly):
        '''Desenha um círculo utilizando as informações de geometria, cor e
        localização do objeto `circle` associado.

        Nota: diferentemente das funções do tipo paint_*, as funções do tipo
        draw_* adaptam automaticamente a renderização para os padrões de zoom e
        deslocamento da tela.'''

        if self._direct:
            self.paint_poly(poly.vertices, poly.color)
        else:
            raise NotImplementedError
