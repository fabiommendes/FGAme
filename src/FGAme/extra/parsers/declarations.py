"""
======================
Declaração de cenários
======================

A FGAme permite a criação de cenários através de uma linguagem declarativa
que muitas vezes é mais conveniente que a inicialização através de código.

Um arquivo de declaração possui uma estrutura definida por indentação::

    <brick@AABB>:
        shape: (100, 100)
        color: random
        image: foo.png
        
    <red>:
        color: red
    
    bricks:
        brick1: brick red
            pos: (0, 0)
        
        brick2@draw.AABB: brick
            pos: (50, 20)

"""

import re
from collections import namedtuple, deque
from ...mathtools import Vec
from ... import pos
from .texttools import normalize_tabs, normalize_blank_lines
from colortools import COLOR_NAMES

__all__ = ['parse_declaration', 'populate', 'GroupFactory', 'ObjectFactory'] 
Token = namedtuple('Token', ['typ', 'value', 'line', 'column', 'indent'])


class Deferred:
    """Fábrica de atributos que devem ser calculados durante a criação por 
    algum tipo de função."""
    
    def __init__(self, func):
        self.func = func
        
    def __call__(self):
        return self.func()
    
def getvalue(x):
    """Retorna x ou executa um deferred"""
    
    return (x() if isinstance(x, Deferred) else x)


class ObjectFactory:
    """Fábrica de um único objeto.
    
    Normalmente criada a partir de um arquivo de declarações para ser inserida
    em um GroupFactory."""
    
    def __init__(self, name, cls=None, 
                 args=(), kwargs=None, 
                 transforms=None, templates=None, istemplate=False):
        self.name = name
        self.cls = cls
        self.args = args
        self.kwargs = ({} if kwargs is None else kwargs)
        self.templates = list(templates or [])
        self.istemplate = istemplate

    def addtemplate(self, template):
        """Registra um template ao objeto"""
        
        self.templates.append(template)
    
    def updatetemplate(self, name, concrete):
        """Atualiza um template definido por string por sua realização 
        concreta"""
        
        if name in self.templates:
            idx = self.templates.index(name)
            self.templates[idx] = concrete
    
    def update(self, factory):
        self.args = factory.args or self.args
        self.kwargs.update(factory.kwargs) 

    def setdefault(self, factory):
        self.args = self.args or factory.args
        D = dict(factory.args)
        D.update(self.args)
        self.kwargs = D
        
    def apply_templates(self):
        for template in self.templates:
            self.cls = self.cls or template.cls
            self.args = self.args or template.args
            D = dict(template.kwargs)
            D.update(self.kwargs)
            self.kwargs = D
        
        del self.templates[:]
    
    def new(self):
        args = map(getvalue, self.args)
        kwargs = {k: getvalue(v) for (k, v) in self.kwargs.items()}
        return self.cls(*args, **kwargs)
    

class GroupFactory:
    """Fábrica de um grupo de objetos.
    
    Normalmente criada a partir de um arquivo de declarações"""
    
    def __init__(self, name):
        self.name = name
        self._factories = []
        self._templates = {}
        
    def add(self, obj):
        self._factories.append(obj)
    
    def addtemplate(self, name, templ):
        self._templates[name] = templ
        
    def create_at(self, world):
        for obj in self.new():
            world.add(obj)
    
    def new(self):
        # Update deferred templates 
        for factory in self._factories:
            for tname in factory.templates:
                try:
                    template = self._templates[tname]
                    factory.updatetemplate(tname, template)
                except KeyError:
                    continue
            factory.apply_templates()
            
        # Create all objects in factory
        out = []
        for factory in self._factories:
            out.append(factory.new())
        return out


