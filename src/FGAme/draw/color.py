# -*-coding: utf8 -*-
import random
from math import sqrt, acos


class Color(object):

    '''
    Objeto básico que representa uma cor.

    O construtor de Color() aceita várias assinaturas de entrada, que
    representam maneiras diferentes de construir uma cor. A maneira mais
    simples e direta consiste em especificar as componentes RGB ou RGBA.

    >>> w1 = Color(255, 255, 255)
    >>> w2 = Color(255, 255, 255, 255)
    >>> w1 == w2
    True

    Além disto, podemos especificar a cor pelo nome.

    >>> Color('white')
    Color(255, 255, 255, 255)

    Todos os nomes do padrão CSS3.0 são aceitos. A lista completa de cores
    pode ser acessada em http://www.w3.org/TR/css3-color/#svg-color.

    Também é possível especificar a cor pelo código hexadecimal. Isto pode ser
    feito através de uma string ou utilizando a sintaxe do Python para gerar
    inteiros a partir da representação hexadecimal.

    >>> red = Color('#F00')
    >>> lime = Color('#00FF00')
    >>> blue = Color(0x0000ff, alpha=128)

    Nos dois primeiros casos o canal alpha é opcional e pode ser embutido na
    string com o código hex. No segundo caso, é necessário passar o canal alpha
    como argumento opcional. O valor padrão é 255, que corresponde a uma cor
    sólida.

    Note que apesar de RGB significar *Red* (vermelho), *Green* (verde), *Blue*
    (azul), o nome web para a cor com o canal verde puro é *Lime*. A cor
    "green" corresponde ao código hex #008000. A FGAme utiliza a mesma
    convenção.


    Examples
    --------

    Os objetos do tipo Color são imutáveis e se comportam como uma tupla.

    >>> list(w1)
    [255, 255, 255, 255]
    >>> w1
    Color(255, 255, 255, 255)

    Podemos acessar a cor em várias representações diferentes utilizando os
    atributos adequados.

    >>> w1.rgb
    (255, 255, 255)

    >>> w1.f_rgb
    (1.0, 1.0, 1.0)

    >>> w1.u_rgb
    16777215

    '''

    __slots__ = ['_red', '_green', '_blue', '_alpha']
    _CACHE = {}
    _RANGE = (0, 1, 2, 3)

    def __new__(cls, value, *args, alpha=255):
        if not args:
            if isinstance(value, Color):
                return value
            elif isinstance(value, tuple):
                A = alpha
                if len(value) == 3:
                    R, G, B = value
                else:
                    R, G, B, A = value
            elif isinstance(value, str):
                value = value.lower()
                if value.startswith('#'):
                    value = value[1:]
                    A = alpha
                    if len(value) == 6:
                        R, G, B = (
                            int(value[2 * i:2 * i + 2], 16) for i in range(3))
                    elif len(value) == 8:
                        R, G, B, A = (
                            int(value[2 * i:2 * i + 2], 16) for i in range(4))
                    elif 3 <= len(value) <= 4:
                        data = (255 * int(x, 16) / 15 for x in value)
                        if len(value) == 3:
                            R, G, B = data
                        else:
                            R, G, B, A = data
                    else:
                        raise ValueError('invalid hex code: #%s' % value)
                elif value == 'random':
                    A = 255
                    R, G, B = [random.randint(0, 255) for _ in range(3)]
                else:
                    return cls._CACHE[value]
            elif isinstance(value, int):
                R = (value & 0xff0000) >> 16
                G = (value & 0xff00) >> 8
                B = (value & 0xff) >> 0
                A = alpha
            else:
                raise ValueError
        else:
            R = value
            A = alpha
            if len(args) == 2:
                G, B = args
            else:
                G, B, A = args

        # Create new object
        new = object.__new__(cls)
        new._red = int(R)
        new._green = int(G)
        new._blue = int(B)
        new._alpha = int(A)
        return new

    # Componentes RGBa
    @property
    def red(self):
        return self._red

    @property
    def green(self):
        return self._green

    @property
    def blue(self):
        return self._blue

    @property
    def alpha(self):
        return self._alpha

    # Componentes HSI
    @property
    def hue(self):
        return NotImplemented

    @property
    def saturation(self):
        return NotImplemented

    @property
    def intensity(self):
        return NotImplemented

    # Representações em diferentes espaço de cores
    @property
    def rgba(self):
        return tuple(self)

    @property
    def rgb(self):
        return self[:3]

    @property
    def f_rgb(self):
        return tuple(x / 255. for x in self[:3])

    @property
    def f_rgba(self):
        return tuple(x / 255. for x in self)

    @property
    def u_rgba(self):
        c = self
        return (c[0] << 24) + (c[1] << 16) + (c[2] << 8) + c[3]

    @property
    def u_rgb(self):
        c = self
        return (c[0] << 16) + (c[1] << 8) + c[2]

    @property
    def hsi(self):
        return self.hsia[:-1]

    @property
    def hsia(self):
        # Conversão para (H)ue, (S)aturation, (I)ntensity
        # ref: https://en.wikipedia.org/wiki/RGB_color_model#Nonlinearity
        R, G, B, a = self

        I = (R + G + B) / 3
        S = 1 - min(R, G, B) / I

        # Valores normalizados
        r, g, b = R / 255, G / 255, B / 255
        h_numer = acos(((r - g) + (r - b)) / 2)
        h_denom = sqrt((r - b) ** 2 + (r - b) * (g - b))
        return h_numer / h_denom, S, I, a

    @property
    def f_hsia(self):
        return tuple(x / 255 for x in self.hsia)

    @property
    def f_hsi(self):
        return tuple(x / 255 for x in self.hsi)

    def copy(self, red=None, green=None, blue=None, alpha=None, **kwds):
        '''Copia a cor possivelmente trocando o valor de alguma das componentes
        RGBA ou componentes HSL ou HSI.

        Examples
        --------

        >>> color = Color('white')
        >>> color.copy(red=80, alpha=128)
        Color(80, 255, 255, 128)
        '''
        R, G, B, A = self

        if red is not None:
            R = red
        if green is not None:
            G = green
        if blue is not None:
            B = blue
        if alpha is not None:
            A = alpha
        if kwds:
            raise NotImplementedError

        return Color(R, G, B, A)

    # Métodos mágicos #########################################################
    def __repr__(self):
        return 'Color%s' % (tuple(self),)

    def __len__(self):
        return 4

    def __eq__(self, other):
        try:
            return (
                (self._red == other._red) and
                (self._green == other._green) and
                (self._blue == other._blue) and
                (self._alpha == other._alpha))
        except (AttributeError, TypeError):
            if len(self) == len(other):
                return all(x == y for (x, y) in zip(self, other))
            return False

    def __iter__(self):
        yield self._red
        yield self._green
        yield self._blue
        yield self._alpha

    def __getitem__(self, key):
        if isinstance(key, int):
            if key == 0:
                return self._red
            elif key == 1:
                return self._green
            elif key == 2:
                return self._blue
            elif key == 3:
                return self._alpha
            elif key < 0:
                key = len(self) - key
                if key < 0:
                    raise IndexError
                return self[key]
        else:
            return tuple(self[i] for i in self._RANGE[key])
        raise IndexError(key)

    def __hash__(self):
        return hash(self.u_rgba)

