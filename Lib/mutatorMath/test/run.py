import os
import sys
import unittest
import doctest

# The 'mutatorMath.test' sub-package is not installed along with the others.
# But we need it to be importable so we can use it in setup.py 'test_suite'.
# We would also like to run the test suite against an installed version of
# mutatorMath package, and not just against the Lib/mutatorMath source
# directory, in order to catch issues with packaging.
# Therefore, below we first import mutatorMath, so whatever 'mutatorMath' is
# first found on the PYTHONPATH will be loaded in sys.modules.
# Then, we temporarily extend the PYTHONPATH to include the location of the
# 'mutatorMath.test' sub-package, relative to the current 'run.py' script.
# This way we can import the doctest modules without also attempting to
# import the 'mutatorMath.test' sub-package, which may be missing when we
# testing an installed mutatorMath, vs the 'editable' Lib/mutatorMath.

import mutatorMath

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
try:
    import test.objects.mutator
    import test.objects.location
    import test.ufo.test
    import test.ufo.geometryTest
    import test.ufo.kerningTest
    import test.ufo.mutingTest
finally:
    sys.path.remove(HERE)


def load_tests(loader, tests, ignore):
    # doctests inline in the actual Location and Mutator objects comments
    tests.addTests(doctest.DocTestSuite(mutatorMath.objects.location))
    tests.addTests(doctest.DocTestSuite(mutatorMath.objects.mutator))

    # standalone Location and Mutator doctests
    tests.addTests(doctest.DocTestSuite(test.objects.mutator))
    tests.addTests(doctest.DocTestSuite(test.objects.location))

    # doctests in the test.ufo package
    tests.addTests(doctest.DocTestSuite(test.ufo.test))
    tests.addTests(doctest.DocTestSuite(test.ufo.geometryTest))
    tests.addTests(doctest.DocTestSuite(test.ufo.kerningTest))
    tests.addTests(doctest.DocTestSuite(test.ufo.mutingTest))

    return tests


if __name__ == '__main__':
    sys.exit(unittest.main())
