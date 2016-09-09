# -*- coding: utf8 -*-
from __future__ import print_function
import pytest
from FGAme.events import EventDispatcher, signal


@pytest.fixture
def A():
    class A(EventDispatcher):
        foo = signal('foo')
        foobar = signal('foo-bar', num_args=1)
        bar = signal('bar', 'x')
    return A


def test_name(A):
    class B(A):
        pass
    assert A.__name__ == 'A'
    assert B.__name__ == 'B'


def test_has_triggers(A):
    methods = dir(A)
    assert 'trigger_foo' in methods
    assert 'trigger_bar' in methods
    assert 'trigger_foo_bar' in methods


def test_subclass_has_triggers(A):
    class B(A):
        pass
    
    methods = dir(B)
    assert 'trigger_foo' in methods
    assert 'trigger_bar' in methods
    assert 'trigger_foo_bar' in methods


def test_subclass_can_add_signals(A):
    class B(A):
        ham = signal('ham')
    
    methods = dir(B)
    print(methods)
    assert 'trigger_foo' in methods
    assert 'trigger_bar' in methods
    assert 'trigger_foo_bar' in methods
    assert 'trigger_ham' in methods


def test_subclass_signals(A):
    print(A.foo)

if __name__ == '__main__':
    import os 
    os.system('py.test test_events.py -q')

