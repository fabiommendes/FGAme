import manuel.ignore
import manuel.codeblock
import manuel.doctest
import manuel.testing
import os


def make_manuel_suite():
    """
    Prepare Manuel test suite.
    """

    # Wrap function so pytest do not expect an spurious "self" fixture.
    def _wrapped(func, name):
        wrapped = lambda: func()
        wrapped.__name__ = name
        return wrapped

    # Collect documentation files
    cd = os.path.dirname
    path = cd(cd(cd(cd(__file__))))
    doc_path = os.path.join(path, 'docs')
    files = sorted(os.path.join(doc_path, f) for f in os.listdir(doc_path))
    files = (f for f in files if f.endswith('.rst') or f.endswith('.txt'))

    # Create manuel suite
    m = manuel.ignore.Manuel()
    m += manuel.doctest.Manuel()
    m += manuel.codeblock.Manuel()

    # Copy tests from the suite to the global namespace
    names = globals()
    suite = manuel.testing.TestSuite(m, *files)
    for i, test in enumerate(suite):
        name = 'test_doc_%s' % i
        names[name] = _wrapped(test.runTest, name)
    return suite

make_manuel_suite()