class DeclarationParser:
    """Parse a declaration file"""
    
    
    def __init__(self, source):
        try: 
            self.source = source.read()
        except AttributeError:
            self.source = source
        self.source = normalize_tabs(self.source, 4)
        self.source = normalize_blank_lines(self.source)
        self.lines = source.splitlines()
        
    def tokenize(self, source):
        """Tokenize source file.
        
        This special generator responds to commands that can be sent through 
        the iterator.send() function. If the argument is 'skipline', it returns
        the next_level source line verbatim as a LINE token. One can also push back
        tokens to the iterator by sending token instances.
        """
        
        # Inspired on example at: https://docs.python.org/3/library/re.html
        
        token_specification = [
            # Base types
            ('NUMBER',  r'\d+(\.\d*)?'),
            ('STRING',  r'"[^"]*"'),
            ('VEC',     r'[(]\s*(?P<x>\d+(\.\d*)?),\s*(?P<y>\d+(\.\d*)?)\s*[)]'),
            ('COMMENT', r'#[^\n]*'),
            
            # Identifiers
            ('NAME',      r'[A-Za-z][A-Za-z0-9_]*'),
            ('TEMPLATE',  r'<(?P<name>[a-zA-Z][a-zA-Z0-9_]*)(@(?P<type>[a-zA-Z][a-zA-Z0-9_]*))?>'),
            
            # Arithmetic operators
            ('OP',      r'[+\-*/]'),
            
            # Special operators
            ('COLON',     r':'),
            
            # Open / close parens
            ('LPAREN',      r'[(]'),
            ('RPAREN',      r'[)]'),
                               
            # Line endings
            ('NEWLINE', r'\n'),
            
            # Skip spaces and tabs (or maybe track indentation)
            ('SKIP',    r'[ \t]+'),
            
            # Any other character
            ('MISMATCH',r'.'),
        ]
        
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        line = None
        lasttok = Token(None, None, None, None, 0)
        lineno = 1
        linestart = 0
        indent = 0
        indentlevels = ['']
        buffer = deque()
        
        state = yield lasttok
        for mo in re.finditer(tok_regex, source):
            kind = mo.lastgroup
            value = mo.group(kind)
            
            # Return line verbatim
            if state == 'skipline':
                if kind == 'NEWLINE':
                    linestart = mo.end()
                    lineno += 1
                    lasttok = Token('LINE', (line or '') + '\n', lineno, 0, 0)
                    state = line = None
                    indent = 0
                elif line is None:
                    line = ''
                    continue
                else:
                    line += value
                    continue
            
            else:
                # Process the values for each token type
                if kind == 'NEWLINE':
                    linestart = mo.end()
                    lineno += 1
                    indent = 0
                
                elif kind == 'SKIP':
                    if lasttok.typ == 'NEWLINE':
                        if value in indentlevels:
                            indent = indentlevels.index(value)
                        else:
                            if len(indentlevels[-1]) >= len(value):
                                raise RuntimeError('inconsistent indentation level at line %s' % lineno)
                            indent = len(indentlevels)
                            indentlevels.append(value)
                    continue
                
                elif kind == 'MISMATCH':
                    raise RuntimeError('%r unexpected on line %d' % (value, lineno))
                
                elif kind == 'TEMPLATE':
                    name = mo.group('name')
                    type_ = mo.group('type')
                    value = (name, type_)
                    
                elif kind == 'STRING':
                    value = value[1:-1]
                    
                elif kind == 'NUMBER':
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                
                elif kind == 'VEC':
                    x = float(mo.group('x'))
                    y = float(mo.group('y'))
                    value = Vec(x, y)
                
                column = mo.start() - linestart
                lasttok = Token(kind, value, lineno, column, indent)
            
            buffer.append(lasttok)
            while buffer:
                lasttok = buffer.popleft()
                cmd = yield lasttok
                if cmd is not None:
                    while isinstance(cmd, Token):
                        buffer.append(cmd)
                        cmd = yield lasttok
                    
                    if cmd is not None:
                        state = cmd
                        cmd = yield lasttok
                        assert cmd is None, 'cannot send two commands at once'
        
        
    def parse(self):
        """Parse object's source"""
        
        ignore_types = {'NEWLINE', 'COMMENT', None}
        tokens = iter(self.tokenize(self.source))
        templates = {}
        blocks = {}
        
        for tk in tokens:
            if tk.typ in ignore_types:
                continue
            
            # Root template definitions
            if tk.typ == 'TEMPLATE':
                template = self.parse_template(tk, tokens)
                templates[template.name] = template
            
            # A block of object/template definitions
            elif tk.typ == 'NAME':
                block = self.parse_group(tk, tokens)
                blocks[block.name] = block
                
            else:
                raise RuntimeError('invalid block')
            
        for name, template in templates.items():
            for block in blocks.values():
                block.addtemplate(name, template)
        return blocks
            
    def parse_group(self, tk, tokens):
        """Parse a group of object definitions"""
        
        self.__assure_block_start(tk, tokens)
        group = GroupFactory(tk.value)
        for tk in tokens:
            group.add(self.parse_object(tk, tokens))
                
        return group
    
    def parse_object(self, tk, tokens):
        """Parse a template block and return the corresponding object factory."""
        
        self.__assure_colon(tk, tokens)
        if tk.typ == 'NAME':
            name, type_ = tk.value, None
        else:
            name, type_ = tk.value
        
        templates = [tk.value for tk in self.tkline(tokens)]
        args, kwargs, transforms = self.parse_block_contents(tk.indent + 1, tokens)
        
        return ObjectFactory(name, _gettype(type_),
                             templates=templates, 
                             args=args, kwargs=kwargs, 
                             transforms=transforms,
                             istemplate=False)
    
    def parse_template(self, tk, tokens):
        """Parse a template block and return the corresponding object factory."""
        
        self.__assure_block_start(tk, tokens)
        name, type_ = tk.value
        args, kwargs, transforms = self.parse_block_contents(tk.indent + 1, tokens)
        
        return ObjectFactory(name, _gettype(type_), 
                             args=args, kwargs=kwargs, 
                             transforms=transforms,
                             istemplate=True)
        
    def parse_block_contents(self, indent, tokens):
        """Parse the contents of a template or object definition block.
        
        Return a tuple with (args, kwargs, transforms)"""
        
        args = ()
        kwargs = {}
        transforms = []
        
        for tk in tokens:
            if tk.typ in ('NEWLINE', 'COMMENT'):
                continue
            
            if tk.indent < indent:
                tokens.send(tk)
                break

            if tk.typ == 'NAME':
                key = tk.value
                value = self.parse_expression(tokens, ctx=CTX_VAR.get(key))
                kwargs[key] = value
                
        return (args, kwargs, transforms)
    
    def parse_expression(self, tokens, ctx=None):
        """Parse the contents of an assignment expression of the type 
        ``name: data``."""
        
        self.__assure_colon('var', tokens)
        data = self.tkline(tokens)
        if len(data) == 1:
            tk = data[0]
            if tk.typ in ['STRING', 'VEC', 'NUMBER']:
                return tk.value
            elif tk.typ == 'NAME':
                return (ctx or CTX_DEFAULT)[tk.value]
            else:
                raise RuntimeError('invalid token: %s' % tk.typ)
        else:
            raise NotImplementedError('expressions are not supported yet')

    #        
    # Utility functions
    #
    def tkline(self, tokens):
        """Fetch all tokens until find a NEWLINE"""
        
        out = []
        for tk in tokens:
            if tk.typ == 'NEWLINE':
                break
            out.append(tk)
        return out 
    
    #
    # Syntax checks
    #
    def __fmt_line(self, tk):
        return ':\n  %s) ' % tk.line + self.lines[tk.line - 1]
    
    def __assure_block_start(self, name, tokens):
        tk = next(tokens) 
        if tk.typ != 'COLON':
            line = self.__fmt_line(tk)
            raise RuntimeError('expected colon after template definition' + line)
        
        tk = next(tokens)
        if tk.typ != 'NEWLINE':
            line = self.__fmt_line(tk)
            raise RuntimeError('expected to start a new block here' + line)
        
    def __assure_colon(self, name, tokens):
        tk = next(tokens)
        if tk.typ != 'COLON':
            name = name.typ
            msg = 'expected colon after %r token definition, got %r' % (name, tk.value)
            raise RuntimeError(msg + self.__fmt_line(tk))    


