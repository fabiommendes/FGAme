# -*- coding: utf8 -*-
import contextlib
from FGAme.mathtools import pi, Vec2, Direction2, ux2D, uy2D
from FGAme.draw import Color
from FGAme.draw import base as draw

rad = pi / 180  # Conversão de graus para radianos
black = Color('black')


class RenderTree(object):

    '''Representa uma árvore de objetos que serão desenhados na tela

    Exemplos
    --------

    Inicializamos a árvore com alguns objetos. A string 'foo' foi colocado em
    uma camada superior e portanto será renderizada por último

    >>> tree = RenderTree()
    >>> tree.add('foo', 1)
    >>> tree.add('bar')
    >>> tree.add('blaz')

    Podemos navegar na árvore utilizando o iterador `walk()`

    >>> list(tree.walk())
    ['bar', 'blaz', 'foo']

    O método remove() permite remover objetos

    >>> tree.remove('bar');
    >>> 'bar' in tree, 'foo' in tree
    (False, True)
    '''

    is_tree = True
    visible = True

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def __init__(self, parent=None):
        self._data = []
        self.parent = None

    # Métodos mágicos #########################################################
    def __contains__(self, obj):
        return any(obj in L for _, L in self._data)

    def __iter__(self):
        return self.walk()

    def __len__(self):
        return sum(len(layer) for layer in self._data)

    def __getitem__(self, idx):
        for i, obj in enumerate(self):
            if i == idx:
                return obj
        raise IndexError(idx)

    # Controle de objetos #####################################################
    def add(self, obj, layer=0):
        '''Adiciona um objeto ou um galho (outro elemento de RenderTree) na
        camada especificada'''

        for i, (layer_idx, data) in enumerate(list(self._data)):
            if layer == layer_idx:
                data.append(obj)
                break
            elif layer < layer_idx:
                self._data.insert(i, (layer, [obj]))
                break
        else:
            self._data.append((layer, [obj]))

    def remove(self, value):
        '''Remove a primeira ocorrência de um valor.'''

        for _, L in self._data:
            if value in L:
                L.remove(value)
                break
        else:
            raise ValueError('object %r not in RenderTree' % value)

    def remove_all(self, value):
        '''Remove todas as ocorrências do valor dado.'''

        for _, L in self._data:
            while value in L:
                L.remove(value)

    def walk(self, reverse=False):
        '''Percorre sobre todos os objetos na ordem correta. Se reverse=True,
        percorre os objetos na ordem contrária.
        '''

        if reverse:
            for _, L in reversed(self._data):
                for obj in reversed(L):
                    yield obj
        else:
            for _, L in self._data:
                for obj in L:
                    yield obj

    def iter_layers(self, skip_empty=True):
        '''Itera sobre as camadas retornando a lista de objetos em cada
        camada'''

        if skip_empty:
            for (_, L) in self._data:
                yield L

        else:
            idx = self._data[0][0]
            for i, L in self._data:
                if i == idx:
                    idx += 1
                    yield L
                else:
                    while idx < i:
                        idx += 1
                        yield []

    def get_layer(self, idx):
        '''Retorna uma lista com os objetos da i-ésima camada'''

        for i, L in self._data:
            if i == idx:
                return L
        else:
            return []

    def update(self, dt):
        '''Percorre todos os objetos na árvore invocando o método update()'''

        for obj in self.walk():
            obj.update(dt)

    def draw(self, screen):
        '''Percorre todos os objetos na árvore invocando o método
        `obj.paint(screen)`'''

        for obj in self.walk():
            if obj.visible:
                try:
                    obj.draw(screen)
                except Exception:
                    print('debug: error drawing %s' % obj)
                    raise

    def linearize(self, layer=0):
        '''Retorna uma versão linearizada da árvore de renderização onde
        todos os objetos são recolocados na mesma camada'''

        data = (layer, list(self.walk()))
        new = RenderTree(parent=self.parent)
        new._data.append(data)
        return new


