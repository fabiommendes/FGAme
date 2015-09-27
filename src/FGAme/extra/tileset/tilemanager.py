import FGAme
from FGAme.mathtools import asvector


class TileManager(object):

    '''Configura um tileset que permite dispor objetos no mundo'''

    def __init__(self, shape=(50, 50), origin=(0, 0)):
        self.shape = asvector(shape)
        self.origin = asvector(origin)
        self.tiles = []
        self.specs = {}
        self.charspecs = {}

    def register_spec(self, name, char, tile=None, **kwds):
        '''
        Registra uma especificação de ladrilho associando a um determinado
        nome e caractere. Por padrão, o ladrilho é uma AABB preta do formado
        especificado pelo atributo shape.

        A função aceita vários argumentos adicionais que determinam as
        propriedades do ladrilho.


        Parameters
        ----------

        tile :
            Se especificado, corresponde ao ladrilho que será replicado a cada
            comando :meth:`add_tile` ou :meth:`add_tileset`.
        mode : 'aabb', 'circle'


        Todos os argumentos opcionais da classe :cls:`FGAme.objects.Object`
        são aceitos.
        '''

        if tile is None:
            tile = self._make_tile(name, **kwds)
        self.specs[name] = tile
        if char is not None:
            self.charspecs[char] = tile

    def _make_tile(self, name, mode='aabb', **kwds):
        '''Cria ladrinho para o método register_spec'''

        modes = {
            'aabb': {
                'cls': FGAme.AABB,
                'shape': self.shape,
            },
            'circle': {
                'cls': FGAme.Circle,
                'radius': min(self.shape) / 2,
            },
            'poly': {
                'cls': FGAme.Poly,
            },

        }

        # Obtem argumentos e classe de inicialização a partir do modo
        mode = modes[mode.lower()]
        cls = mode.pop('cls')
        kwds.update(mode)

        # Configura argumentos padrão para todos os objetos
        kwds.setdefault('mass', 'inf')

        # Inicializa e reposiciona
        tile = cls(**kwds)
        tile.name = name
        tile.move(self.origin - tile.pos_se)

        return tile

    def add_tile(self, pos, tile):
        '''Adiciona o ladrilho especificado na posição dada.

        O ladrilho pode ser um objeto arbitrário que pode ser adicionado a um
        mundo ou pode ser especificado pelo nome ou caractere de identificação.

        A posição (i, j) corresponde ao valor (normalmente) inteiro da posição
        medida em número de ladrilhos deslocados nas coordenadas x e y
        respectivamente. Deste modo, um valor fracionário como (10, 0.5)
        significa deslocar 10 ladrilhos para a direita e meio ladrilho para
        cima a partir da origem definida em `self.origin`.
        '''

        i, j = pos
        dx, dy = self.shape
        x0, y0 = self.origin

        if isinstance(tile, str):
            name = tile
            try:
                if len(name) == 1:
                    tile = self.charspecs[name]
                else:
                    tile = self.specs[name]
            except KeyError:
                raise ValueError('%r is not a valid tile name' % name)

        tile = tile.copy()
        tile.move(x0 + i * dx, y0 + j * dy)
        self.tiles.append(tile)

    def add_tileset(self, data):
        '''Adiciona um tileset completo a partir da string de especificação.

        Um exemplo de string ``data`` é dado abaixo::
            |             **
            |        **     xxxxxxxxxx
            |           xxx
            | ##    xxx
            | H#                         ^^
            |xxxxxxxxxxxxxxxxxxxx    xxxxxxxxxxx
            |xxxxxxxxxxxxxxxxxxxx^^^^xxxxxxxxxxx

        Cada linha deve começar com o caracter "|". A partir daí a posição de
        cada ladrilho é calculada para corresponder à mesma posíção na string.
        Os ladrilhos são então inseridos por caractere de identificação (o
        espaço em branco significa a ausência de ladrilho).

        Neste caso, temos o chão quase inteiramente formado por ladrilhos do
        tipo "x" e um ladrilho do tipo "H" na posição (1, 2). Os outros
        ladrilhos estão dispostos de maneira análoga.

        O usuário pode utilizar qualquer caractere unicode à exceção de espaço,
        tab, newline e hashtag para identificar um ladrilho. Espaços em branco
        são interpretados como a ausência de ladrilhos e as linhas representam
        cada camada do ladrilhamento. O hashtag ("#") é ignorado da mesma forma
        que o espaço. Normalmente é utilizado para sinalizar que a posição está
        tomada por algum ladrilho vizinho. No caso, o ladrilho H pode ocupar um
        tamanho de 2x2, apesar de estar posicionado somente em uma casa
        específica.

        Cada ladrilho deve ter sido criado previamente pela função
        :meth:`register_spec`. Caso o usuário utilize um caractere inválido,
        isto corresponderá a um erro.
        '''

        y = data.count('|') - 1
        for line in data.splitlines():
            line = line.lstrip()
            if line.startswith('|'):
                line = line[1:]
            else:
                continue

            for x, char in enumerate(line):
                if char not in ' #':
                    self.add_tile((x, y), char)
            y -= 1

    def update_world(self, world, layer=0):
        '''Usado por World.add() para adicionar o tileset'''

        for tile in self.tiles:
            if tile.is_rogue():
                world.add(tile.copy(), layer)
            else:
                raise RuntimeError('tile already present in world')

    def __iter__(self):
        return iter(self.tiles)

    def __len__(self):
        return len(self.tiles)

if __name__ == '__main__':
    from FGAme import World, AABB

    ts = '''
    |            oo
    |        oo     xxxxxxxxxxxxxxxxxx
    |           xxx
    |       xxx
    |                                        ii
    |xxxxxxxxxxxxxxxxxxxxxxxxxxxxx    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    |xxxxxxxxxxxxxxxxxxxxxxxxxxxxxiiiixxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    '''

    w = World()
    tm = TileManager((30, 30))
    tm.register_spec('brick', 'x', color='red')
    tm.register_spec('coin', 'o', mode='circle', color='yellow')
    tm.register_spec('spike', 'i', color='black')
    tm.add_tileset(ts)

    w.add(tm)
    w.run()
