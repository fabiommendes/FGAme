# -*- coding: utf8 -*-

from FGAme.mathutils import Vec2
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
    __slots__ = ['_direct', 'width', 'height', 'pos', 'zoom', '_background']

    def __init__(self, shape=(800, 600), pos=(0, 0), zoom=1, background=None):
        self.width, self.height = shape
        self.pos = Vec2(*pos)
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
    __slots__ = ['_drawing_funcs']

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
    def paint_pixel(self, pos, color='black'):
        '''Pinta um pixel na posição especificada na tela'''

        x, y = pos
        self.paint_rect((x, y, 1, 1), color)

    def paint_circle(self, radius, pos, color='black', solid=True):
        '''Pinta um círculo especificando a posição do centro, seu raio e
        opcionalmente a cor.

        Se a opção solid=True (padrão), desenha um círculo sólido. Caso
        contrário, desenha apenas uma linha'''

        raise NotImplementedError

    def paint_poly(self, L_points, color='black', solid=True):
        '''Pinta um polígono a partir de uma lista de vértices'''

        raise NotImplementedError

    def paint_aabb(self, xmin, xmax, ymin, ymax, color='black', solid=True):
        '''Pinta uma caixa de contorno alinhada aos eixos'''

        dx, dy = xmax - xmin, ymax - ymin
        self.paint_rect((xmin, ymin, dx, dy), color=color, solid=solid)

    def paint_rect(self, rect, color='black'):
        '''Semelhante à paint_aabb(), mas utiliza uma tupla com
        (xmin, ymin, width, height) como entrada e somente pinta cores
        sólidas'''

        x, y, w, h = rect
        self.paint_poly(
            [(x, y), (x + w, y), (x + w, y + h), (x, y + h)], color)

    def paint_line(self, pt1, pt2, color='black', solid=True):
        '''Pinta na tela uma linha que vai do ponto pt1 até o ponto pt2'''

        raise NotImplementedError

    def paint_image(self, pos, texture):
        '''Pinta uma textura/imagem na tela. O parâmetro pos especifica a
        posição do canto inferior esquerdo'''

    def clear_background(self, color=None):
        '''Limpa o fundo com a cor especificada'''

        raise NotImplementedError

    # Objetos derivados #######################################################

    def draw_tree(self, tree):
        '''Renderiza uma DrawingTree chamando a função correspondente para
        desenhar cada objeto'''

        for obj in tree.walk():
            try:
                obj.draw(self)
            except AttributeError:
                tt = type(obj).__name__
                raise ValueError("don't know how to draw %s object" % tt)

    def draw_circle(self, circle):
        '''Desenha um círculo utilizando as informações de geometria, cor e
        localização do objeto `circle` associado.

        Nota: diferentemente das funções do tipo paint_*, as funções do tipo
        draw_* adaptam automaticamente a renderização para os padrões de zoom e
        deslocamento da tela.'''

        self.paint_circle(circle.radius, circle.pos, circle.color, True)

    def draw_aabb(self, aabb):
        '''Desenha um círculo utilizando as informações de geometria, cor e
        localização do objeto `circle` associado.

        Nota: diferentemente das funções do tipo paint_*, as funções do tipo
        draw_* adaptam automaticamente a renderização para os padrões de zoom e
        deslocamento da tela.'''

        self.paint_rect(aabb.rect, aabb.color, True)

    def draw_poly(self, poly):
        '''Desenha um círculo utilizando as informações de geometria, cor e
        localização do objeto `circle` associado.

        Nota: diferentemente das funções do tipo paint_*, as funções do tipo
        draw_* adaptam automaticamente a renderização para os padrões de zoom e
        deslocamento da tela.'''

        self.paint_poly(poly.vertices, poly.color)

    def draw_image(self, image):
        if self._direct:
            pos = image.pos_sw
            self.paint_image(pos, image._data)
        else:
            raise NotImplementedError

    def draw(self, object):
        object.draw(self)