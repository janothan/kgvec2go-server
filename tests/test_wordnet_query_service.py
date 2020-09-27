from kgvec2go_server.wordnet.wordnet_query_service import WordnetQueryService as WQService


class TestWordnetQueryService:

    def test_transform_string(self):
        assert 'stabilizer' == WQService.transform_string('wn-lemma:stabilizer#stabilizer-n')
