# Python test set -- built-in functions

import test.support, unittest
import sys
import pickle

import warnings
warnings.filterwarnings("ignore", "integer argument expected",
                        DeprecationWarning, "unittest")

class RangeTest(unittest.TestCase):
    def test_range(self):
        self.assertEqual(list(range(3)), [0, 1, 2])
        self.assertEqual(list(range(1, 5)), [1, 2, 3, 4])
        self.assertEqual(list(range(0)), [])
        self.assertEqual(list(range(-3)), [])
        self.assertEqual(list(range(1, 10, 3)), [1, 4, 7])
        self.assertEqual(list(range(5, -5, -3)), [5, 2, -1, -4])

        a = 10
        b = 100
        c = 50

        self.assertEqual(list(range(a, a+2)), [a, a+1])
        self.assertEqual(list(range(a+2, a, -1)), [a+2, a+1])
        self.assertEqual(list(range(a+4, a, -2)), [a+4, a+2])

        seq = list(range(a, b, c))
        self.assertTrue(a in seq)
        self.assertTrue(b not in seq)
        self.assertEqual(len(seq), 2)

        seq = list(range(b, a, -c))
        self.assertTrue(b in seq)
        self.assertTrue(a not in seq)
        self.assertEqual(len(seq), 2)

        seq = list(range(-a, -b, -c))
        self.assertTrue(-a in seq)
        self.assertTrue(-b not in seq)
        self.assertEqual(len(seq), 2)

        self.assertRaises(TypeError, range)
        self.assertRaises(TypeError, range, 1, 2, 3, 4)
        self.assertRaises(ValueError, range, 1, 2, 0)

        self.assertRaises(TypeError, range, 0.0, 2, 1)
        self.assertRaises(TypeError, range, 1, 2.0, 1)
        self.assertRaises(TypeError, range, 1, 2, 1.0)
        self.assertRaises(TypeError, range, 1e100, 1e101, 1e101)

        self.assertRaises(TypeError, range, 0, "spam")
        self.assertRaises(TypeError, range, 0, 42, "spam")

        self.assertEqual(len(range(0, sys.maxsize, sys.maxsize-1)), 2)

        r = range(-sys.maxsize, sys.maxsize, 2)
        self.assertEqual(len(r), sys.maxsize)

    def test_repr(self):
        self.assertEqual(repr(range(1)), 'range(0, 1)')
        self.assertEqual(repr(range(1, 2)), 'range(1, 2)')
        self.assertEqual(repr(range(1, 2, 3)), 'range(1, 2, 3)')

    def test_pickling(self):
        testcases = [(13,), (0, 11), (-22, 10), (20, 3, -1),
                     (13, 21, 3), (-2, 2, 2)]
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            for t in testcases:
                r = range(*t)
                self.assertEquals(list(pickle.loads(pickle.dumps(r, proto))),
                                  list(r))

    def test_odd_bug(self):
        # This used to raise a "SystemError: NULL result without error"
        # because the range validation step was eating the exception
        # before NULL was returned.
        with self.assertRaises(TypeError):
            range([], 1, -1)

def test_main():
    test.support.run_unittest(RangeTest)

if __name__ == "__main__":
    test_main()
