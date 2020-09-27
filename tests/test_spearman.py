from collections import namedtuple

from scipy.stats import spearmanr
from math import factorial

from kgvec2go_server.evaluation.calculate_rho import Evaluator


class TestSpearmanMethod:

    def test_spearmanr(self):
        """This test just checks the behavior of scipy.stats.spearmanr.
        """
        assert 1 == spearmanr(a=[1, 2, 3], b=[4, 5, 6]).correlation
        assert 1 == spearmanr(a=[1, 2, 5], b=[4, 5, 9]).correlation
        assert -1 == spearmanr(a=[1, 2, 5], b=[100, 99, 88]).correlation

    def test_factorial(self):
        """This test just checks the behavior of math.factorial.
        """
        assert 6 == factorial(3)
        assert 24 == factorial(4)
        assert 2 == factorial(2)

    def test_get_relative_score_for_borda(self):
        GsEntryResult = namedtuple('Entry', 'w1 w2 sim')

        my_list = [GsEntryResult('a', 'b', 0.5),
                   GsEntryResult('c', 'd', 1.0),
                   GsEntryResult('e', 'f', 0),
                   GsEntryResult('g', 'h', -0.5)]

        result = Evaluator.get_relative_score_for_borda(my_list)
        assert 0.5 == Evaluator.get_entry_of_relative_score_for_borda(result, 'c', 'd').score

    def test_sum_scores(self):
        GsEntryResult = namedtuple('Entry', 'w1 w2 score')

        list_1 = [GsEntryResult('a', 'b', 0.5),
                  GsEntryResult('c', 'd', 1.0),
                  GsEntryResult('g', 'h', -0.5)]

        list_2 = [GsEntryResult('a', 'b', 0.5),
                  GsEntryResult('c', 'd', 1.0),
                  GsEntryResult('e', 'f', 3),
                  GsEntryResult('g', 'h', 0.5)]

        result = Evaluator.sum_scores([list_1, list_2])
        assert 1 == Evaluator.get_entry_of_relative_score_for_borda(result, 'a', 'b').score
        assert 3 == Evaluator.get_entry_of_relative_score_for_borda(result, 'e', 'f').score
        assert 0 == Evaluator.get_entry_of_relative_score_for_borda(result, 'g', 'h').score
