import gensim
from gensim.models import KeyedVectors
from collections import namedtuple


class DBpediaQueryService:

    def __init__(self, entity_file, model_file='', vector_file=''):
        if vector_file != '':
            self.vectors = KeyedVectors.load(vector_file, mmap=None)
        elif model_file != '':
            self.model = gensim.models.Word2Vec.load(model_file)
            self.vectors = self.model.wv
        else:
            print("ERROR - a model or vector file needs to be specified.")

        # reading the instances
        self.all_lemmas = self.__read_lemmas(entity_file)

        # term mapping example entry: sleep -> {bn:sleep_n_EN, bn:sleep_v_EN, bn:Sleep_n_EN}
        self.term_mapping = self.__map_terms(self.all_lemmas)

        print("Examples from DBpedia vocabulary")
        iteration = 0
        for word in self.vectors.vocab:
            print(word.encode('utf-8'))
            iteration += 1
            if iteration > 100:
                break

    def __read_lemmas(self, entity_file_path):
        result = []
        number_of_key_errors = 0
        with open(entity_file_path, errors='ignore') as lemma_file:
            for lemma in lemma_file:
                lemma = lemma.replace("\n", "")
                if lemma not in self.vectors.vocab:
                    print("Could not find DBpedia concept: " + lemma)
                    number_of_key_errors += 1
                else:
                    result.append(lemma.replace("\n", "").replace("\r", ""))
        print("DBpedia lemmas read.")
        print("Number of key errors " + str(number_of_key_errors))
        return result

    def __map_terms(self, all_lemmas):
        result = {}
        for uri in all_lemmas:
            lookup_key = self.__transform_string(uri)
            result[lookup_key] = uri
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
        string_to_be_transformed = string_to_be_transformed.replace("dbr:", "")
        string_to_be_transformed = string_to_be_transformed.strip(" ")
        string_to_be_transformed = string_to_be_transformed.replace(" ", "_")
        string_to_be_transformed = string_to_be_transformed.replace("'", "_")
        string_to_be_transformed = string_to_be_transformed.replace("-", "_")
        string_to_be_transformed = string_to_be_transformed.replace(".", "")
        return string_to_be_transformed

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

        #try:
        #    mapping_1 = self.term_mapping[lookup_key_1]
        #    mapping_2 = self.term_mapping[lookup_key_2]
        #    print(concept_1 + " mapped to " + str(mapping_1))
        #    print(concept_2 + " mapped to " + str(mapping_2))
        #except KeyError:
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
            similarity = self.vectors.similarity(self.term_mapping[lookup_key_1], self.term_mapping[lookup_key_2])
            #print("sim(" + concept_1 + ", " + concept_2 + ") = " + str(similarity))
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


    def find_closest_lemmas(self, lemma, top):
        print("Closest lemma query for " + lemma + " received.")
        lookup_key = self.__transform_string(lemma)
        print("Transformed to " + lookup_key)
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
            vector = self.vectors.get_vector(uri)
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

    def find_closest_lemmas_given_key(self, key, top):
        if key not in self.vectors.vocab:
            return None
        result_list = []
        ResultEntry = namedtuple('ResultEntry', 'concept similarity')
        for concept in self.all_lemmas:
            result_list.append(ResultEntry(concept, self.vectors.similarity(key, concept)))
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