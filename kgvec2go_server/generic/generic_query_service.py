from gensim.models import KeyedVectors
from pathlib import Path
import logging
from typing import Union

from kgvec2go_server.generic.generic_linker import GenericLinker


class GenericKvQueryService:
    """A class that can provide any backend service given a KV file.
    """

    def __init__(
            self, kv: KeyedVectors, linker: GenericLinker
    ):
        #logging.info(f"Loading kv file {kv_path}")
        #self.kv: KeyedVectors = KeyedVectors.load(kv_path, mmap='r')
        self.kv = kv
        self.linker = linker

    def get_vector_json(self, label: str) -> str:
        link: str = self.linker.link(label=label)
        if link is None:
            return "{}"
        vector = self.kv[link]
        result = f'{{ "uri": "{link}", "vector": {GenericKvQueryService.__to_json_array(vector=vector)}}}'
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
