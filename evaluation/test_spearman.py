from collections import namedtuple

from scipy.stats import spearmanr
from math import factorial
import unittest

from evaluation.calculate_rho import Evaluator


class TestSpearmanMethod(unittest.TestCase):


    def test_spearmanr(self):
        self.assertEqual(1, spearmanr([1, 2, 3], [4, 5, 6]).correlation)
        self.assertEqual(1, spearmanr([1, 2, 5], [4, 5, 9]).correlation)
        self.assertEqual(-1, spearmanr([1, 2, 5], [100, 99, 88]).correlation)

    def test_factorial(self):
        self.assertEqual(6, factorial(3))
        self.assertEqual(24, factorial(4))
        self.assertEqual(2, factorial(2))

    def test_get_relative_score_for_borda(self):
        GsEntryResult = namedtuple('Entry', 'w1 w2 sim')

        list = []
        list.append(GsEntryResult('a', 'b',0.5))
        list.append(GsEntryResult('c', 'd',1.0))
        list.append(GsEntryResult('e', 'f',0)) # will be ignored
        list.append(GsEntryResult('g', 'h',-0.5))

        result = Evaluator.get_relative_score_for_borda(list)
        self.assertEqual(0.5, Evaluator.get_entry_of_relative_score_for_borda(result, 'c', 'd').score)


    def test_sum_scores(self):
        GsEntryResult = namedtuple('Entry', 'w1 w2 sim')

        list_1 = []
        list_1.append(GsEntryResult('a', 'b',0.5))
        list_1.append(GsEntryResult('c', 'd',1.0))
        list_1.append(GsEntryResult('g', 'h',-0.5))

        list_2 = []
        list_2.append(GsEntryResult('a', 'b', 0.5))
        list_2.append(GsEntryResult('c', 'd', 1.0))
        list_2.append(GsEntryResult('e', 'f', 3))
        list_2.append(GsEntryResult('g', 'h', 0.5))

        result = Evaluator.sum_scores([list_1, list_2])
        self.assertEqual(1, Evaluator.get_entry_of_relative_score_for_borda(result, 'a', 'b').score)
        self.assertEqual(3, Evaluator.get_entry_of_relative_score_for_borda(result, 'd', 'f').score)
        self.assertEqual(0, Evaluator.get_entry_of_relative_score_for_borda(result, 'g', 'h').score)



