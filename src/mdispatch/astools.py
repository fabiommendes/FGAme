'''
Created on 12/05/2015

@author: chips
'''

import ast
import inspect
import sys
from ast import AST as Node

__author__ = 'Martin Blais <blais@furius.ca>'


def dump(obj):
    try:
        printer = obj.dump
    except AttributeError:
        print(type(obj))
        printer = obj.__repr__
    return printer()


def indent(st, prefix):
    L = [prefix + y for y in st.splitlines()]
    return '\n'.join(L)


def tname(obj):
    return type(obj).__name__


class Symbol(str):

    def __repr__(self):
        return ':' + self.__str__()


class Op(str):

    def __repr__(self):
        return ':%s()' % self.__str__()


class ExprMeta(type):

    def __new__(cls, name, bases, ns):
        return type.__new__(cls, name, bases, ns)

    def __init__(self, name, bases, ns):
        if hasattr(self, 'fields'):
            self.nargs = len(self.fields)

            for i, f in enumerate(self.fields):
                setattr(self, f, property(type(self)._make_getter(i)))

    @classmethod
    def _make_getter(cls, idx):
        def getter(self):
            return self.args[idx]
        return getter


class Expr(object, metaclass=ExprMeta):
    nargs = None

    def __init__(self, head, *args, type=None, ast=None, lineno=None,
                 col_offset=None):
        self.head = head
        self.args = list(args)
        if (self.nargs is not None) and (len(self.args) != self.nargs):
            N = self.nargs
            M = len(self.args)
            raise ValueError('expected %s args, got %s' % (N, M))

        self.type = type
        self.ast = ast
        if ast is not None:
            lineno = lineno or getattr(ast, 'lineno', None)
            col_offset = col_offset or getattr(ast, 'col_offset', None)
        self.lineno = lineno
        self.col_offset = col_offset

    def dump(self):
        '''Return a pretty-printed string representation of itself'''

        data = indent('\n'.join([dump(x) for x in self.args]), '  ')
        return '%s:\n%s' % (self.head, data)

    def dump_ast(self):
        '''Convert expression to Python's internal AST representation'''
        pass

    def compile(self):
        '''Compiles itself'''

        return compile(self.source(), '<none>')

    def source(self):
        '''Return the source code representation of itself'''

        pass

    @classmethod
    def from_object(cls, obj):
        data = inspect.getsource(obj)
        return cls.from_ast(ast.parse(data))

    @classmethod
    def from_ast(cls, raw):
        return getattr(cls, '_from_' + tname(raw))(raw)

    @classmethod
    def _from_Module(cls, raw):
        body = map(cls.from_ast, raw.body)
        return Block(*body, ast=raw)

    @classmethod
    def _from_FunctionDef(cls, raw):
        call = []
        for arg in raw.args.args:
            name = arg.arg
            tt = arg.annotation
            default = None
            call.append(Arg(name, tt, default))
        body = map(cls.from_ast, raw.body)
        return Function(Call(Symbol(raw.name), *call), Block(*body))

    @classmethod
    def _from_Return(cls, raw):
        return Return(cls.from_ast(raw.value))

    @classmethod
    def _from_BinOp(cls, raw):
        return Call(Op(tname(raw.op).lower()),
                    cls.from_ast(raw.left),
                    cls.from_ast(raw.right))

    @classmethod
    def _from_Name(cls, raw):
        return Symbol(raw.id)

    @classmethod
    def _from_Num(cls, raw):
        return raw.n


class HasHead(Expr):
    head = None

    def __init__(self, *args, type=None, ast=None, lineno=None,
                 col_offset=None):
        super().__init__(self.head, *args, type=type, ast=ast, lineno=lineno,
                         col_offset=col_offset)


class Block(HasHead):
    head = 'block'


class Function(HasHead):
    head = 'function'
    fields = ['call', 'body']


class Call(HasHead):
    head = 'call'


class Arg(HasHead):
    head = 'arg'
    fields = ['name', 'type_decl', 'default']

    def dump(self):
        if self.default is None:
            return 'arg: %s:%s' % tuple(self.args[:2])
        else:
            return 'arg: %s:%s (%s)' % tuple(self.args)


class Return(HasHead):
    head = 'return'
    fields = ['value']


def f(x):
    return x ** 2

e = Expr.from_object(f)
print(e.__dict__)
print(e.dump())
print(e.source())
