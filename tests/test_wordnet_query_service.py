from wordnet.wordnet_query_service import WordnetQueryService as wqs


class TestWordnetQueryService:

    def test_transform_string(self):
        assert 'stabilizer' == wqs.transform_string('wn-lemma:stabilizer#stabilizer-n')
