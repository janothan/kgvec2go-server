from kgvec2go_server.dbpedia.dbpedia_query_service import (
    DBpediaQueryService as DBPService,
)


class TestDBpediaQueryService:
    def test_transform_string(self):
        assert "European_Union" == DBPService.transform_string(
            "http://dbpedia.org/resource/European_Union"
        )
        assert "European_Union" == DBPService.transform_string(
            "dbr:European_Union"
        )
