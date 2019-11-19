import gensim
import re

import logging
from gensim.models import KeyedVectors
from collections import namedtuple


class AlodQueryService:

    def __init__(self, model_file='', vector_file=''):
        if model_file == '' and vector_file == '':
                logging.error("ERROR - At least one file must be given.")
        elif model_file != '':
            print("Load alod classic model.")
            self.model = gensim.models.Word2Vec.load(model_file)
            #print("Write vector file.")
            #vector_file = get_tmpfile(self.__get_file_name(model_file))
            #print("Writing vector file: " + str(vector_file))
            #self.model.wv.save(vector_file)
            self.word_vectors = self.model.wv
        elif vector_file != '':
            self.word_vectors = KeyedVectors.load(vector_file, mmap='r')

        self.all_lemmas = self.__read_lemmas()

        # cache for closests concepts
        self.closest_concepts_cache = {}



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

        string_to_be_transformed = string_to_be_transformed.lower()
        string_to_be_transformed = string_to_be_transformed.strip(" ")
        string_to_be_transformed = string_to_be_transformed.replace(" ", "_")
        string_to_be_transformed = string_to_be_transformed.replace("'", "_")
        string_to_be_transformed = string_to_be_transformed.replace("-", "_")
        return string_to_be_transformed

    def __read_lemmas(self):
        result = {}
        for entry in self.word_vectors.vocab:
            result[self.__transform_string(entry)] = entry
        print("ALOD Classic lemmas read.")
        return result

    def find_closest_lemmas_given_key(self, key, top):

        if key not in self.word_vectors.vocab:
            return None


        result = '{\n"result": [\n'
        is_first = True
        for entry, similarity in self.word_vectors.most_similar(key, topn=int(top)):
            if is_first:
                is_first = False
                result += '{ "concept":"' + str(entry) + '", "score":' + str(similarity) + "}"
            else:
                result += ',\n{ "concept":"' + str(entry) + '", "score":' + str(similarity) + "}"
        result += "\n]\n}"
        return result

        # old

        #if key not in self.word_vectors.vocab:
        #    return None
        #result_list = []
        #ResultEntry = namedtuple('ResultEntry', 'concept similarity')
        #for concept in self.all_lemmas:
        #    result_list.append(ResultEntry(concept, self.word_vectors.similarity(key, self.all_lemmas[concept])))
        #result_list.sort(key=self.__take_second, reverse=True)
        #result_list = result_list[:int(top)]
        #result = '{\n"result": [\n'
        #is_first = True
        #for entry in result_list:
        #    if is_first:
        #        is_first = False
        #        result += '{ "concept":"' + str(entry[0]) + '", "score":' + str(entry[1]) + "}"
        #    else:
        #        result += ',\n{ "concept":"' + str(entry[0]) + '", "score":' + str(entry[1]) + "}"
        #result += "\n]\n}"
        #return result

    def find_closest_lemmas(self, lemma, top):
        print("Closest lemma query for " + lemma + " received.")
        lookup_key = self.__transform_string(lemma)

        if lookup_key in self.closest_concepts_cache:
            print("Serve answer from cache.")
            return self.closest_concepts_cache[lookup_key]

        result = "{}"
        if lookup_key in self.all_lemmas:
            result = self.find_closest_lemmas_given_key(key=self.all_lemmas[lookup_key], top=top)

        self.closest_concepts_cache[lookup_key] = result
        return result

    def __take_second(self, element):
        """For sorting."""
        return element[1]

    def get_vector(self, lemma):
        lookup_key = self.__transform_string(lemma)
        if lookup_key in self.all_lemmas:
            uri = self.all_lemmas[lookup_key]
            vector = self.word_vectors.get_vector(uri)
            return '{ "uri": "' + uri + '",\n"vector": ' + self.__to_json_arry(vector) + '}'
        else:
            return "{}"

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
        if lookup_key_1 in self.all_lemmas and lookup_key_2 in self.all_lemmas:
            return self.word_vectors.similarity(lookup_key_1, lookup_key_2)
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

    def __get_file_name(self, file_path):
        return re.search("(?<=\/)[^\/]*$", file_path).group(0)

    def __str__(self):
        return "ALOD Query Service"

def main():
    print("Start")
    service = AlodQueryService(vector_file="./alod_500_4/sg200_alod_500_4")
    #print(service.get_vector('sleep'))
    #print(service.find_closest_lemmas('sleep', 10))
    print(service.get_similarity("car", "amex"))
    print(service.get_similarity("truck", "car"))
    print(service.get_similarity("car", "vacation"))
    print("End")



if __name__ == "__main__":
    main()