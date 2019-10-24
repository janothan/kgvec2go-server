import gensim
from collections import namedtuple


class DbnaryQueryService:
    """Query service for the dbnary data set.

    """

    def __init__(self, entity_file, model_file):
        self.all_lemmas = self.__read_lemmas(entity_file)
        self.model = gensim.models.Word2Vec.load(model_file)
        self.term_mapping = self.__map_terms(self.all_lemmas)

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

        string_to_be_transformed = string_to_be_transformed.replace("http://kaiko.getalp.org/dbnary/eng/", "")
        string_to_be_transformed = string_to_be_transformed.lower()
        string_to_be_transformed = string_to_be_transformed.strip(" ")
        string_to_be_transformed = string_to_be_transformed.replace(" ", "_")
        return string_to_be_transformed

    def __read_lemmas(self, path_to_lemma_file):
        result = []
        with open(path_to_lemma_file, errors='ignore') as lemma_file:
            for lemma in lemma_file:
                result.append(lemma.replace("\n", ""))
        print("Dbnary lemmas read.")
        return result

    def find_closest_lemmas_given_key(self, key, top):
        if key not in self.model.wv.vocab:
            return None
        result_list = []
        ResultEntry = namedtuple('ResultEntry', 'concept similarity')
        for concept in self.all_lemmas:
            result_list.append(ResultEntry(concept, self.model.wv.similarity(key, concept)))
        result_list.sort(key=self.__take_second, reverse=True)
        result_list = result_list[:int(top)]
        result = '{\n"result": [\n'
        is_first = True
        for entry in result_list:
            if is_first:
                is_first = False
                result += '{ "concept":"' + str(entry[0]) + '", "score":' + str(entry[1]) + "}"
            else:
                result += ',\n{ "concept":"' + str(entry[0]) + '", "score":' + str(entry[1]) + "}"
        result += "\n]\n}"
        return result

    def find_closest_lemmas(self, lemma, top):
        print("Closest lemma query for " + lemma + " received.")
        lookup_key = self.__transform_string(lemma)
        if lookup_key in self.term_mapping:
            return self.find_closest_lemmas_given_key(key=self.term_mapping[lookup_key], top=top)
        else:
            return "{}"

    def __take_second(self, element):
        """For sorting."""
        return element[1]

    def get_vector(self, lemma):
        lookup_key = self.__transform_string(lemma)
        if lookup_key in self.term_mapping:
            uri = self.term_mapping[lookup_key]
            vector = self.model.wv.get_vector(uri)
            return '{ "uri": "' + uri + '",\n"vector": ' + self.__to_json_arry(vector) + '}'
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
                result += ',' + str(element)
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
        a = self.term_mapping[lookup_key_1]
        b = self.term_mapping[lookup_key_2]
        if lookup_key_1 in self.term_mapping and lookup_key_2 in self.term_mapping:
            return self.model.wv.similarity(self.term_mapping[lookup_key_1], self.term_mapping[lookup_key_2])
        else:
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




def main():
    print("Start")
    service = DbnaryQueryService(entity_file="./dbnary_500_8_pages/dbnary_entities.txt",
                                 model_file="./dbnary_500_8_pages/sg200_dbnary_500_8_pages")
    # print(service.find_closest_lemmas_given_key('http://kaiko.getalp.org/dbnary/eng/famous', 10))
    # print(service.find_closest_lemmas('famous', 10))
    # print(service.find_closest_lemmas('dog', 10))
    # print(service.find_closest_lemmas('swap', 10))
    # print(service.find_closest_lemmas('random_bla_balc_asdef', 10))
    #print(service.find_closest_lemmas('World Wide WEb', 10))
    print(service.get_vector("professor"))
    #print("End")


if __name__ == "__main__":
    main()