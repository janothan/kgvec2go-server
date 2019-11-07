import operator
from collections import namedtuple

from alod.alod_query_service import AlodQueryService
from scipy.stats import spearmanr
from collections import OrderedDict
from math import factorial

from babelnet.babelnet_query_service import BabelNetQueryService
from dbnary.dbnary_query_service import DbnaryQueryService
from dbpedia.dbpedia_query_service import DBpediaQueryService
from wordnet.wordnet_query_service import WordnetQueryService


class Evaluator:

    def __init__(self):
        pass

    def load_wordsim(self, path_to_wordsim):
        with open(path_to_wordsim) as file:
            result = []
            for line in file.readlines():
                line = line.rstrip('\n')
                result.append(line.split("\t"))
            return result

    def wordsim_spearman_rho(self, path_to_wordsim, service):
        wordsim = self.load_wordsim(path_to_wordsim)
        service_similarity = []
        wordsim_similarity = []
        for entry in wordsim:
            similarity = service.get_similarity(entry[0], entry[1])
            if similarity is None:
                print("ERROR: Not found: " + entry[0] + "   " + entry[1])
                service_similarity.append(0)
                wordsim_similarity.append(entry[2])
            else:
                service_similarity.append(similarity)
                wordsim_similarity.append(entry[2])
        return spearmanr(service_similarity, wordsim_similarity)

    def simlex_spearman_rho(self, path_to_simlex, service, nouns_only=False, use_pos=False):
        simlex = self.__load_simlex(path_to_simlex)
        service_similarity = []
        simlex_similarity = []
        number_of_entries_not_found = 0
        for entry in simlex:
            if nouns_only and entry[2] != "N":
                continue
            if use_pos:
                similarity = service.get_similarity(entry[0], entry[1], entry[2])
            else:
                similarity = service.get_similarity(entry[0], entry[1])
            if similarity is None:
                number_of_entries_not_found += 1
                print("ERROR: Not found: " + entry[0] + "   " + entry[1])
                service_similarity.append(0)
                simlex_similarity.append(entry[3])
            else:
                service_similarity.append(similarity)
                simlex_similarity.append(entry[3])
        print("Number of entries not found: " + str(number_of_entries_not_found))
        return spearmanr(service_similarity, simlex_similarity)


    def men_spearman_rho(self, path_to_men, service, nouns_only=False, use_pos=False):
        """

        Parameters
        ----------
        path_to_men : str
            the path to the file 'MEN_dataset_lemma_form_full'

        service
            The service to be evaluated.

        nouns_only
            Process only the 2005 noun-noun forms of the data set.

        use_pos
            Indicator whether the POS of the wordnet data set shall be used.

        Returns
        -------
        SpearmanrResult
            The spearman correlation.
        """

        men = self.__load_men(path_to_men)
        service_similarity = []
        men_similarity = []
        for entry in men:
            if nouns_only and (entry[1] != "n" or entry[3] != "n"):
                continue
            if use_pos:
                similarity = service.get_similarity(concept_1=entry[0], pos_1=entry[1], concept_2=entry[2], pos_2=entry[3])
            else:
                similarity = service.get_similarity(entry[0], entry[2])
            if similarity is None:
                print("ERROR: Not found: " + entry[0] + "   " + entry[2])
                service_similarity.append(0)
                men_similarity.append(entry[4])
            else:
                service_similarity.append(similarity)
                men_similarity.append(entry[4])
        return spearmanr(service_similarity, men_similarity)
        print(men)


    def __load_men(self, path_to_men):
        """Parses the MEN gold standard file into a processable structure.

        Parameters
        ----------
        path_to_men : str
            The path to the file 'MEN_dataset_lemma_form_full'

        Returns
        -------
        list
            a parsed list of tuples. One tuple respresents one line in the file.
        """
        with open(path_to_men) as file:
            result = []
            for line in file.readlines():
                line = line.rstrip('\n')
                intermediate_result = line.split(" ")
                result_line = []
                result_line.extend(intermediate_result[0].split("-"))
                result_line.extend(intermediate_result[1].split("-"))
                result_line.append(intermediate_result[2])
                result.append(result_line)
            return result

    def __load_simlex(self, path_to_simlex):
        """Parses the SimLex-999.txt file into a processable data structure.

        Parameters
        ----------
        path_to_simlex
            The path where the SIMLEX text file resides.

        Returns
        -------
        list
            a parsed list of tuples. One tuple represents one line in the file.
            [0] word 1
            [1] word 2
            [2] part of speech
            [3] Score in the range [0,10]
        """
        with open(path_to_simlex) as file:
            result = []
            for line in file.readlines():
                if line.startswith("word1"):
                    continue
                line = line.rstrip('\n')
                intermediate_result = line.split("\t")
                result.append((intermediate_result[0:4]))
            return result



    @staticmethod
    def sum_scores(list_of_borda_scores):
        GsBordaEntryResult = namedtuple('Entry', 'w1 w2 score')
        final_score_card = []
        for score_list in list_of_borda_scores:
            for entry in score_list:
                score_card_entry = Evaluator.get_entry_of_relative_score_for_borda(final_score_card, entry.w1, entry.w2)
                if score_card_entry != None:
                    final_score_card.remove(score_card_entry)
                    new_entry = GsBordaEntryResult(entry.w1, entry.w2, score_card_entry.score + entry.score)
                    final_score_card.append(new_entry)
                else:
                    final_score_card.append(entry)
        return final_score_card



    @staticmethod
    def get_relative_score_for_borda(score_map):
        # remove 0 values (exact 0 values are not found by system)
        descending_list = []
        for entry in score_map:
            if entry.sim != 0:
                descending_list.append(entry)

        print(descending_list)
        descending_list.sort(key=lambda e : e.sim, reverse=True)
        print(descending_list)

        GsBordaEntryResult = namedtuple('Entry', 'w1 w2 score')
        result = []
        position = 0
        length = len(descending_list)
        normalization_score = factorial(length)
        for entry in descending_list:
            result.append(GsBordaEntryResult(entry.w1, entry.w2, (length - position) / normalization_score))
            position += 1
        return result


    @staticmethod
    def get_entry_of_relative_score_for_borda(relative_score_for_borda, w1, w2):
        for entry in relative_score_for_borda:
            if entry.w1 == w1 and entry.w2 == w2:
                return entry
        return None

