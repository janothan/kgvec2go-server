import unittest

from wordnet.wordnet_query_service import WordnetQueryService as wqs


class TestWordnetQueryService(unittest.TestCase):

    def test_transform_string(self):
        self.assertEqual('stabilizer', wqs.transform_string('wn-lemma:stabilizer#stabilizer-n'))


if __name__ == '__main__':
    unittest.main()