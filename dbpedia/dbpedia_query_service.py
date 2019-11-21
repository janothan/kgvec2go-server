import gensim
from gensim.models import KeyedVectors
from collections import namedtuple
import logging


class DBpediaQueryService:

    def __init__(self, entity_file, model_file='', vector_file='', redirect_file=''):
        if vector_file != '':
            self.vectors = KeyedVectors.load(vector_file, mmap=None)
        elif model_file != '':
            self.model = gensim.models.Word2Vec.load(model_file)
            self.vectors = self.model.wv
        else:
            print("ERROR - a model or vector file needs to be specified.")

        self.all_lemmas = []
        self.redirects = {}
        if redirect_file != '':
            logging.info("Pasing redirects...")
            self.redirects = self.__parse_redirects(redirect_file)

        # reading the instances
        self.all_lemmas = self.__read_lemmas(entity_file)

        # term mapping example entry: sleep -> {bn:sleep_n_EN, bn:sleep_v_EN, bn:Sleep_n_EN}
        self.term_mapping = self.__map_terms(self.all_lemmas, self.redirects)

        self.closest_concepts_cache = {}

        print("Examples from DBpedia vocabulary")
        iteration = 0
        for word in self.vectors.vocab:
            print(str(word.encode('utf-8')))
            iteration += 1
            if iteration > 100:
                break

    def __read_lemmas(self, entity_file_path):
        result = set()
        number_of_key_errors = 0
        number_of_redirects = 0
        with open(entity_file_path, errors='ignore') as lemma_file:
            for lemma in lemma_file:
                lemma = lemma.replace("\n", "")
                if lemma not in self.vectors.vocab:
                    if lemma not in self.redirects:
                        # print("Could not find DBpedia concept: " + lemma)
                        number_of_key_errors += 1
                    else:
                        number_of_redirects += 1
                else:
                    result.add(lemma.replace("\n", "").replace("\r", ""))
        print("DBpedia lemmas read.")
        print("Number of key errors " + str(number_of_key_errors))
        print("Number of redirects " + str(number_of_redirects))
        return result

    def __map_terms(self, all_lemmas, redirects):
        result = {}
        for uri in all_lemmas:
            lookup_key = self.__transform_string(uri)
            result[lookup_key] = uri
        for uri in redirects:
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

        lookup_key_1 = self.term_mapping[lookup_key_1]
        lookup_key_2 = self.term_mapping[lookup_key_2]

        try:
            # handling redirects
            if lookup_key_1 not in self.vectors.vocab:
                print("Lookup Key 1 (" + lookup_key_1 + ") not in vocabulary. Check redirects.")
                lookup_key_1 = self.redirects[lookup_key_1]
                print("Lookup Key 1 redirects to: " + str(lookup_key_1.encode(encoding="utf-8")))
            if lookup_key_2 not in self.vectors.vocab:
                print("Lookup Key 2 (" + lookup_key_2 + ") not in vocabulary. Check redirects.")
                lookup_key_2 = self.redirects[lookup_key_2]
                print("Lookup Key 2 redirects to: " + str(lookup_key_2.encode(encoding="utf-8")))

            similarity = self.vectors.similarity(lookup_key_1, lookup_key_2)
            #print("sim(" + concept_1 + ", " + concept_2 + ") = " + str(similarity))
            return similarity
        except KeyError:
            print("KeyError: One of the following concepts not found in vocabulary.")
            print("\t " + str(lookup_key_1.encode(encoding="utf-8")))
            print("\t " + str(lookup_key_2.encode(encoding="utf-8")))
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

        if lookup_key in self.closest_concepts_cache:
            print("Serve answer from cache.")
            return self.closest_concepts_cache[lookup_key]


        if lookup_key in self.term_mapping:
            result = self.find_closest_lemmas_given_key(key=self.term_mapping[lookup_key], top=top)

        if result is None:
            result = "{}"

        self.closest_concepts_cache[lookup_key] = result
        return result


    def __take_second(self, element):
        """For sorting."""
        return element[1]

    def get_vector(self, lemma):
        lookup_key = self.__transform_string(lemma)
        if lookup_key in self.term_mapping:
            uri = self.term_mapping[lookup_key]

            if uri not in self.vectors:
                uri = self.redirects[uri]

            if uri is not None:
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

    def __parse_redirects(self, path_to_redirects):
        """
        Reads DBpedia redirects.

        Parameters
        ----------
        path_to_redirects

        Returns
        -------

        """
        result = {}
        with open(path_to_redirects, "r", encoding="utf-8") as redirects_file:
            for line in redirects_file:
                if line.startswith("#") or line == "":
                    continue
                token = line.split(sep=" ")
                source = token[0]
                target = token[2]
                source = self.__transform_tag(source)
                target = self.__transform_tag(target)
                result[source] = target
        return result


    def __transform_tag(self, tag):
        tag = tag.lstrip("<")
        tag = tag.rstrip(">")
        tag = tag.replace("http://dbpedia.org/resource/", "dbr:")
        return tag


    def analogy(self, a_is_to, b_like, c_to, topn=10):
        a_is_to_key = self.__link_term(a_is_to)
        print(a_is_to + " linked to " + a_is_to_key)
        b_like_key = self.__link_term(b_like)
        print(b_like + " linked to " + b_like_key)
        c_to_key = self.__link_term(c_to)
        print(c_to + " linked to " + c_to_key)

        if a_is_to_key is None or b_like_key is None or c_to_key is None:
            return None
        try:
            result = self.vectors.most_similar(positive=[c_to_key, a_is_to_key], negative=[b_like_key], topn=10)
        except KeyError:
            return None
        return result


    def __link_term(self, term):
        normalized_term = self.__transform_string(term)

        if normalized_term not in self.term_mapping:
            if normalized_term[0].islower():
                print("Could not find " + normalized_term)
                normalized_term = normalized_term[0].upper() + normalized_term[1:]
                print("Trying " + normalized_term)
                if normalized_term not in self.term_mapping:
                    print("Could not find " + term)
                    return None
                else:
                    return self.term_mapping[normalized_term]
        else:
            lookup_key = self.term_mapping[normalized_term]

        if lookup_key not in self.vectors.vocab:
            print("Lookup Key (" + lookup_key + ") not in vocabulary. Check redirects.")
            if lookup_key not in self.redirects:
                return None
            lookup_key = self.redirects[lookup_key]
            print("Lookup Key 1 redirects to: " + str(lookup_key.encode(encoding="utf-8")))
            return lookup_key
        else:
            return lookup_key


    def __str__(self):
        return "DBpedia Query Service"


