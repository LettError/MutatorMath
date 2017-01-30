import unittest
import doctest

import mutatorMath
import mutatorMath.test.objects.mutator
import mutatorMath.test.objects.location
import mutatorMath.test.ufo.test
import mutatorMath.test.ufo.geometryTest
import mutatorMath.test.ufo.kerningTest
import mutatorMath.test.ufo.mutingTest


def load_tests(loader, tests, ignore):
    # doctests inline in the actual Location and Mutator objects comments
    tests.addTests(doctest.DocTestSuite(mutatorMath.objects.location))
    tests.addTests(doctest.DocTestSuite(mutatorMath.objects.mutator))

    # standalone Location and Mutator doctests
    tests.addTests(doctest.DocTestSuite(mutatorMath.test.objects.mutator))
    tests.addTests(doctest.DocTestSuite(mutatorMath.test.objects.location))

    # doctests in the test.ufo package
    tests.addTests(doctest.DocTestSuite(mutatorMath.test.ufo.test))
    tests.addTests(doctest.DocTestSuite(mutatorMath.test.ufo.geometryTest))
    tests.addTests(doctest.DocTestSuite(mutatorMath.test.ufo.kerningTest))
    tests.addTests(doctest.DocTestSuite(mutatorMath.test.ufo.mutingTest))

    return tests


if __name__ == '__main__':
    unittest.main()

