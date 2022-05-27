from abc import ABC
from typing import Union
from gensim.models import KeyedVectors


class GenericLinker(ABC):
    def link(self, label: str) -> Union[None, str]:
        pass


class GenericDBpediaLinker(GenericLinker):
    def __init__(self, kv: KeyedVectors):
        self.kv = kv

    def link(self, label: str) -> Union[None, str]:
        if label is None:
            return None

        if label in self.kv.key_to_index:
            return label

        # fallback: replace space
        if " " in label:
            label = label.replace(" ", "_")

        if label in self.kv.key_to_index:
            return label

        # fallback: add DBpedia URI
        likely_correct_label = label
        label = "http://dbpedia.org/resource/" + likely_correct_label

        if label in self.kv.key_to_index:
            return label

        label = "http://dbpedia.org/ontology/" + likely_correct_label

        if label in self.kv.key_to_index:
            return label

        return None
