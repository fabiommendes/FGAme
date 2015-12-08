from contextlib import contextmanager
from FGAme.mathtools import Vec2, asvector, shapes
from FGAme.draw import colorproperty, Color
from FGAme import util


__all__ = ['Screen', 'Canvas', 'camera']
black = Color('black')
white = Color('white')


# TODO: refatorar para ter uma classe de Canvas separada da classe Window?
class Screen(object):

    """Classe que define a funcionalidade básica de todos os backends que
    gerenciam a disponibilização de imagens na tela do computador.

    Existem dois modelos de renderização disponíveis

        * O modelo Canvas (ou tela) utiliza a metáfora de pintura, onde os
          pixels da tela são "pintados" a cada frame de renderização.

        * O modelo LiveTree delega a pintura para um backend mais básico que
          determina o instante preciso do frame de renderização e quais partes
          da tela devem ser re-escritas com base numa árvore que guarda e
          atualiza as funções de renderização.
    """
    __instance = None
    is_canvas = False
    background = colorproperty('background')

    def __new__(cls, *args, **kwds):
        if cls.__instance is not None:
            raise TypeError('cannot create two instances of singleton object')
        return object.__new__(cls)

    def __init__(self, shape=(800, 600), pos=(0, 0), zoom=1, background=None):
        self.width, self.height = shape
        self.pos = Vec2(*pos)
        self.zoom = zoom
        self.background = background
        self.visible = False

    def init(self):
        """Deve ser chamado como primeira função para iniciar explicitamente a
        tela e para abrir e mostrar a janela de jogo."""

        pass

    def show(self):
        """Deve ser chamado como primeira função para iniciar explicitamente a
        tela e para abrir e mostrar a janela de jogo."""

        self.visible = True

    @property
    def shape(self):
        return self.width, self.height


class Camera:
    """Represents a camera."""

    def __init__(self, canvas, displacement=(0, 0), scale=1, rotation=0):
        if scale != 1 or rotation != 0:
            raise ValueError('rotations and rescaling are not supported')

        self.displacement = asvector(displacement)
        self.canvas = canvas
        self._passthru = True

    def pan(self, delta_or_x, y=None):
        """Pan camera by the given displacement"""

        if y is None:
            delta = delta_or_x
        else:
            delta = Vec2(delta_or_x, y)
        self.displacement -= delta
        self._passthru = self.displacement == (0, 0)

    def panleft(self, px):
        """Pan camera to the left by the given amount (in pixels)."""

        self.pan(-px, 0)

    def panright(self, px):
        """Pan camera to the right by the given amount (in pixels)."""

        self.pan(px, 0)

    def panup(self, px):
        """Pan camera upwards by the given amount (in pixels)."""

        self.pan(0, px)

    def pandown(self, px):
        """Pan camera downards right by the given amount (in pixels)."""

        self.pan(0, -px)

    @property
    def shape(self):
        return self.width, self.height

    @property
    def width(self):
        return self.canvas.width

    @property
    def height(self):
        return self.canvas.height

    @property
    def xmin(self):
        return -self.displacement.x

    @property
    def xmax(self):
        return -self.displacement.x + self.width


    #
    # Drawing functions
    #
    def draw_circle(self, circle, fillcolor=None, linecolor=None, linewidth=1):
        """Desenha um círculo na tela."""

        if not self._passthru:
            circle = circle.displaced(self.displacement)

        if fillcolor is not None:
            self.canvas.draw_raw_circle_solid(circle, fillcolor)
        if linecolor is not None and linewidth:
            self.canvas.draw_raw_circle_border(circle, linewidth, linecolor)

    def draw_aabb(self, aabb, fillcolor=None, linecolor=None, linewidth=1):
        """Desenha uma AABB na tela."""

        if not self._passthru:
            aabb = aabb.displaced(self.displacement)

        if fillcolor is not None:
            self.canvas.draw_raw_aabb_solid(aabb, fillcolor)
        if linecolor is not None and linewidth:
            self.canvas.draw_raw_aabb_border(aabb, linewidth, linecolor)

    def draw_poly(self, poly, fillcolor=None, linecolor=None, linewidth=1):
        """Desenha um polígono na tela."""

        if not self._passthru:
            poly = poly.displaced(self.displacement)

        if fillcolor is not None:
            self.canvas.draw_raw_poly_solid(poly, fillcolor)
        if linecolor is not None and linewidth:
            self.canvas.draw_raw_poly_border(poly, linewidth, linecolor)

    def draw_segment(self, segment, linecolor=black, linewidth=1):
        """Desenha um segmento de reta."""

        if not self._passthru:
            segment = segment.displaced(self.displacement)

        if linecolor is not None and linewidth:
            self.canvas.draw_raw_segment(segment, linewidth, linecolor)

    def draw_ray(self, ray, linecolor=black, linewidth=1):
        """Desenha um raio (reta semi-finita)"""

        raise NotImplementedError

    def draw_line(self, line, linecolor=black, linewidth=1):
        """Desenha uma reta infinita"""

        raise NotImplementedError

    def draw_path(self, path, linecolor=black, linewidth=1):
        """Desenha um caminho formado por vários pontos."""

        if not self._passthru:
            path = path.displaced(self.displacement)

        points = iter(path)
        pt0 = next(points)
        for pt1 in points:
            self.canvas.draw_raw_segment(shapes.Segment(pt0, pt1), linewidth,
                                         linecolor)
            pt0 = pt1

    def draw_image(self, image):
        """Desenha uma imagem/animação/sprite na tela"""

        if not self._passthru:
            image = image.displaced(self.displacement)
        self.canvas.draw_raw_image(image)

    # Interface de objetos do tipo Drawable. Objetos podem sinalizar que são
    # desenhaveis quando implementam o método obj.draw(canvas). O método draw
    # é chamado com um objeto do tipo Canvas como atributo e deve se desenhar
    # a partir de chamadas às funções primitivas de desenho.
    def draw(self, obj):
        """Desenha objetos do tipo Drawable.

        Objetos do tipo Drawable possuem uma função obj.draw(screen) que
        desenha o objeto na tela fornecida como parâmetro de entrada.
        """
        obj.draw(self)


