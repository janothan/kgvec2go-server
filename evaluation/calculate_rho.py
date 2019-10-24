from collections import namedtuple

from alod.alod_query_service import AlodQueryService
from scipy.stats import spearmanr

from babelnet.babelnet_query_service import BabelNetQueryService
from dbnary.dbnary_query_service import DbnaryQueryService
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
            else:
                service_similarity.append(similarity)
                wordsim_similarity.append(entry[2])
        return spearmanr(service_similarity, wordsim_similarity)

    def simlex_spearman_rho(self, path_to_simlex, service, nouns_only=False, use_pos=False):
        simlex = self.__load_simlex(path_to_simlex)
        service_similarity = []
        simlex_similarity = []
        for entry in simlex:
            if nouns_only and entry[2] != "N":
                continue
            if use_pos:
                similarity = service.get_similarity(entry[0], entry[1], entry[2])
            else:
                similarity = service.get_similarity(entry[0], entry[1])
            if similarity is None:
                print("ERROR: Not found: " + entry[0] + "   " + entry[1])
            else:
                service_similarity.append(similarity)
                simlex_similarity.append(entry[3])
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

def main():
    evaluator = Evaluator()
    # alod_service = AlodQueryService(vector_file="./alod/alod_500_4/sg200_alod_500_4")

    # dbnary_service = DbnaryQueryService(entity_file="../dbnary/dbnary_500_4_df_pages/dbnary_entities.txt",
    #                                   model_file="../dbnary/dbnary_500_4_df_pages/sg200_dbnary_pages_500_4_df")

    # wordnet_service = WordnetQueryService(entity_file='../wordnet/wordnet_500_4_df/wordnet_entities.txt',
    #                                       model_file='../wordnet/wordnet_500_4_df/sg200_wordnet_500_4_df')

    babelnet_service = BabelNetQueryService('entity_file', model_file='', vector_file='')

    print("WordSim-353: " + str(evaluator.wordsim_spearman_rho(r"C:\Users\D060249\Documents\Vector_Evaluation\wordsim353_sim_rel\wordsim_similarity_goldstandard.txt", babelnet_service)))
    print("SimLex-999: " + str(evaluator.simlex_spearman_rho(r"C:\Users\D060249\Downloads\SimLex-999\SimLex-999.txt", babelnet_service, nouns_only=False, use_pos=False)))
    print("MEN: " + str(evaluator.men_spearman_rho(r"C:\Users\D060249\Downloads\MEN\MEN\MEN_dataset_lemma_form_full", babelnet_service,
                                     nouns_only=False, use_pos=False)))

if __name__ == "__main__":
    main()




