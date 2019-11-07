# import modules; set up logging
import gensim
import logging
import os
import gzip

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', filename='word2vec_log.out', level=logging.INFO)

def main():

    # define the path to the sentences below
    path_to_sentences = r'/work/jportisc/Walk_Generation_babelnet_100_8_df_mt/walks_df_babelnet_100_en/'
    sg200name = 'sg200_babelnet_100_8_df_mc1_updated'


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
    model = gensim.models.Word2Vec(size=200, workers=20, sample=0, min_count=1, window=5, sg=1, negative=25, iter=5, sentences=sentences)
    #print('Gensim Model SG 200 initialized. Building vocabulary...')

    # Build Vocabulary
    #model.build_vocab(sentences)
    #print('Vocabulary successfully built.')

    #print('Training SG 200')
    #model.train(sentences=sentences, total_examples=model.corpus_count, epochs=model.epochs)

    logging.info('SG 200 trained - Saving...')
    model.save(sg200name)
    logging.info('SG 200 saved.')

    print("DONE")


'''
This method rewrites a given word2vec model in a Java-friendly format. The Java project can consume the resulting file.
File Structure:
- 1 concept per line
- concept <space> <vector-components space separated>
'''
def rewrite_model_for_java_gzipped(path_to_model, path_to_output_file):
    print('Starting Rewriting Model for Java')
    model = gensim.models.Word2Vec.load(path_to_model)
    content_to_write = []

    for concept in model.wv.vocab:
        resultline = concept
        for element in model[concept]:
            resultline = resultline + " " + str(element)
        content_to_write.append(resultline)

    outputFile = gzip.open(path_to_output_file, 'wb')
    for line in content_to_write:
        outputFile.write((line + "\n").encode('utf-8'))
    outputFile.close()
    print(str(len(content_to_write)) + " concepts written.")
    print("Model for Java rewritten.")


main()