#
# Canvas: backends baseados em renderização do tipo "pintura"
#
class Canvas(Screen):

    """Sub-classes implementam a metáfora de "pintura" para a renderização das
    imagens.

    As sub-implementações devem saber como renderizar objetos geométricos
    básicos como círculos, linhas, pontos, polígonos, etc.
    """
    is_canvas = True

    def __init__(self, shape=(800, 600), pos=(0, 0), zoom=1, background=None):
        super(Canvas, self).__init__(shape, pos, zoom, background)
        self._drawing_funcs = {}
        self.camera = Camera(self)

    def show(self):
        if not self.visible:
            super(Canvas, self).show()
            self.clear_background('white')
            self.flip()

    def flip(self):
        """Transmite o buffer de pintura para a tela do computador"""

        raise NotImplementedError

    @contextmanager
    def autoflip(self):
        """Ao sair do bloco `with`, executa automaticamente o método flip()"""

        try:
            yield None
        finally:
            self.flip()

    @contextmanager
    def painting(self):
        """Semelhante ao método `autoflip()`, mas limpa a tela antes de fazer
        os desenhos.

        Deste modo, somente as imagens referentes aos comandos dentro do bloco
        serão exibidas."""

        self.clear_background(self.background or Color('white'))
        try:
            yield None
        finally:
            self.flip()

    #
    # Objetos primitivos
    # ------------------
    #
    # Estas funções desenham objetos primitivos na tela sem se atentar para
    # transformações de escala, translação e rotação. As operações
    # primitivas devem ser sobrescritas por cada backend suportado.
    # A maior parte das implementações padrão é vazia
    #
    
    # Entes primitivos
    def draw_raw_pixel(self, pos, color=black):
        """Desenha um pixel na posição dada"""
        raise NotImplementedError

    def draw_raw_segment(self, segment, width=1.0, color=black):
        """Desenha um segmento de reta"""
        raise NotImplementedError

    def draw_raw_line(self, line, width=1.0, color=black):
        """Desenha uma linha infinita"""
        # TODO: implementar a partir de raw_segment()
        raise NotImplementedError

    def draw_raw_ray(self, line, width=1.0, color=black):
        """Desenha um raio (ou linha semi-infinita)"""
        # TODO: implementar a partir de raw_segment()
        raise NotImplementedError

    # Figuras sólidas
    def draw_raw_circle_solid(self, circle, color=black):
        """Desenha um círculo sólido na tela"""
        raise NotImplementedError

    def draw_raw_circle_border(self, circle, width=1.0, color=black):
        """Desenha a borda de um círculo"""
        raise NotImplementedError

    def draw_raw_aabb_solid(self, aabb, color=black):
        """Desenha uma aabb sólida"""
        raise NotImplementedError

    def draw_raw_aabb_border(self, aabb, width=1.0, color=black):
        """Desenha a borda de uma aabb"""

        poly = shapes.Poly(aabb.vertices)
        self.draw_raw_poly_border(poly, width=width, color=color)

    def draw_raw_poly_solid(self, poly, color=black):
        """Desenha um polígono sólido"""
        raise NotImplementedError

    def draw_raw_poly_border(self, poly, width=1.0, color=black):
        """Desenha a borda de um polígono"""
        # TODO: implementar a partir de raw_segment()
        raise NotImplementedError

    def draw_raw_texture(self, texture, start_pos=(0, 0)):
        """Desenha uma textura na tela"""
        raise NotImplementedError

    def draw_raw_image(self, image):
        """Desenha uma imagem na tela"""

        self.draw_raw_texture(image.texture, image.pos_sw)

    def clear_background(self, color):
        """Limpa o fundo com a cor especificada"""

        raise NotImplementedError


@util.caching_proxy_factory
def camera():
    """Global camera object."""

    from FGAme import conf
    return conf.get_screen().camera
