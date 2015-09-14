'''
Parsers para micro-linguagens baseadas em indentação.
'''
import re
from collections import namedtuple

#
# Regex constants
#
WHITESPACE = re.compile('\s+')
B_WHITESPACE = re.compile('^\s+')


Node = namedtuple('Node', ['head', 'body', 'nodes', 'line_no'])


class rule(object):

    def __init__(self, func, is_optional=False):
        self.is_optional = is_optional
        self._func
        self._node = None
        self._result = None

    def is_valid(self, node):
        try:
            self._result = self._func(node)
            self._node = node
            return True
        except ValueError:
            return False

    def parse(self, node):
        if node is self._node:
            return self._result
        elif not self.is_valid(node):
            raise ValueError('cannot parse an invalid node')
        else:
            return self._result

    @classmethod
    def from_keys(self, **kwds):
        pass


class IndentParser(object):

    def __init__(self):
        self.rules = []

    def parse(self, source):
        return blockparse(source)

    def __call__(self, *args, **kwds):
        return self.parse(*args, **kwds)


def blockparse(source):
    '''Retorna uma lista de nós do tipo Node, onde cada nó possui a
    estrutura::

        <one line head>
            <multi line body>
    '''
    blocks = []
    indent = 0
    source = deindent(normalize_blank_lines(source))

    # Cria blocos
    for line_no, line in enumerate(source.splitlines()):
        if line:
            indent = get_indent(line)
            if not indent:
                block = Node(line, [], None, line_no)
                blocks.append(block)
            else:
                body = blocks[-1].body
                if body and get_indent(body[-1]) != indent:
                    raise SyntaxError('inconsistent indentation')
                body.append(line)
        elif blocks:
            blocks[-1]

    # Funde lista de linhas para cada bloco
    for idx, block in enumerate(blocks):
        head, data, _, line_no = block
        data = deindent('\n'.join(data))
        try:
            nodes = blockparse(data)
        except SyntaxError:
            nodes = None
        blocks[idx] = Node(head, data, nodes, line_no)

    return blocks


def normalize_blank_lines(source):
    '''Transformas linhas que contêm apenas espaços em linhas vazias'''

    lines = source.splitlines()
    lines = [('' if line.isspace() else line) for line in lines]
    return '\n'.join(lines)


def normalize_tabs(source, size=4):
    '''Troca tabs por espaços'''

    return source.replace('\t', ' ' * size)


def deindent(source):
    '''Remove uma indentação global'''

    # Normaliza
    source = normalize_blank_lines(normalize_tabs(source))

    # Encontra indentação
    indent = float('inf')
    lines = source.splitlines()
    for line in lines:
        if line:
            match = B_WHITESPACE.match(line)
            if match:
                indent = min(indent, match.end())

    # Reindenta todas as linhas
    if indent == float('inf'):
        indent = 0
    for i, line in enumerate(lines):
        if line:
            lines[i] = line[indent:]

    return '\n'.join(lines)


def get_indent(st):
    '''Retorna a indentação da string de entrada'''

    for idx, c in enumerate(st):
        if c != ' ':
            return idx
    return 0


source = '''
    Group:
        color: red

        Circle:
            radius: 10
            pos: middle

        Circle:
            radius: 10
            pos: middle + (100, 100)


    foo:
        arg1, arg2, arg3
        noarg
        arg4

        foo: bar

        @long-press(up):
            self.move(0, 10)

        @long-press(down):
            self.move(0, -10)

    bar:
        sdfsdfsd sdfsdf
'''

p = IndentParser()
print(p.parse(source))