def main():
    evaluator = Evaluator()

    wordSim_353_similarity_gs = r"/work/jportisc/EmbeddingServer/gold_standards/wordsim_similarity_goldstandard.txt"
    simlex_gs = r"/work/jportisc/EmbeddingServer/gold_standards/SimLex-999.txt"
    men_gs = r"/work/jportisc/EmbeddingServer/gold_standards/MEN_dataset_lemma_form_full.txt"

    #babelnet_service = BabelNetQueryService('entity_file', model_file='', vector_file='')
    #print("WordSim-353 (BabelNet): " + str(evaluator.wordsim_spearman_rho(wordSim_353_similarity_gs, babelnet_service)))
    #print("SimLex-999 [all] (BabelNet): " + str(evaluator.simlex_spearman_rho(simlex_gs, babelnet_service, nouns_only=False, use_pos=True)))
    #print("SimLex-999 [nouns] (BabelNet): " + str(evaluator.simlex_spearman_rho(simlex_gs, babelnet_service, nouns_only=True, use_pos=False)))
    #print("MEN [all] (BabelNet): " + str(evaluator.men_spearman_rho(men_gs, babelnet_service, nouns_only=False, use_pos=True)))
    #print("MEN [nouns] (BabelNet): " + str(evaluator.men_spearman_rho(men_gs, babelnet_service, nouns_only=True, use_pos=False)))

    dbpedia_service = DBpediaQueryService(entity_file='/work/jportisc/Walk_Generation_dbpedia_100_8_df/cache/dbpedia_entities.txt', model_file='/work/jportisc/models/iteration_2/dbpedia/100_8/dbpedia_100_8_df')
    print("WordSim-353 (DBpedia): " + str(evaluator.wordsim_spearman_rho(wordSim_353_similarity_gs, dbpedia_service)))
    print("SimLex-999 [all] (DBpedia): " + str(evaluator.simlex_spearman_rho(simlex_gs, dbpedia_service, nouns_only=False, use_pos=False)))
    print("SimLex-999 [nouns] (DBpedia): " + str(evaluator.simlex_spearman_rho(simlex_gs, dbpedia_service, nouns_only=True, use_pos=False)))
    print("MEN [all] (DBpedia): " + str(evaluator.men_spearman_rho(men_gs, dbpedia_service, nouns_only=False, use_pos=False)))
    print("MEN [nouns] (DBpedia): " + str(evaluator.men_spearman_rho(men_gs, dbpedia_service, nouns_only=True, use_pos=False)))

    dbnary_service = DbnaryQueryService(entity_file="/work/jportisc/EmbeddingServer/dbnary/dbnary_entities.txt", model_file="/work/jportisc/models/iteration_2/wiktionary/without_vocab_loss/sg200_dbnary_500_8_df_all")
    print("WordSim-353 (DBnary): " + str(evaluator.wordsim_spearman_rho(wordSim_353_similarity_gs, dbnary_service)))
    print("SimLex-999 [all] (DBnary): " + str(evaluator.simlex_spearman_rho(simlex_gs, dbnary_service, nouns_only=False, use_pos=False)))
    print("SimLex-999 [nouns] (DBnary): " + str(evaluator.simlex_spearman_rho(simlex_gs, dbnary_service, nouns_only=True, use_pos=False)))
    print("MEN [all] (DBnary): " + str(evaluator.men_spearman_rho(men_gs, dbnary_service, nouns_only=False, use_pos=False)))
    print("MEN [nouns] (DBnary): " + str(evaluator.men_spearman_rho(men_gs, dbnary_service, nouns_only=True, use_pos=False)))

    alod_service = AlodQueryService(model_file="/work/jportisc/models/iteration_2/alod/100_4_df/alodc_df_100_4")
    print("WordSim-353 (ALOD): " + str(evaluator.wordsim_spearman_rho(wordSim_353_similarity_gs, alod_service)))
    print("SimLex-999 [all] (ALOD): " + str(evaluator.simlex_spearman_rho(simlex_gs, alod_service, nouns_only=False, use_pos=False)))
    print("SimLex-999 [nouns] (ALOD): " + str(evaluator.simlex_spearman_rho(simlex_gs, alod_service, nouns_only=True, use_pos=False)))
    print("MEN [all] (ALOD): " + str(evaluator.men_spearman_rho(men_gs, alod_service, nouns_only=False, use_pos=False)))
    print("MEN [nouns] (ALOD): " + str(evaluator.men_spearman_rho(men_gs, alod_service, nouns_only=True, use_pos=False)))

    wordnet_service = WordnetQueryService(entity_file='/work/jportisc/EmbeddingServer/wordnet/wordnet_entities.txt', model_file='/work/jportisc/models/iteration_2/wordnet/without_strings/sg200_wordnet_500_8_df_without_strings')
    print("WordSim-353 (WordNet): " + str(evaluator.wordsim_spearman_rho(wordSim_353_similarity_gs, wordnet_service)))
    print("SimLex-999 [all] (WordNet): " + str(evaluator.simlex_spearman_rho(simlex_gs, wordnet_service, nouns_only=False, use_pos=True)))
    print("SimLex-999 [nouns] (WordNet): " + str(evaluator.simlex_spearman_rho(simlex_gs, wordnet_service, nouns_only=True, use_pos=True)))
    print("MEN [all] (WordNet): " + str(evaluator.men_spearman_rho(men_gs, wordnet_service, nouns_only=False, use_pos=True)))
    print("MEN [nouns] (WordNet): " + str(evaluator.men_spearman_rho(men_gs, wordnet_service, nouns_only=True, use_pos=True)))


if __name__ == "__main__":
    main()




