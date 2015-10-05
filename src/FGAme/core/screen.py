# -*- coding: utf8 -*-
from contextlib import contextmanager
from FGAme.mathtools import Vec2, shapes
from FGAme.draw import color_property, Color

black = Color('black')
white = Color('white')


###############################################################################
#                          Classe Screen genérica
###############################################################################
# TODO: refatorar para ter uma classe de Canvas separada da classe Window?
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
    __instance = None
    is_canvas = False
    background = color_property('background')

    def __new__(cls, *args, **kwds):
        if cls.__instance is not None:
            raise TypeError('cannot create two instances of singleton object')
        return object.__new__(cls)

    def __init__(self, shape=(800, 600), pos=(0, 0), zoom=1, background=None):
        self.width, self.height = shape
        self.pos = Vec2(*pos)
        self.zoom = zoom
        self.background = background
        self._direct = True
        self.visible = False

    def init(self):
        '''Deve ser chamado como primeira função para iniciar explicitamente a
        tela e para abrir e mostrar a janela de jogo.'''

        pass

    def show(self):
        '''Deve ser chamado como primeira função para iniciar explicitamente a
        tela e para abrir e mostrar a janela de jogo.'''

        self.visible = True

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

    def show(self):
        if not self.visible:
            super(Canvas, self).show()
            self.clear_background('white')
            self.flip()

    def flip(self):
        '''Transmite o buffer de pintura para a tela do computador'''

        raise NotImplementedError

    # Context managers ########################################################
    @contextmanager
    def autoflip(self):
        '''Ao sair do bloco `with`, executa automaticamente o método flip()'''

        try:
            yield None
        finally:
            self.flip()

    @contextmanager
    def painting(self):
        '''Semelhante ao método `autoflip()`, mas limpa a tela antes de fazer
        os desenhos.

        Deste modo, somente as imagens referentes aos comandos dentro do bloco
        serão exibidas.'''

        self.clear_background(self.background or Color('white'))
        try:
            yield None
        finally:
            self.flip()

    # Objetos primitivos ######################################################
    # Estas funções desenham objetos primitivos na tela sem se atentar para
    # transformações de escala, translação e rotação. São as operações
    # primitivas que devem ser sobrescritas por cada backend suportado.
    # A maior parte das implementações padrão é vazia

    # Entes primitivos
    def draw_raw_pixel(self, pos, color=black):
        '''Desenha um pixel na posição dada'''
        raise NotImplementedError

    def draw_raw_segment(self, segment, width=1.0, color=black):
        '''Desenha um segmento de reta'''
        raise NotImplementedError

    def draw_raw_line(self, line, width=1.0, color=black):
        '''Desenha uma linha infinita'''
        # TODO: implementar a partir de raw_segment()
        raise NotImplementedError

    def draw_raw_ray(self, line, width=1.0, color=black):
        '''Desenha um raio (ou linha semi-infinita)'''
        # TODO: implementar a partir de raw_segment()
        raise NotImplementedError

    # Figuras sólidas
    def draw_raw_circle_solid(self, circle, color=black):
        '''Desenha um círculo sólido na tela'''
        raise NotImplementedError

    def draw_raw_circle_border(self, circle, width=1.0, color=black):
        '''Desenha a borda de um círculo'''
        raise NotImplementedError

    def draw_raw_aabb_solid(self, aabb, color=black):
        '''Desenha uma aabb sólida'''
        raise NotImplementedError

    def draw_raw_aabb_border(self, aabb, width=1.0, color=black):
        '''Desenha a borda de uma aabb'''
        raise NotImplementedError

    def draw_raw_poly_solid(self, poly, color=black):
        '''Desenha um polígono sólido'''
        raise NotImplementedError

    def draw_raw_poly_border(self, poly, width=1.0, color=black):
        '''Desenha a borda de um polígono'''
        # TODO: implementar a partir de raw_segment()
        raise NotImplementedError

    def draw_raw_texture(self, texture, start_pos=(0, 0)):
        '''Desenha uma textura na tela'''
        raise NotImplementedError

    def draw_raw_image(self, image):
        '''Desenha uma imagem na tela'''

        self.draw_raw_texture(image.texture, image.pos_sw)

    def clear_background(self, color):
        '''Limpa o fundo com a cor especificada'''

        raise NotImplementedError

    # Objetos derivados #######################################################
    # Estas são as funções que devem ser utilizadas diretamente pelos usuários
    # da FGAme. Elas desenham um objeto a partir de uma figura primitiva e
    # aplicam automaticamente as transformações de escala, translação e rotação
    # necessárias.
    def draw_circle(self, circle, solid=None, color=None,
                    line_width=None, line_color=None):
        '''Desenha um círculo na tela.'''

        if not self._direct:
            raise RuntimeError

        if solid:
            self.draw_raw_circle_solid(circle, color)
        if line_color is not None and line_width:
            self.draw_raw_circle_border(circle, line_width, line_color)

    def draw_aabb(self, aabb, solid=True, color=black,
                  line_width=0.0, line_color=black):
        '''Desenha uma AABB na tela.'''

        if not self._direct:
            raise RuntimeError
        
        if solid:
            self.draw_raw_aabb_solid(aabb, color)
        if line_color is not None and line_width:
            self.draw_raw_aabb_border(aabb, line_width, line_color)

    def draw_poly(self, poly, solid=True, color=black,
                  line_width=0.0, line_color=black):
        '''Desenha um polígono na tela.'''

        if not self._direct:
            raise RuntimeError

        if solid:
            self.draw_raw_poly_solid(poly, color)
        if line_color is not None and line_width:
            self.draw_raw_poly_border(poly, line_width, line_color)

    def draw_segment(self, segment, width=0.0, color=black):
        '''Desenha um segmento de reta.'''

        if not self._direct:
            raise RuntimeError

        self.draw_raw_segment(segment, width, color)

    def draw_ray(self, ray, width=0.0, color=black):
        '''Desenha um raio (reta semi-finita)'''

        raise NotImplementedError

    def draw_line(self, ray, width=0.0, color=black):
        '''Desenha uma reta infinita'''

        raise NotImplementedError

    def draw_path(self, path, width=0.0, color=black):
        '''Desenha um caminho formado por vários pontos.'''

        if not self._direct:
            raise RuntimeError

        points = iter(path)
        pt0 = next(points)
        for pt1 in points:
            self.draw_raw_segment(shapes.Segment(pt0, pt1), width, color)
            pt0 = pt1

    def draw_image(self, image):
        if self._direct:
            self.draw_raw_image(image)
        else:
            raise NotImplementedError

    # Interface de objetos do tipo Drawable. Objetos podem sinalizar que são
    # desenhaveis quando implementam o método obj.draw(canvas). O método draw
    # é chamado com um objeto do tipo Canvas como atributo e deve se desenhar
    # a partir de chamadas às funções primitivas de desenho.
    def draw(self, object):
        '''Desenha objetos do tipo Drawable.

        Objetos do tipo Drawable possuem uma função obj.draw(screen) que
        desenha o objeto na tela fornecida como parâmetro de entrada.
        '''
        object.draw(self)
