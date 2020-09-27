import gensim
import logging
import os
import gzip
import numpy as np
from gensim.models import KeyedVectors

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', filename='log.out', level=logging.INFO)


def save_vector_file(path_to_model, path_to_vector_file):
    print("Parsing: " + path_to_model)
    model = gensim.models.Word2Vec.load(path_to_model)
    print("Model parsed. Writing vector file: " + path_to_vector_file)
    model.wv.save(path_to_vector_file)
    print("Vector file written.")


def shrink_vectors(vectors, path_to_concept_file, file_to_write):
    """Writes a new, reduced vector file with the given concepts.

    Parameters
    ----------
    vectors : KeyedValue Object
        Can be obtained from a file through: KeyedVectors.load(vector_file_name, mmap='r').
    path_to_concept_file : str
        The path to the file containing the concepts that shall be kept.
    file_to_write : str
        Reduced vector file that will be written. This parameter contains the file path.

    Returns
    -------

    """
    concepts_to_be_kept = read_concept_file(path_to_concept_file)
    print("File with concepts that shall be kept read.")

    new_vectors = []
    new_vocab = {}
    new_index2entity = []
    new_vectors_norm = []

    # dummy call
    vectors.most_similar(next(iter(vectors.vocab.keys())))

    for i in range(len(vectors.vocab)):
        word = vectors.index2entity[i]
        vec = vectors.vectors[i]
        vocab = vectors.vocab[word]
        vec_norm = vectors.vectors_norm[i]
        if i % 10000 == 0:
            print("Finished " + str(i) + " out of " + str(len(vectors.vocab)))
        if word in concepts_to_be_kept:
                vocab.index = len(new_index2entity)
                new_index2entity.append(word)
                new_vocab[word] = vocab
                new_vectors.append(vec)
                new_vectors_norm.append(vec_norm)

    vectors.vocab = new_vocab
    vectors.vectors = np.array(new_vectors)
    vectors.index2entity = np.array(new_index2entity)
    vectors.index2word = np.array(new_index2entity)
    vectors.vectors_norm = np.array(new_vectors_norm)
    vectors.save(file_to_write)
    return vectors

def read_concept_file(path_to_concept_file):
    result = []
    with open(path_to_concept_file, errors='ignore') as concept_file:
        for lemma in concept_file:
            lemma = lemma.replace("\n", "").replace("\r", "")
            result.append(lemma)
    print("File read.")
    return result

def train(path_to_sentences, file_to_write):

    # a memory-friendly iterator
    class MySentences(object):
        def __init__(self, dirname):
            self.dirname = dirname

        def __iter__(self):
            for fname in os.listdir(self.dirname):
                print("Processing file: " + fname)
                try:
                    for line in gzip.open(os.path.join(self.dirname, fname), mode='rt', encoding="utf-8"):
                        line = line.rstrip('\n')
                        words = line.split(" ")
                        yield words
                except Exception:
                    logging.error("Failed reading file:")
                    logging.error(fname)


    logging.info("Starting Process")

    # init
    sentences = MySentences(path_to_sentences)
    logging.info('Sentences Object successfully initialized.')

    # sg 200
    model = gensim.models.Word2Vec(size=200, workers=20, window=5, sg=1, negative=25, iter=5, sentences=sentences)
    #print('Gensim Model SG 200 initialized. Building vocabulary...')

    # Build Vocabulary
    #model.build_vocab(sentences)
    #print('Vocabulary successfully built.')

    #print('Training SG 200')
    #model.train(sentences=sentences, total_examples=model.corpus_count, epochs=model.epochs)

    logging.info('SG 200 trained - Saving...')
    model.save(file_to_write)
    logging.info('SG 200 saved.')

    print("Training DONE")


def main():
    """
    path_to_sentences = r'./walks'
    file_to_write = r'./sg200_dbnary_utf8_500_8_df_mc5'
    path_to_concepts_file = r"./cache/dbnary_entities.txt"
    train(path_to_sentences, file_to_write)

    # save vectors
    print("Saving vectors.")
    vector_file_name = file_to_write + "_vectors.kv"
    save_vector_file(file_to_write, vector_file_name)
    """

    print("Shrinking vectors")
    vector_file_name = "./sg200_dbpedia_500_8_df_vectors.kv"
    path_to_concepts_file = "./dbpedia_entities.txt"
    file_to_write = "./sg200_dbpedia_500_8_df_vectors_reduced.kv"
    shrink_vectors(KeyedVectors.load(vector_file_name, mmap='r'), path_to_concept_file=path_to_concepts_file,
                   file_to_write=file_to_write)


if __name__ == "__main__":
    main()
