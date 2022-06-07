from __future__ import annotations

from gensim.models import KeyedVectors
import logging
from typing import Union, List, Tuple
import sys
from numpy import ndarray

from kgvec2go_server.generic.generic_linker import GenericLinker

# logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class GenericKvQueryService:
    """A class that can provide any backend service given a KV file."""

    def __init__(
        self,
        kv: KeyedVectors,
        linker: GenericLinker,
        dataset: str,
        dataset_version: str,
        model: str,
        model_version: str,
    ):
        """

        Parameters
        ----------
        kv : KeyedVectors
            Vectors.
        linker : GenericLinker
            Linker.
        dataset : str
            String representation of the embedded dataset (e.g. "DBpedia").
        dataset_version : str
            String representation of the version of the embedded dataset (e.g. "").
        model
        model_version
        """
        self.kv = kv
        self.linker = linker
        self.dataset = dataset
        self.dataset_version = dataset_version
        self.model = model
        self.model_version = model_version

    def get_vector(self, label: str) -> Union[Tuple[str, ndarray], None]:
        link: str = self.linker.link(label=label)
        if link is None:
            return None
        return link, self.kv[link]

    def get_vector_json(self, label: str) -> str:
        link_vector: Union[Tuple[str, ndarray], None] = self.get_vector(label=label)
        if link_vector is None:
            return "{}"
        result = f'{{ "uri": "{link_vector[0]}", "vector": {GenericKvQueryService.__to_json_array(vector=link_vector[1])}}}'
        return result

    def get_similarity(self, label_1: str, label_2: str) -> Union[float, None]:
        """Calculate the similarity between the two given concepts.

        Parameters
        ----------
        label_1 : str
            The first concept.

        label_2 : str
            The second concept

        Returns
        -------
        float
            Similarity. If no concepts can be found: None.
        """
        link_1 = self.linker.link(label=label_1)
        link_2 = self.linker.link(label=label_2)

        if link_1 is None or link_2 is None:
            return None
        return self.kv.similarity(w1=link_1, w2=link_2)

    def get_similarity_json(self, label_1: str, label_2: str) -> str:
        """Calculate the similarity between the two given concepts.

        Parameters
        ----------
        label_1 : str
            The first concept.

        label_2 : str
            The second concept

        Returns
        -------
        str
            Similarity as JSON.
        """
        similarity = self.get_similarity(label_1, label_2)
        if similarity is None:
            return "{}"
        else:
            return '{ "result" : ' + str(similarity) + " }"

    def get_closest_concepts(
        self, label: str, topn: int
    ) -> Union[None, List[Tuple[str, float]]]:
        """Get the closest concepts in a data structure.

        Parameters
        ----------
        label: str
            Concept label or URI.
        topn: int
            Number of closest concepts that shall be returned.

        Returns
        -------
        list of (str, float) or numpy.array
        """
        link: str = self.linker.link(label=label)
        if link is None:
            logging.error(f"No concept found for label `{label}`")
            return None

        return self.kv.most_similar(link, topn=topn)

    def get_closest_concepts_json(self, label: str, topn: int) -> str:
        """Get the closest concepts as JSON string.

        Parameters
        ----------
        label: str
            Concept label or URI.
        topn: int
            Number of closest concepts that shall be returned.

        Returns
        -------
        Result as JSON string.
        """
        return self.__closest_concepts_to_json(
            self.get_closest_concepts(label=label, topn=topn)
        )

    def most_similar_addition(
        self, label_1: str, label_2: str, topn: int
    ) -> Union[None, List[Tuple[str, float]]]:
        link_1: str = self.linker.link(label=label_1)
        link_2: str = self.linker.link(label=label_2)
        if link_1 is None or link_2 is None:
            return None

        l1_vector = self.kv.get_vector(key=link_1)
        l2_vector = self.kv.get_vector(key=link_2)
        lookup_vector = l1_vector + l2_vector

        return self.kv.most_similar(positive=[lookup_vector], topn=topn)

    def most_similar_addition_json(self, label_1: str, label_2: str, topn: int) -> str:
        return self.__closest_concepts_to_json(
            self.most_similar_addition(label_1=label_1, label_2=label_2, topn=topn)
        )

    @staticmethod
    def __closest_concepts_to_json(
        closest_concepts: Union[None, List[Tuple[str, float]]]
    ) -> str:
        if closest_concepts is None:
            return "{}"
        is_first = True
        result = '{\n"result": [\n'
        for concept, score in list(closest_concepts):
            if is_first:
                is_first = False
                result += (
                    '{ "concept":"' + str(concept) + '", "score":' + str(score) + "}"
                )
            else:
                result += (
                    ',\n{ "concept":"' + str(concept) + '", "score":' + str(score) + "}"
                )
        result += "\n]\n}"
        return result

    @staticmethod
    def __to_json_array(vector):
        result = ""
        is_first = True
        for element in vector:
            if is_first:
                is_first = False
                result += "[" + str(element)
            else:
                result += "," + str(element)
        return result + "]"

    @staticmethod
    def _normalize_for_list_search(
        name: str,
    ) -> str:
        """Normalization operation for searching/finding services in a list of services.

        Parameters
        ----------
        name : str
            String to be normalized.

        Returns
        -------
        Normalized string.
        """
        name = name.lower()
        name = name.replace("-", "")
        name = name.replace("_", "")
        name = name.replace(" ", "")
        return name

    @staticmethod
    def get_service_from_list(
        the_list: List[GenericKvQueryService],
        dataset: str,
        dataset_version: str,
        model: str,
        model_version: str,
    ) -> Union[None, GenericKvQueryService]:
        """Retrieves a service from a list given search criteria.

        Parameters
        ----------
        the_list : List[GenericKvQueryService]
            The list in which shall be searched.
        dataset : str
            The dataset name.
        dataset_version : str
            The dataset version.
        model : str
            The model name.
        model_version : str
            The model version.

        Returns
        -------
        None if no service could be found for the given concepts, else the found service.
        """
        for entry in the_list:
            if not GenericKvQueryService._normalize_for_list_search(
                name=entry.dataset
            ) == GenericKvQueryService._normalize_for_list_search(dataset):
                continue
            if not GenericKvQueryService._normalize_for_list_search(
                name=entry.dataset_version
            ) == GenericKvQueryService._normalize_for_list_search(dataset_version):
                continue
            if not GenericKvQueryService._normalize_for_list_search(
                name=entry.model
            ) == GenericKvQueryService._normalize_for_list_search(model):
                continue
            if not GenericKvQueryService._normalize_for_list_search(
                name=entry.model_version
            ) == GenericKvQueryService._normalize_for_list_search(model_version):
                continue
            return entry

        return None