Color._CACHE.update(
    # HTML 4.01 colors.
    # See https://en.wikipedia.org/wiki/Web_colors
    white=Color('#ffffff'),
    silver=Color('#c0c0c0'),
    gray=Color('#808080'),
    black=Color('#000000'),
    red=Color('#ff0000'),
    maroon=Color('#800000'),
    yellow=Color('#ffff00'),
    olive=Color('#808000'),
    lime=Color('#00ff00'),
    green=Color('#008000'),
    aqua=Color('#00ffff'),
    teal=Color('#008080'),
    blue=Color('#0000ff'),
    navy=Color('#000080'),
    fuschia=Color('#ff00ff'),
    purple=Color('#800080'),
    transparent=Color('#ffffff00'),
    null=Color('#00000000'),
)

# SVG extended Colors
# http://www.w3.org/TR/css3-color/#svg-color
COLOR_NAMES = [
    ['aliceblue', '#F0F8FF'],
    ['antiquewhite', '#FAEBD7'],
    ['aqua', '#00FFFF'],
    ['aquamarine', '#7FFFD4'],
    ['azure', '#F0FFFF'],
    ['beige', '#F5F5DC'],
    ['bisque', '#FFE4C4'],
    ['black', '#000000'],
    ['blanchedalmond', '#FFEBCD'],
    ['blue', '#0000FF'],
    ['blueviolet', '#8A2BE2'],
    ['brown', '#A52A2A'],
    ['burlywood', '#DEB887'],
    ['cadetblue', '#5F9EA0'],
    ['chartreuse', '#7FFF00'],
    ['chocolate', '#D2691E'],
    ['coral', '#FF7F50'],
    ['cornflowerblue', '#6495ED'],
    ['cornsilk', '#FFF8DC'],
    ['crimson', '#DC143C'],
    ['cyan', '#00FFFF'],
    ['darkblue', '#00008B'],
    ['darkcyan', '#008B8B'],
    ['darkgoldenrod', '#B8860B'],
    ['darkgray', '#A9A9A9'],
    ['darkgreen', '#006400'],
    ['darkgrey', '#A9A9A9'],
    ['darkkhaki', '#BDB76B'],
    ['darkmagenta', '#8B008B'],
    ['darkolivegreen', '#556B2F'],
    ['darkorange', '#FF8C00'],
    ['darkorchid', '#9932CC'],
    ['darkred', '#8B0000'],
    ['darksalmon', '#E9967A'],
    ['darkseagreen', '#8FBC8F'],
    ['darkslateblue', '#483D8B'],
    ['darkslategray', '#2F4F4F'],
    ['darkslategrey', '#2F4F4F'],
    ['darkturquoise', '#00CED1'],
    ['darkviolet', '#9400D3'],
    ['deeppink', '#FF1493'],
    ['deepskyblue', '#00BFFF'],
    ['dimgray', '#696969'],
    ['dimgrey', '#696969'],
    ['dodgerblue', '#1E90FF'],
    ['firebrick', '#B22222'],
    ['floralwhite', '#FFFAF0'],
    ['forestgreen', '#228B22'],
    ['fuchsia', '#FF00FF'],
    ['gainsboro', '#DCDCDC'],
    ['ghostwhite', '#F8F8FF'],
    ['gold', '#FFD700'],
    ['goldenrod', '#DAA520'],
    ['gray', '#808080'],
    ['green', '#008000'],
    ['greenyellow', '#ADFF2F'],
    ['grey', '#808080'],
    ['honeydew', '#F0FFF0'],
    ['hotpink', '#FF69B4'],
    ['indianred', '#CD5C5C'],
    ['indigo', '#4B0082'],
    ['ivory', '#FFFFF0'],
    ['khaki', '#F0E68C'],
    ['lavender', '#E6E6FA'],
    ['lavenderblush', '#FFF0F5'],
    ['lawngreen', '#7CFC00'],
    ['lemonchiffon', '#FFFACD'],
    ['lightblue', '#ADD8E6'],
    ['lightcoral', '#F08080'],
    ['lightcyan', '#E0FFFF'],
    ['lightgoldenrodyellow', '#FAFAD2'],
    ['lightgray', '#D3D3D3'],
    ['lightgreen', '#90EE90'],
    ['lightgrey', '#D3D3D3'],
    ['lightpink', '#FFB6C1'],
    ['lightsalmon', '#FFA07A'],
    ['lightseagreen', '#20B2AA'],
    ['lightskyblue', '#87CEFA'],
    ['lightslategray', '#778899'],
    ['lightslategrey', '#778899'],
    ['lightsteelblue', '#B0C4DE'],
    ['lightyellow', '#FFFFE0'],
    ['lime', '#00FF00'],
    ['limegreen', '#32CD32'],
    ['linen', '#FAF0E6'],
    ['magenta', '#FF00FF'],
    ['maroon', '#800000'],
    ['mediumaquamarine', '#66CDAA'],
    ['mediumblue', '#0000CD'],
    ['mediumorchid', '#BA55D3'],
    ['mediumpurple', '#9370DB'],
    ['mediumseagreen', '#3CB371'],
    ['mediumslateblue', '#7B68EE'],
    ['mediumspringgreen', '#00FA9A'],
    ['mediumturquoise', '#48D1CC'],
    ['mediumvioletred', '#C71585'],
    ['midnightblue', '#191970'],
    ['mintcream', '#F5FFFA'],
    ['mistyrose', '#FFE4E1'],
    ['moccasin', '#FFE4B5'],
    ['navajowhite', '#FFDEAD'],
    ['navy', '#000080'],
    ['oldlace', '#FDF5E6'],
    ['olive', '#808000'],
    ['olivedrab', '#6B8E23'],
    ['orange', '#FFA500'],
    ['orangered', '#FF4500'],
    ['orchid', '#DA70D6'],
    ['palegoldenrod', '#EEE8AA'],
    ['palegreen', '#98FB98'],
    ['paleturquoise', '#AFEEEE'],
    ['palevioletred', '#DB7093'],
    ['papayawhip', '#FFEFD5'],
    ['peachpuff', '#FFDAB9'],
    ['peru', '#CD853F'],
    ['pink', '#FFC0CB'],
    ['plum', '#DDA0DD'],
    ['powderblue', '#B0E0E6'],
    ['purple', '#800080'],
    ['red', '#FF0000'],
    ['rosybrown', '#BC8F8F'],
    ['royalblue', '#4169E1'],
    ['saddlebrown', '#8B4513'],
    ['salmon', '#FA8072'],
    ['sandybrown', '#F4A460'],
    ['seagreen', '#2E8B57'],
    ['seashell', '#FFF5EE'],
    ['sienna', '#A0522D'],
    ['silver', '#C0C0C0'],
    ['skyblue', '#87CEEB'],
    ['slateblue', '#6A5ACD'],
    ['slategray', '#708090'],
    ['slategrey', '#708090'],
    ['snow', '#FFFAFA'],
    ['springgreen', '#00FF7F'],
    ['steelblue', '#4682B4'],
    ['tan', '#D2B48C'],
    ['teal', '#008080'],
    ['thistle', '#D8BFD8'],
    ['tomato', '#FF6347'],
    ['turquoise', '#40E0D0'],
    ['violet', '#EE82EE'],
    ['wheat', '#F5DEB3'],
    ['white', '#FFFFFF'],
    ['whitesmoke', '#F5F5F5'],
    ['yellow', '#FFFF00'],
    ['yellowgreen', '#9ACD32']
]
for _name, _code in COLOR_NAMES:
    Color._CACHE.setdefault(_name, Color(_code))

