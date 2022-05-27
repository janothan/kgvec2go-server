from gensim.models import KeyedVectors
from pathlib import Path
import logging
from typing import Union, List, Tuple

from numpy import ndarray

from kgvec2go_server.generic.generic_linker import GenericLinker


class GenericKvQueryService:
    """A class that can provide any backend service given a KV file."""

    def __init__(self, kv: KeyedVectors, linker: GenericLinker):
        self.kv = kv
        self.linker = linker

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