#
# Public API
#   
def parse_declaration(source):
    """Processa um arquivo de declarações e retorna o GroupFactory 
    correspondente."""
    
    parser = DeclarationParser(source)
    return parser.parse()

def populate(world, source, groups=None):
    """Popula o mundo com a declaração de objetos fornecida.
    
    O usuário pode passar uma string, arquivo de declarações ou um objeto do 
    tipo GroupFactory"""
    
    if isinstance(source, GroupFactory):
        if groups:
            raise TypeError('cannot declare groups to a single factory')
        return source.create_at(world)
    
    # Normalize source
    if not isinstance(source, dict):
        source = parse_declaration(source)
    
    # Normalize groups    
    if groups is None:
        groups = source.keys()
    elif isinstance(groups, str):
        groups = [groups]
    for group in groups:
        source[group].create_at(world)


#
# Utility functions
#
def _gettype(T):
    """Return type from name"""
    
    if isinstance(T, type):
        return T
    try:
        return TYPENAMES[T]
    except KeyError:
        raise ValueError('invalid type name: %s' % T)

#
# Dictionary constants
#
CTX_DEFAULT = {'inf': float('inf')}
CTX_POS = dict(
    CTX_DEFAULT,
    middle = pos.middle,
)
CTX_VEL = dict(
    CTX_DEFAULT,
)
CTX_COLOR = dict(CTX_DEFAULT, random='random')
CTX_COLOR.update(dict(COLOR_NAMES))

# Map variable names to their respective contexts
CTX_VAR = dict(pos=CTX_POS, vel=CTX_VEL, color=CTX_COLOR, colorline=CTX_COLOR)
 
# Map type names into types
import FGAme as _
TYPENAMES = {None: None} 
for name in 'AABB Circle'.split():
    TYPENAMES[name] = getattr(_, name)
    TYPENAMES['draw.' + name] = getattr(_.draw, name)
for name in 'Path Segment'.split():
    TYPENAMES['draw.' + name] = getattr(_.draw, name)