def main():
    path_to_dbpedia_vectors = "/Users/janportisch/Documents/Language_Models/dbpedia/sg200_dbpedia_500_8_df_vectors.kv"
    path_to_dbpedia_entities = "/Users/janportisch/Documents/Language_Models/dbpedia/dbpedia_entities.txt"
    path_to_dbpedia_redirects = "/Users/janportisch/Documents/Research/DBpedia/redirects_en.ttl"
    # dbpedia_service = 0
    dbpedia_service = DBpediaQueryService(entity_file=path_to_dbpedia_entities, vector_file=path_to_dbpedia_vectors,
                                          redirect_file=path_to_dbpedia_redirects)
    print("Load complete. Run query.")
    for key, sim in dbpedia_service.analogy("Berlin", "Germany", "Paris"):
        print(str(key) + "   " + str(sim))

    for key, sim in dbpedia_service.analogy("Germany", "Europe", "China"):
        print(str(key) + "   " + str(sim))

    for key, sim in dbpedia_service.analogy("Merkel", "Germany", "France"):
        print(str(key) + "   " + str(sim))

    for key, sim in dbpedia_service.analogy("Ludwig van Beethoven", "Bonn", "Johann Sebastian Bach"):
        print(str(key) + "   " + str(sim))

    for key, sim in dbpedia_service.analogy("Ludwig van Beethoven", "Bonn", "Bill Clinton"):
        print(str(key) + "   " + str(sim))

if __name__ == "__main__":
    main()