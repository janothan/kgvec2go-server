import gensim
import re
from gensim.test.utils import get_tmpfile
from gensim.models import KeyedVectors
from collections import namedtuple


class BabelNetQueryService:
    def __init__(self, entity_file, model_file="", vector_file=""):

        self.all_lemmas = self.__read_lemmas(entity_file)

        # term mapping example entry: sleep -> {bn:sleep_n_EN, bn:sleep_v_EN, bn:Sleep_n_EN}
        self.term_mapping = self.__map_terms(self.all_lemmas)

        if model_file == "" and vector_file == "":
            print("ERROR - At least one file must be given.")
        elif model_file != "":
            print("Load BabelNet model.")
            self.model = gensim.models.Word2Vec.load(model_file)
            # vector_file = get_tmpfile(self.__get_file_name(model_file))
            if vector_file != "":
                print("Writing vector file: " + str(vector_file))
                self.model.wv.save(vector_file)
            self.word_vectors = self.model.wv
        elif vector_file != "":
            try:
                vector_file_path = get_tmpfile(self.__get_file_name(vector_file))
                self.word_vectors = KeyedVectors.load(vector_file_path, mmap="r")
            except FileNotFoundError:
                vector_file_path = vector_file
                self.word_vectors = KeyedVectors.load(vector_file_path, mmap="r")

    def __map_terms(self, all_lemmas):
        result = {}
        for uri in all_lemmas:
            lookup_key = self.transform_string(uri)
            if lookup_key in result:
                result[lookup_key].add(uri)
            else:
                result[lookup_key] = {uri}
        print("Term mapping created. Size: " + str(len(result)))
        print("Example:")
        iteration_number = 0
        for k, v in result.items():
            iteration_number += 1
            print("Key: " + k)
            for value in v:
                print("Value for " + k + ": " + value)
            if iteration_number > 10:
                break
        print("End of example.")
        return result

    def get_lookup_key(self, search_term, pos="n"):
        """
        Best effort: If there is no vector for the given POS but a string match with another POS,
        that vector will be returned. Mini test case:

        print(self.get_lookup_key("sleep", pos='n')) # bn:sleep_n_EN
        print(self.get_lookup_key("sleep", pos='v')) # bn:sleep_v_EN
        print(self.get_lookup_key("Sleep", pos='n')) # bn:Sleep_n_EN
        print(self.get_lookup_key("Sleep")) # bn:Sleep_n_EN
        print(self.get_lookup_key("sleep")) # bn:sleep_n_EN

        Parameters
        ----------
        search_term
        pos

        Returns
        -------

        """
        lookup_key = self.transform_string(search_term)
        pos = pos.lower()
        result = None
        if lookup_key not in self.term_mapping:
            # cannot be mapepd
            return None
        set_to_pick_from = self.term_mapping.get(lookup_key)

        # check for exact match
        for candidate in set_to_pick_from:
            if search_term in candidate and ("_" + pos + "_EN") in candidate:
                return candidate

        # exact match not found, return first POS match
        for candidate in set_to_pick_from:
            if ("_" + pos + "_EN") in candidate:
                return candidate

        # pos not found, try noun
        if pos != "n":
            pos = "n"
            for candidate in set_to_pick_from:
                if ("_" + pos + "_EN") in candidate:
                    return candidate

        # no POS match, no exact match, return any
        return tuple(set_to_pick_from)[0]

    @staticmethod
    def transform_string(string_to_be_transformed):
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

        # string_to_be_transformed = string_to_be_transformed.lower()
        string_to_be_transformed = string_to_be_transformed.lstrip("bn:")
        string_to_be_transformed = re.sub(
            "_[a-zA-Z]{1}_(en|EN)$", "", string_to_be_transformed
        )
        string_to_be_transformed = string_to_be_transformed.strip(" ")
        string_to_be_transformed = string_to_be_transformed.replace(" ", "_")
        string_to_be_transformed = string_to_be_transformed.replace("'", "_")
        string_to_be_transformed = string_to_be_transformed.replace("-", "_")
        return string_to_be_transformed

    def __read_lemmas(self, path_to_lemma_file):
        result = []
        with open(path_to_lemma_file, errors="ignore") as lemma_file:
            for lemma in lemma_file:
                result.append(lemma.replace("\n", "").replace("\r", ""))
        print("BabelNet lemmas read.")
        return result

    def find_closest_lemmas_given_key(self, key, top):
        if key not in self.word_vectors.vocab:
            return None
        result_list = []
        ResultEntry = namedtuple("ResultEntry", "concept similarity")
        for concept in self.all_lemmas:
            result_list.append(
                ResultEntry(
                    concept, self.word_vectors.similarity(key, self.all_lemmas[concept])
                )
            )
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
        lookup_key = self.transform_string(lemma)
        if lookup_key in self.all_lemmas:
            return self.find_closest_lemmas_given_key(
                key=self.all_lemmas[lookup_key], top=top
            )
        else:
            return "{}"

    def __take_second(self, element):
        """For sorting."""
        return element[1]

    def get_vector_json(self, lemma, pos="n"):
        vector = self.get_lookup_key(lemma, pos)
        if vector is None:
            return "{}"
        return (
            '{ "uri": "'
            + vector
            + '",\n"vector": '
            + self.__to_json_array(vector)
            + "}"
        )

    def get_similarity(self, concept_1, concept_2, pos):
        return self.get_similarity(concept_1, concept_2, pos, pos)

    def get_similarity(
        self, concept_1: str, concept_2: str, pos_1: str = "n", pos_2: str = "n"
    ) -> float:
        """Calculate the similarity between the two given concepts.

        Parameters
        ----------
        concept_1 : str
            The first concept.

        concept_2 : str
            The second concept

        pos_1 : str
            The POS of concept_1.

        pos_2 : str
            The POS of concept_2.

        Returns
        -------
        float
            Similarity. If no concepts can be found: None.
        """
        lookup_key_1 = self.get_lookup_key(concept_1, pos_1)
        lookup_key_2 = self.get_lookup_key(concept_2, pos_2)
        if lookup_key_1 is None:
            print(
                "[babelnet_query_service#get_similarity] Concept '"
                + concept_1
                + "' could not be found."
            )
            return None
        if lookup_key_2 is None:
            print(
                "[babelnet_query_service#get_similarity] Concept '"
                + concept_2
                + "' could not be found."
            )
            return None
        try:
            print("Find similarity for:")
            print(lookup_key_1)
            print(lookup_key_2)
            similarity = self.word_vectors.similarity(lookup_key_1, lookup_key_2)
            print("Similarity = " + str(similarity))
            return similarity
        except KeyError:
            print(
                "A key error occurred for tuple: ("
                + concept_1
                + " | "
                + concept_2
                + ")"
            )
            print("Lookup key 1: " + lookup_key_1)
            print("Lookup key 2: " + lookup_key_2)
            return None

    def get_similarity_json(
        self, concept_1: str, concept_2: str, pos_1: str = "n", pos_2: str = "n"
    ):
        """Calculate the similarity between the two given concepts.

        Parameters
        ----------
        concept_1 : str
            The first concept.

        concept_2 : str
            The second concept.

         pos_1 : str
             The POS of concept_1.

         pos_2 : str
             The POS of concept_2.

        Returns
        -------
        float
            Similarity as JSON.
        """
        similarity = self.get_similarity(concept_1, concept_2, pos_1=pos_1, pos_2=pos_2)
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

    @staticmethod
    def __get_file_name(file_path):
        return re.search(r"(?<=\/)[^\/]*$", file_path).group(0)


def main():
    print("Start")
    print(BabelNetQueryService.transform_string("Gold_smith_n_EN"))
    # service = BabelNetQueryService(vector_file="./sg200_babelnet_100_8_vectors", entity_file="./babelnet_entities_en.txt")
    # print(service.get_vector('sleep'))
    # print(service.find_closest_lemmas('sleep', 10))
    # print(service.get_similarity("car", "amex"))
    # print(service.get_similarity("truck", "car"))
    # print(service.get_similarity("car", "vacation"))

    print("End")


if __name__ == "__main__":
    main()
