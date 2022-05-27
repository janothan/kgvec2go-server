import pytest
from gensim.models import KeyedVectors

from kgvec2go_server.generic.generic_linker import GenericDBpediaLinker
from kgvec2go_server.generic.generic_query_service import GenericKvQueryService

kv: KeyedVectors
linker: GenericDBpediaLinker
qs: GenericKvQueryService


def setup_module(module):
    global kv
    global linker
    global qs
    kv = KeyedVectors.load("./tests/data/dbpedia_sample_vectors.kv", mmap="r")
    linker = GenericDBpediaLinker(kv=kv)
    qs = GenericKvQueryService(kv=kv, linker=linker)


def test_get_vector():
    result = qs.get_vector(label="Hotel")
    assert result != None
    assert len(result[1]) == 200
    assert result[1][0] == pytest.approx(1.8226044)


def test_get_vector_json():
    result = qs.get_vector_json(label="Hotel")
    assert result != "{}"

    result = qs.get_vector_json(label="Does Not Exist")
    assert result == "{}"


def test_get_similarity():
    assert True


def test_get_similarity_json():
    assert True
