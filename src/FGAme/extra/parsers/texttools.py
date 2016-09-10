'''
String manipulation functions
'''

import re
from collections import deque

#
# Regex constants
#
WHITESPACE = re.compile('\s+')
B_WHITESPACE = re.compile('^\s+')


#
# API functions
#
def rollbackiter(iterator):
    '''Iterator that accepts rolling back by using the send() method'''
    
    iterator = iter(iterator)
    buffer = deque([])
    while True:
        try:
            x = buffer.popleft() if buffer else next(iterator)
        except StopIteration:
            break
        y = yield x
        if y is not None:
            buffer.append(y)
            buffer.append(x)

        
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


def lwhitespace(st):
    '''Return a string with the whitespace at the left of st.'''

    ws = []
    for c in st:
        if c in ' \t':
            ws.append(c)
        else:
            break
    return ''.join(ws)


def next_block(lineiter):
    '''Return an iterator over all lines in the next_level indentation block from the
    given iterable over (lineno, line) objects. Line strings do not have a 
    trailing newline.'''
    
    lines = []
    indent = '\x00'
    indentlevel = 0
    
    for lineno, line in lineiter:
        if line.strip() == '':
            lines.append((lineno, ''))
        else:
            if not line.startswith(indent):
                if indent is '\x00':
                    indent = lwhitespace(line)
                    indentlevel = len(indent)
                else:
                    len(indent)
            else:
                if not line[indentlevel].isspace():
                    break
            lines.append((lineno, line[indentlevel:].rstrip()))
    
    try:
        lineiter.send(lines[-1])
        lines.pop()
    except (StopIteration, IndexError):
        pass
    return lines


def split_indent_blocks(st, lineno=0, stringfy=True):
    '''Given a string of text, split into blocks of same indentation'''
    
    lines = rollbackiter(enumerate(st.splitlines()))
    block = True
    blocks = []

    while block:
        block = next_block(lines)
        blocks.append(block)
    
    if not blocks[-1]:
        blocks.pop()
    
    if stringfy:
        return [format_block(x) for x in blocks]
    else:
        return blocks

def format_block(block):
    '''Convert a block to a string of text'''
    
    data = '\n'.join(line for (_, line) in block)
    return data.strip('\n')

    
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
            self.imove(0, 10)

        @long-press(down):
            self.imove(0, -10)

    bar:
        sdfsdfsd sdfsdf
'''

if __name__ == '__main__':
    from pprint import pprint
    print(*map(format_block, split_indent_blocks(source)), sep='\n')


