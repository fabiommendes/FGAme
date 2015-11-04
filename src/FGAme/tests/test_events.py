from FGAme.events import EventDispatcher, signal
import unittest

class TestEventDispatcher(unittest.TestCase):
    def setUp(self):
        class A(EventDispatcher):
            foo = signal('foo')
            foobar = signal('foo-bar', num_args=1)
            bar = signal('bar', 'x')
            
        self.A = A

    def test_name(self):
        class B(self.A):
            pass
        assert self.A.__name__ == 'A'
        assert B.__name__ == 'B'

    def test_has_triggers(self):
        methods = dir(self.A)
        self.assertIn('trigger_foo', methods)
        self.assertIn('trigger_bar', methods)
        self.assertIn('trigger_foo_bar', methods)

    def test_subclass_has_triggers(self):
        class B(self.A):
            pass
        
        methods = dir(B)
        self.assertIn('trigger_foo', methods)
        self.assertIn('trigger_bar', methods)
        self.assertIn('trigger_foo_bar', methods)

    def test_subclass_can_add_signals(self):
        class B(self.A):
            ham = signal('ham')
        
        methods = dir(B)
        self.assertIn('trigger_foo', methods)
        self.assertIn('trigger_bar', methods)
        self.assertIn('trigger_foo_bar', methods)
        self.assertIn('trigger_ham', methods)

if __name__ == '__main__':
    from pytest import main 
    main('test_events.py -q')

