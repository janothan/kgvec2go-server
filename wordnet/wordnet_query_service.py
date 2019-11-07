import gensim
import re
from collections import namedtuple


class WordnetQueryService:

    def __init__(self, entity_file, model_file):
        self.all_lemmas = self.__read_lemmas(entity_file)
        self.model = gensim.models.Word2Vec.load(model_file)
        self.term_mapping = self.__map_terms(self.all_lemmas)

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

        string_to_be_transformed = string_to_be_transformed.replace("wn-lemma:", "")
        #string_to_be_transformed = string_to_be_transformed.lower()
        string_to_be_transformed = string_to_be_transformed.strip(" ")
        string_to_be_transformed = re.sub(pattern='#.*$', repl="", string=string_to_be_transformed)
        return string_to_be_transformed


    def __map_terms(self, all_lemmas):
        result = {}
        for uri in all_lemmas:
            lookup_key = self.transform_string(uri)
            if lookup_key in result:
                result[lookup_key].append(uri)
            else:
                result[lookup_key] = [uri]
        return result

    def __read_lemmas(self, path_to_lemma_file):
        result = []
        with open(path_to_lemma_file, errors='ignore') as lemma_file:
            for lemma in lemma_file:
                result.append(lemma.replace("\n", ""))
        print("WordNet lemmas read.")
        return result

    def find_closest_lemmas_given_key(self, key, top):
        if key not in self.model.wv.vocab:
            return None
        ResultEntry = namedtuple('ResultEntry', 'concept similarity')
        result_list = []
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
        """The wordnet data set is structured according to word fuction (noun, verb etc.). Here, the results are
        merged (e.g. for 'sleep' the lemmas 'sleep-n' and 'sleep-v' are merged.

        Returns
        -------
        str
            Result list in JSON."""

        print("Query for " + lemma + " received.")
        lookup_key = self.transform_string(lemma)
        if lookup_key in self.term_mapping:
            result_list = []
            for concept in self.all_lemmas:
                temp_result_list = []
                for uri in self.term_mapping[lookup_key]:
                    temp_result_list.append((concept, self.model.wv.similarity(uri, concept)))
                temp_result_list.sort(key=self.__take_second, reverse=True)
                result_list.append(temp_result_list[0])
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
        else:
            return "{}"

    def __take_second(self, element):
        """For sorting."""
        return element[1]

    def get_vector(self, lemma):
        lookup_key = self.transform_string(lemma)
        result = '{ "result": ['
        is_first = True
        if lookup_key in self.term_mapping:
            for key in self.term_mapping[lookup_key]:
                vector = self.model.wv.get_vector(key)
                if is_first:
                    is_first = False
                    result += '{"uri": ' + '"' + key + '",\n"vector": ' + self.__to_json_arry(vector) + '}'
                else:
                    result += ',\n{"uri": ' + '"' + key + '",\n"vector": ' + self.__to_json_arry(vector) + '}'
            return result + '] }'
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


    def get_similarity(self, concept_1, concept_2, pos_1='N', pos_2='N'):
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
        lookup_key_1 = self.transform_string(concept_1)
        lookup_key_2 = self.transform_string(concept_2)
        if lookup_key_1 in self.term_mapping and lookup_key_2 in self.term_mapping:
            # always pick the noun if there are multiple matches
            vector_1 = self.__pick_pos_vector(self.term_mapping[lookup_key_1], pos=pos_1)
            vector_2 = self.__pick_pos_vector(self.term_mapping[lookup_key_1], pos=pos_2)
            return self.model.wv.similarity(vector_1, vector_2)
        else:
            return None

    def __pick_pos_vector(self, vectors, pos='n'):
        """Pick the vector out of the set of given vectors. If no vector from the given POS can be found, the first
           vector of the given set of vectors is returned.

            Parameters
            ----------
            vectors : list
                The set of vectors.
            pos : basestring
                Default: Noun (n). The vector to be preferred.

             Returns
             -------
             list
                The resulting vector.
        """
        pos = pos.lower()
        if pos not in ["j", "v", "n", "r", "a"]:
            print("POS not in [j,v,n,r,a] (given: " + pos + "). Using fall-back: n.")
            pos = "n"
        for vector in vectors:
            if vector.endswith("-" + pos):
                return vector
        return vectors[0]

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
    service = WordnetQueryService(entity_file='./wordnet_500_8/wordnet_entities.txt',
                                         model_file='./wordnet_500_8/sg200_wordnet_500_8')
    # print(service.find_closest_lemmas_given_key('http://kaiko.getalp.org/dbnary/eng/famous', 10))
    # print(service.find_closest_lemmas('famous', 10))
    # print(service.find_closest_lemmas('dog', 10))
    # print(service.find_closest_lemmas('swap', 10))
    # print(service.find_closest_lemmas('random_bla_balc_asdef', 10))
    print(service.get_vector('sleep'))
    print(service.find_closest_lemmas('sleep', 10))
    print("End")

if __name__ == "__main__":
    main()