#
# Funções e objetos úteis
#


class color_property(property):

    '''
    Propriedade que converte automaticamente os valores fornecidos como
    strings, tuplas ou inteiros em objetos do tipo Color.

    Mantêm o valor None, caso fornecido.
    '''

    def __init__(self, name, default=None):
        self.name = name
        self.default = (None if default is None else Color(default))
        attr = '_' + name

        def fget(self):
            return getattr(self, attr, default)

        def fset(self, value):
            if value is None:
                fdel(self)
            else:
                setattr(self, attr, Color(value))

        def fdel(self):
            if hasattr(self, attr):
                delattr(self, attr)

        super(color_property, self).__init__(fget, fset, fdel)


def rgb(color):
    '''Convert input in a tuple of (red, green, blue) colors.

    Null values are converted to solid black.'''

    try:
        return color.rgb
    except AttributeError:
        return Color(color or 'black').rgb


def rgba(color):
    '''Convert input in a tuple of (red, green, blue, alpha) components

    Null values are converted to solid black.'''

    try:
        return color.rgba
    except AttributeError:
        return Color(color or 'black').rgba

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    print(Color('white'), Color(255, 255, 255), Color(0xffffffff))
    assert Color('white') == Color(255, 255, 255)
    assert Color('white') == Color(255, 255, 255, 255)
    for hexcode in ['#FFF', '#FFFF', '#FFFFFF', '#FFFFFFFF']:
        assert Color('white') == Color(hexcode)
    assert Color('white') == Color(0xffffff)
