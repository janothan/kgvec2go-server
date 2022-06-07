import gensim
from collections import namedtuple
from gensim.models import KeyedVectors
from typing import Union


class DbnaryQueryService:
    """Query service for the dbnary data set."""

    def __init__(
        self,
        entity_file="",
        model_file="",
        vector_file="",
        is_reduced_vector_file=False,
    ):
        """

        Parameters
        ----------
        entity_file
            File to the entities.
        model_file
            The model file. If used, the vector_file is not required.
        vector_file
            The vector file. If used, the model_file is not required.
        is_reduced_vector_file
            True if unnecessary have already been removed from the vector space (using vector_shrinker.py).
        """
        if vector_file == "":
            self.model = gensim.models.Word2Vec.load(model_file)
            self.vectors = self.model.wv
        else:
            self.vectors = KeyedVectors.load(vector_file, mmap="r")

        self.is_reduced_vector_file = is_reduced_vector_file
        self.all_lemmas = self.__read_lemmas(entity_file)
        self.term_mapping = self.__map_terms(self.all_lemmas)

        # cache for UI
        self.closest_concepts_cache = {}

    def __map_terms(self, all_lemmas):
        result = {}
        for uri in all_lemmas:
            result[self.__transform_string(uri)] = uri
        return result

    def __transform_string(self, string_to_be_transformed):
        """Transforms any string for lookup, also URIs.

        Parameters
        ----------
        string_to_be_transformed : str
            The string that shall be transformed.

        Returns
        -------
        str
            Transformed string.
        """

        string_to_be_transformed = string_to_be_transformed.replace(
            "http://kaiko.getalp.org/dbnary/eng/", ""
        )
        # string_to_be_transformed = string_to_be_transformed.lower()
        string_to_be_transformed = string_to_be_transformed.strip(" ")
        string_to_be_transformed = string_to_be_transformed.replace(" ", "_")
        return string_to_be_transformed

    def __read_lemmas(self, path_to_lemma_file):
        if self.is_reduced_vector_file:
            return self.vectors
        else:
            result = []
            number_of_vocab_errors = 0
            with open(path_to_lemma_file, errors="ignore") as lemma_file:
                for lemma in lemma_file:
                    lemma = lemma.replace("\n", "").replace("\r", "")
                    if lemma not in self.vectors:
                        print(
                            "The follwing lemma was not found in the vocabulary: "
                            + str(lemma.encode(encoding="utf-8"))
                        )
                        number_of_vocab_errors += 1
                    else:
                        result.append(lemma)
                    # if lemma not in self.vectors.vocab:
                    #    print(lemma + " not in vocabulary.")
            print("Dbnary lemmas read.")
            print("Number of vocabulary errors: " + str(number_of_vocab_errors))
            return result

    def find_closest_lemmas_given_key(self, key, top) -> Union[None, str]:
        if key not in self.vectors:
            return None
        if self.is_reduced_vector_file:
            result_list = self.vectors.most_similar(positive=key, topn=top)
        else:
            result_list = []
            ResultEntry = namedtuple("ResultEntry", "concept similarity")
            not_found_error = 0
            for concept in self.all_lemmas:
                try:
                    similarity = self.vectors.similarity(key, concept)
                    result_list.append(ResultEntry(concept, similarity))
                except KeyError:
                    print("Word " + concept + " not found. Continue...")
                    not_found_error += 1
            print("Not found keys: " + str(not_found_error))
            result_list.sort(key=self.__take_second, reverse=True)
            result_list = result_list[: int(top)]
        result = '{\n"result": [\n'
        is_first = True
        for entry in result_list:
            if is_first:
                is_first = False
                result += (
                    '{ "concept":"'
                    + str(entry[0])
                    + '", "score":'
                    + str(entry[1])
                    + "}"
                )
            else:
                result += (
                    ',\n{ "concept":"'
                    + str(entry[0])
                    + '", "score":'
                    + str(entry[1])
                    + "}"
                )
        result += "\n]\n}"
        return result

    def find_closest_lemmas(self, lemma, top):
        print("Closest lemma query for " + lemma + " received.")
        lookup_key = self.__transform_string(lemma)

        if lookup_key in self.closest_concepts_cache:
            print("Serve answer from cache.")
            return self.closest_concepts_cache[lookup_key]

        result = "{}"
        if lookup_key in self.term_mapping:
            result = self.find_closest_lemmas_given_key(
                key=self.term_mapping[lookup_key], top=top
            )

        self.closest_concepts_cache[lookup_key] = result
        return result

    def __take_second(self, element):
        """For sorting."""
        return element[1]

    def get_vector(self, lemma):
        lookup_key = self.__transform_string(lemma)
        if lookup_key in self.term_mapping:
            uri = self.term_mapping[lookup_key]
            vector = self.vectors.get_vector(uri)
            return (
                '{ "uri": "'
                + uri
                + '",\n"vector": '
                + self.__to_json_arry(vector)
                + "}"
            )
        else:
            return "{}"

    def __to_json_arry(self, vector):
        result = ""
        is_first = True
        for element in vector:
            if is_first:
                is_first = False
                result += "[" + str(element)
            else:
                result += "," + str(element)
        return result + "]"

    def get_similarity(self, concept_1, concept_2):
        """Calculate the similarity between the two given concepts.

        Parameters
        ----------
        concept_1 : str
            The first concept.

        concept_2 : str
            The second concept

        Returns
        -------
        float
            Similarity. If no concepts can be found: None.
        """
        lookup_key_1 = self.__transform_string(concept_1)
        lookup_key_2 = self.__transform_string(concept_2)

        # try:
        #    mapping_1 = self.term_mapping[lookup_key_1]
        #    mapping_2 = self.term_mapping[lookup_key_2]
        #    print(concept_1 + " mapped to " + str(mapping_1))
        #    print(concept_2 + " mapped to " + str(mapping_2))
        # except KeyError:
        #    #not important, just logging
        #    pass

        if lookup_key_1 not in self.term_mapping:
            if lookup_key_1[0].islower():
                print("Could not find " + lookup_key_1)
                lookup_key_1 = lookup_key_1[0].upper() + lookup_key_1[1:]
                print("Trying " + lookup_key_1)
                if lookup_key_1 not in self.term_mapping:
                    print("Coud not find " + concept_1)
                    return None

        if lookup_key_2 not in self.term_mapping:
            if lookup_key_2[0].islower():
                print("Could not find " + lookup_key_2)
                lookup_key_2 = lookup_key_2[0].upper() + lookup_key_2[1:]
                print("Trying " + lookup_key_2)
                if lookup_key_2 not in self.term_mapping:
                    print("Coud not find " + concept_2)
                    return None

        try:
            similarity = self.vectors.similarity(
                self.term_mapping[lookup_key_1], self.term_mapping[lookup_key_2]
            )
            # print("sim(" + concept_1 + ", " + concept_2 + ") = " + str(similarity))
            return similarity
        except KeyError:
            print("KeyError: One of the following concepts not found in vocabulary.")
            print("\t " + str(self.term_mapping[lookup_key_1]))
            print("\t " + str(self.term_mapping[lookup_key_2]))
            return None

    def get_similarity_json(self, concept_1, concept_2):
        """Calculate the similarity between the two given concepts.

        Parameters
        ----------
        concept_1 : str
            The first concept.

        concept_2 : str
            The second concept

        Returns
        -------
        float
            Similarity as JSON.
        """
        similarity = self.get_similarity(concept_1, concept_2)
        if similarity is None:
            return "{}"
        else:
            return '{ "result" : ' + str(similarity) + " }"

    def __str__(self):
        return "DBnary/Wiktionary Query Service"


def main():
    print("Start")
    service = DbnaryQueryService(
        entity_file="./dbnary_500_8_pages/dbnary_entities.txt",
        model_file="./dbnary_500_8_pages/sg200_dbnary_500_8_pages",
    )
    # print(service.find_closest_lemmas_given_key('http://kaiko.getalp.org/dbnary/eng/famous', 10))
    # print(service.find_closest_lemmas('famous', 10))
    # print(service.find_closest_lemmas('dog', 10))
    # print(service.find_closest_lemmas('swap', 10))
    # print(service.find_closest_lemmas('random_bla_balc_asdef', 10))
    # print(service.find_closest_lemmas('World Wide WEb', 10))
    print(service.get_vector("professor"))
    # print("End")


if __name__ == "__main__":
    main()
