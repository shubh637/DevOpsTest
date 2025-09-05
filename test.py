import unittest
from add import add

class TestAddFunction(unittest.TestCase):
    def test_add_positive_numbers(self):
        self.assertEqual(add(3, 4), 7)

    def test_add_negative_numbers(self):
        self.assertEqual(add(-1, -1), -2)

    def test_add_zero(self):
        self.assertEqual(add(0, 5), 5)
        self.assertEqual(add(5, 0), 5)

    def test_add_floats(self):
        self.assertAlmostEqual(add(2.5, 3.1), 5.6)

if __name__ == "__main__":
    unittest.main()
