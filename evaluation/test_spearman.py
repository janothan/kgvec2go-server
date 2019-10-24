from scipy.stats import spearmanr
import unittest

class TestSpearmanMethod(unittest.TestCase):


    def test_spearmanr(self):
        self.assertEqual(1, spearmanr([1, 2, 3], [4, 5, 6]).correlation)
        self.assertEqual(1, spearmanr([1, 2, 5], [4, 5, 9]).correlation)
        self.assertEqual(-1, spearmanr([1, 2, 5], [100, 99, 88]).correlation)