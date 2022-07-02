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
    qs = GenericKvQueryService(
        kv=kv,
        linker=linker,
        dataset="TD",
        dataset_version="TDV",
        model="TM",
        model_version="TMV",
    )


def test_get_service_from_list():
    my_list = [qs]
    assert (
        GenericKvQueryService.get_service_from_list(
            my_list,
            dataset="td",
            dataset_version="td-v",
            model="tm",
            model_version="tmv",
        )
        is not None
    )


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
    result = qs.get_similarity(label_1="Hotel", label_2="Aero East Europe")
    assert result is not None


def test_get_similarity_json():
    assert True


def get_triple_score():
    result = qs.get_triple_score(
        subject_label="Hotel", predicate_label="Aero East Europe", object_label="Lake"
    )
    assert result is not None
