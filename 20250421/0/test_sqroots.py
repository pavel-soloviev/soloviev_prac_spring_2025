import unittest
import quadratic


class TestSqroots(unittest.TestCase):
    def test_0(self):
        self.assertEqual(quadratic.sqroots("1 1 1"), "")

    def test_1(self):
        self.assertEqual(quadratic.sqroots("1 2 1"), "-1.0")

    def test_2(self):
        self.assertEqual(quadratic.sqroots("1 -3 2"), "2.0 1.0")

    def test_exception(self):
        with self.assertRaises(ValueError):
            quadratic.sqroots("abc")
