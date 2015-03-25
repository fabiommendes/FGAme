# -*- coding: utf8 -*-

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
from collections import MutableSequence
import string


class Parser(object):

    '''Processa um arquivo de declaração de objetos. Retorna uma árvore com a
    hierarquia implícita na declaração. A estrutura resultante é mais
    conveniente para processamento futuro.

    >>> example = """
    ... Rect:
    ...     shape: (100, 200)
    ...     vel: (100, 100)
    ...     color: red
    ...
    ... # Comentários
    ... draw.Triangle:
    ...     length: 100
    ...     pos: (0, 1)
    ...     color: black
    ...
    ... Rect:
    ... Triangle:"""
    >>> tree = parse_data(example)
    >>> print(tree[1])
    draw.Triangle:
        length: 100
        pos: (0, 1)
        color: 'black'
    '''

    def __init__(self, buffer):
        if isinstance(buffer, str):
            buffer = StringIO(buffer)
        self.buffer = buffer

    def parse(self):
        '''Retorna uma lista de listas onde cada nó representa um ponto na
        hierarquia definida pela declaração fornecida junto com seu número de
        linha.'''

        lines = list(enumerate(L.rstrip() for L in self.buffer.readlines()))
        root = Root()
        currpath = [root]
        identation = -1

        for ln, line in get_logical_lines(lines):
            idx = get_indentation(line)

            # Linhas que não terminam com ":" são atribuições de valor.
            # Modifica o nó para que estas linhas já carreguem o valor
            # processado
            data = line.strip()
            node = self.process_line(ln, data)

            # Mesmo nível hierárquico
            if idx == identation:
                currpath[-2].children.append(node)
                currpath[-1] = node

            # Sobe um nível hierárquico
            elif idx <= identation:
                currpath.pop()
                currpath[-2].children.append(node)
                currpath[-1] = node

            # Desce um nível hierárquico
            else:
                currpath[-1].children.append(node)
                currpath.append(node)

            identation = idx

        return root

    def process_line(self, ln, data):
        '''Retorna um objeto que representa a instrução desenvolvida na linha
        fornecida'''

        if data.endswith(':'):
            return Header.from_string(data, ln)
        else:
            return Assignment.from_string(data, ln)

#=========================================================================
# Classes auxiliares e nós na árvore de Parse
#=========================================================================
#
# Classe base para criação de nós
#


class Root(MutableSequence):

    def __init__(self):
        self.children = []

    def __str__(self):
        return '\n'.join(str(x) for x in self.children)

    def __repr__(self):
        return 'Root(%r)' % self.children

    # Métodos abstratos de MutableSequence
    def __delitem__(self, idx):
        del self.children[idx]

    def __getitem__(self, idx):
        return self.children[idx]

    def __len__(self):
        return len(self.children)

    def __setitem__(self, idx, value):
        self.children[idx] = value

    def insert(self, idx, value):
        self.children.insert(idx, value)


class Header(object):

    def __init__(self, name, ln=0):
        self.name = name
        self.ln = ln
        self.children = []

    @classmethod
    def from_string(cls, data, ln):
        data = data.strip()
        data = data[:-1]
        if data[0] == '<' and data[-1] == '>':
            return Group(data[1:-1], ln)
        else:
            return Declaration(data, ln)

    def __str__(self):
        out = [self.strheader()]
        for child in self.children:
            for line in str(child).splitlines():
                out.append('    ' + line)
        return '\n'.join(out)


class Group(Header):

    def strheader(self):
        return '<%s>:' % self.name


class Declaration(Header):

    def strheader(self):
        return '%s:' % self.name


class Assignment(object):
    __slots__ = ['name', 'value', 'ln']

    def __init__(self, name, value, ln=0):
        self.name = name
        self.value = value
        self.ln = ln

    def __repr__(self):
        return '%s: %r' % (self.name, self.value)

    @classmethod
    def from_string(cls, data, ln=0):
        '''Inicializa a partir de uma string do tipo "foo: bar"'''

        data = data.strip()
        name, _, data = data.partition(':')
        data = cls._process_data(data)
        return cls(name, data, ln=ln)

    @classmethod
    def _process_data(cls, data):
        # HACK!! Implemente isso direito!
        data = data.strip()

        # Números
        if data[0].isdigit():
            return number(data)

        # Strings
        elif data.isalnum() and data[0] in string.ascii_letters:
            return data
        elif (data[0] == data[-1]) and data[0] in ['"', "'"]:
            return data

        # Tuplas
        elif data[0] == '(' and data[-1] == ')':
            data = data[1:-1].split(',')
            return tuple(cls._process_data(x) for x in data)

        # Listas
        elif data[0] == '[' and data[-1] == ']':
            data = data[1:-1].split(',')
            return [cls._process_data(x) for x in data]

        # Erro
        else:
            raise ValueError('could not process data: %r' % data)

#=========================================================================
# Funções auxiliares
#=========================================================================


def number(data):
    '''Converte uma string em um número'''
    try:
        return int(data)
    except:
        return float(data)


def get_logical_lines(lines):
    '''Processa as linhas eliminando linhas vazias e comentários'''

    out = []
    for i, line in lines:
        # Discard empty lines
        if not line.strip():
            continue

        # Strip comment lines
        if line.lstrip().startswith('#'):
            continue

        out.append((i, line))
    return out


def get_indentation(st):
    '''Retorna um inteiro com o nível de identação da string `st`'''

    idx = 0
    for c in st:
        if c == ' ':
            idx += 1
        else:
            break
    return idx


def parse_data(data):
    '''Processa o conteúdo de declarações de objeto fornecido e retorna uma
    árvore com a hierarquia implícita no arquivo.'''

    return Parser(data).parse()

if __name__ == '__main__':
    import doctest
    doctest.testmod()