class Pen(RenderTree):

    '''Uma RenderTree que constroi objetos usando uma metáfora parecida com o
    módulo turtle do Python.

    Diferentemente do resto da FGAme, utiliza graus (e não radianos) como
    medida padrão para ângulos. Isto previne erros de arredondamento em
    rotações.

    Em 64 bits, 6 rotações de pi/6 (30 graus) não resultam em uma rotação
    completa de pi devido ao acúmulo de erros de arredondamento. Frações
    menores geralmente resultam em erros de arredondamento ainda maiores.
    Quando representamos esta rotação em graus, os erros de arredondamento só
    aparecem para rotações que representam uma fração de grau, sendo bem menos
    perceptíveis para o usuário.

    Em arquiteturas de 32 bits, o resultado é pior.


    Examples
    --------

    Uma caneta desenha traços na tela

    >>> pen = Pen()
    >>> for _ in range(4):
    ...     pen.fwd(100)
    ...     pen.left(90)
    >>> pen.commit()
    >>> pen[0]
    Path([(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0), (0.0, 0.0)])

    Podemos desenhar figuras geométricas usando gerenciadores de contexto

    >>> with pen.rect():
    ...    pen.left(45)
    ...    pen.fwd(50)

    #>>> pen[1]
    #AABB([0.0, 35.4, 0.0, 35.4])



    '''

    # Vetores em direções especiais
    _SPECIAL_DIRECTIONS = {
        0: ux2D, 90: uy2D, 180: -ux2D, 270: -uy2D,
        45: Direction2(1, 1),
        135: Direction2(-1, 1),
        225: Direction2(-1, -1),
        315: Direction2(1, -1),
    }

    def __init__(self, pos=(0, 0)):
        super(Pen, self).__init__()
        self._pos_prev = self._pos = Vec2(*pos)
        self._current = [self._pos]
        self._angle = 0
        self._angle_prev = 0
        self._dirty = False
        self._fill_color = black
        self._line_color = black
        self._line_width = 1.0
        self._pen_down = True
        self._can_move_pen_z = True
        self._can_move_pen_xy = True

    #
    # Propriedades da classe
    #
    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        if self._pen_down:
            self._pos, self._pos_prev = Vec2(*value), self._pos
            self._current.append(self._pos)
        else:
            self._pos = Vec2(*value)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        if self._dirty:
            self._angle, self._angle_prev = float(value), self._angle
            self._dirty = False
        else:
            self._angle = float(value)

    @property
    def theta(self):
        return self.angle * rad

    @theta.setter
    def theta(self, value):
        self.angle = value / rad

    #
    # Controle de movimento da caneta
    #
    def up(self):
        '''Levanta a caneta e para de desenhar'''

        if self._pen_down:
            self._assure_can_move_pen_z()
            self.commit()
            self._pen_down = False

    def down(self):
        '''Abaixa a caneta e desenha'''

        if not self._pen_down:
            self._assure_can_move_pen_z()
            self._current = [self.pos]
            self._pen_down = True

    def move(self, x_or_delta, y=None):
        '''Move o objeto pelo vetor de deslocamento dado'''

        if y is not None:
            return self.move(Vec2(x_or_delta, y))

        self._assure_can_move_pen_xy()
        self.pos += x_or_delta

    def goto(self, x_or_delta, y=None):
        '''Vai até a posição especificada na tela'''

        if y is not None:
            return self.goto(Vec2(x_or_delta, y))

        self.move(x_or_delta - self._pos)

    def left(self, angle=90):
        '''Rota à esquerda pelo ângulo especificado em graus'''

        self.angle += angle

    def right(self, angle=90):
        '''Rota à direita pelo ângulo especificado em graus'''

        self.left(-angle)

    def forward(self, length):
        '''Move para frente pelo comprimento especificado em pixels'''

        self.move(self.direction() * length)

    def fwd(self, length):
        '''Atalho para `obj.forward(length)`'''

        self.forward(length)

    def backwards(self, length):
        '''Move para trás pelo comprimento especificado em pixels'''

        self.forward(-length)

    def back(self, length):
        '''Atalho para `obj.backwards(length)`'''

        self.backwards(length)

    def direction(self):
        '''Retorna um vetor unitário na direção especificada'''

        # Casos especiais, para obter direções precisas
        try:
            return self._SPECIAL_DIRECTIONS[self._angle % 360]
        except KeyError:
            return ux2D.rotate(self.theta)

    #
    # Controle de transações
    #
    def commit(self):
        '''Insere linha que estava sendo desenha na árvore'''

        if len(self._current) > 1:
            self.add(
                draw.Path(self._current, width=self._line_width,
                          color=self._fill_color))
        self.clear()

    def clear(self):
        '''Remove última linha que estava sendo desenhada'''

        self._current = [self._pos]

    #
    # Context managers
    #
    @contextlib.contextmanager
    def lock_pen_z(self):
        '''Tranca o movimento da caneta no eixo z'''

        # Set up
        can_move = self._can_move_pen_z
        self._can_move_pen_z = False

        # Enter
        yield

        # Clean
        self._can_move_pen_z = can_move

    @contextlib.contextmanager
    def lock_pen_xy(self):
        '''Tranca o movimento da caneta no plano'''

        # Set up
        can_move = self._can_move_pen_xy
        self._can_move_pen_xy = False

        # Enter
        yield

        # Clean
        self._can_move_pen_xy = can_move

    @contextlib.contextmanager
    def rect(self, line_color=None, **kwds):
        '''Gerenciador de contexto que inicia o desenho de uma AABB cujos
        limites se encontram no ponto inicial e no ponto final do caminho.'''

        # TODO: fatorar para mover implementação comum a outras figuras
        # geométricas para o mesmo método.

        # Set up
        start = self.pos
        self.commit()
        self.down()
        if line_color is None:
            line_color = self._line_color

        # Enter
        with self.lock_pen_z():
            yield

        # Clean
        end = self.pos
        self.clear()
        limits = sorted([v.x for v in [start, end]])
        limits.extend(sorted([v.y for v in [start, end]]))
        self.add(draw.AABB(*limits, line_color=line_color, **kwds))

    def circle(self, **kwds):
        '''Gerenciador de contexto que inicia o desenho de um círculo cujo
        centro está no ponto inicial e o raio vai até o ponto final'''

        raise NotImplementedError

    def aabb(self, **kwds):
        '''Gerenciador de contexto que inicia o desenho de uma AABB que
        envolve todos os pontos da trajetória realizada.'''

    def cbb(self, **kwds):
        '''Gerenciador de contexto que desenha o menor círculo que envolve
        todos os pontos da trajetória realizada'''

        raise NotImplementedError

    def poly(self, **kwds):
        '''Gerenciador de contexto que inicia o desenho de um polígono
        fechado'''

        raise NotImplementedError

    #
    # Utility private methods
    #
    def _assure_can_move_pen_z(self):
        if not self._can_move_pen_z:
            raise RuntimeError('pen is locked to vertical movement')

    def _assure_can_move_pen_xy(self):
        if not self._can_move_pen_xy:
            raise RuntimeError('pen is locked to horizontal movement')

    def _solid_kwds(self, kwds=None):
        kwds = kwds or {}
        solid = kwds.setdefault('solid', self._fill_color is not None)
        if solid:
            kwds.setdefault('color', self._fill_color)
        kwds.setdefault('line_width', self._line_width)
        kwds.setdefault('line_color', self._line_color)
        return kwds

    def _curve_kwds(self, kwds=None):
        kwds = kwds or {}
        kwds.setdefault('width', self._line_width)
        kwds.setdefault('color', self._line_color)
        return kwds

    def _add_first(self, obj):
        '''Adiciona obj e retorna seu valor'''

        self.add(obj)
        return obj

    #
    # Adiciona objetos
    #
    def _add_solid(self, constructor, args, kwds):
        '''Worker para as funções do tipo add_*solid*()'''

        kwds.setdefault('pos', self.pos)
        kwds = self._solid_kwds(kwds)
        return self._add_first(constructor(*args, **kwds))

    def add_aabb(self, *args, **kwds):
        '''Adiciona um círculo ao desenho'''

        return self._add_solid(draw.AABB, args, kwds)

    def add_circle(self, radius, pos=None, **kwds):
        '''Adiciona um círculo ao desenho'''

        kwds = self._solid_kwds(kwds)
        return self._add_first(draw.Circle(radius, pos or self.pos, **kwds))

    def add_poly(self, vertices, pos=None, **kwds):
        '''Adiciona um polígono ao desenho'''

        return self._add_first(draw.Poly(vertices, pos or self.pos, **kwds))

    def add_rectangle(self, *args, **kwds):
        '''Adiciona um retângulo ao desenho'''

        return self._add_solid(draw.Rectangle, args, kwds)

    def add_triangle(self, *args, **kwds):
        '''Adiciona um triângulo ao desenho'''

        return self._add_solid(draw.Triangle, args, kwds)

    def add_segment(self, p1, p2=None, **kwds):
        '''Adiciona um segmento de reta ao desenho.

        Se somente um ponto for fornecido, utiliza a posição inicial como
        ponto inicial e o ponto dado como posição final.'''

        if p2 is None:
            p1, p2 = self.pos, p1
        self._add(draw.Segment(p1, p2, **kwds))

    def add_ray(self, arg1, direction=None, **kwds):
        '''Adiciona um raio (reta semi-finita) ao desenho.

        Pode ser chamada como `pen.add_ray(direction)` para iniciar um raio a
        partir do ponto inicial ou `pen.add_ray(point, direction) para
        especificar tanto o ponto inicial como a direção. '''

        if direction is None:
            p0, direction = self.pos, arg1
        else:
            p0 = arg1
        self._add(draw.Ray(p0, direction, **kwds))

    def add_line(self, arg1, direction=None, **kwds):
        '''Adiciona uma reta infinita ao desenho. A assinatura é igual à
        função `pen.add_ray()`'''

        if direction is None:
            p0, direction = self.pos, arg1
        else:
            p0 = arg1
        return self._add(draw.Line(p0, direction, **kwds))

    def add_path(self, *points, **kwds):
        '''Desenha uma linha seguindo a sequencia de pontos partindo do ponto
        atual.

        Pode ser chamada com um único argumento posicional que representa uma
        sequência de pontos ou por vários argumentos que representam pontos
        individuais. Se o primeiro argumento for None ou uma Elipisis (...),
        adiciona o ponto atual ao começo da lista.
        '''

        # Checa entradas
        if not points:
            raise ValueError('must pass at least 2 points')
        elif len(points) == 1:
            return self.add_path(*points[0], **kwds)

        if points[0] is None or points[0] is Ellipsis:
            points = list(points)
            points[0] = self.pos
        return self._add(draw.Path(points, **kwds))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
