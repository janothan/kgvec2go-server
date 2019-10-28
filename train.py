# import modules; set up logging
import gensim
import logging
import os
import gzip

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', filename='word2vec_log.out', level=logging.INFO)

def main():

    # define the path to the sentences below
    path_to_sentences = r'/Users/janportisch/IdeaProjects/Walk-Generator/walks/wordnet_500_8_df'

    # a memory-friendly iterator
    class MySentences(object):
        def __init__(self, dirname):
            self.dirname = dirname

        def __iter__(self):
            for fname in os.listdir(self.dirname):
                print("Processing file: " + fname)
                try:
                    for line in gzip.open(os.path.join(self.dirname, fname), mode='rt', errors='ignore'):
                        line = line.rstrip('\n')
                        words = line.split(" ")
                        yield words
                except Exception:
                    print("Failed reading file:")
                    print(fname)


    print("Starting Process")

    # init
    sentences = MySentences(path_to_sentences)
    print('Sentences Object successfully initialized.')

    # sg 200
    model = gensim.models.Word2Vec(size=200, workers=10, window=5, sg=1, negative=25, iter=5)
    print('Gensim Model SG 200 initialized. Building vocabulary...')

    # Build Vocabulary
    model.build_vocab(sentences)
    print('Vocabulary successfully built.')

    print('Training SG 200')
    sg200name = 'sg200_wordnet_500_8_df_with_strings'
    model.train(sentences=sentences, total_examples=model.corpus_count, epochs=model.epochs)

    print('SG 200 trained - Saving...')
    model.save(sg200name)
    # rewrite_model_for_java_gzipped(path_to_model=sg200name, path_to_output_file=(sg200name + "_java.gz"))
    print('SG 200 saved.')

    # cbow 200 model
    # model_cbow200 = gensim.models.Word2Vec(size=200, workers=5, window=2, sg=0, iter=5, cbow_mean=1, alpha=0.05)
    # model_cbow200.reset_from(model)

    # sg 500 model
    # model_sg500 = gensim.models.Word2Vec(size=500, workers=5, window=2, sg=1, negative=25, iter=5)
    # model_sg500.reset_from(model)

    # cbow 500 model
    # model_cbow500 = gensim.models.Word2Vec(size=500, workers=5, window=2, sg=0, iter=5, cbow_mean=1, alpha=0.05)
    # model_cbow500.reset_from(model)

    del model

    # print('Training CBOW 200.')
    # cbow_200_name = 'cobw_200'
    # model_cbow200.train(sentences=sentences, total_examples=model_cbow200.corpus_count, epochs=model_cbow200.iter)
    # print('CBOW 200 trained - Saving...')
    # model_cbow200.save(cbow_200_name)
    # rewrite_model_for_java_gzipped(path_to_model=cbow_200_name, path_to_output_file=(cbow_200_name + "_java.gz"))
    # print('CBOW 200 saved.')

    # del model_cbow200
    # print('Dimension 200 completed. Next: Dimesnion 500.')

    # print('Training SG 500')
    # sg500_name = 'sg_500'
    # model_sg500.train(sentences=sentences, total_examples=model_sg500.corpus_count, epochs=model_sg500.iter)
    # print('SG 500 trained.')
    # model_sg500.save(sg500_name)
    # rewrite_model_for_java_gzipped(path_to_model=sg500_name, path_to_output_file=(sg500_name + "_java.gz"))
    # print('SG 500 saved.')
    # del model_sg500

    # print('Training CBOW 500')
    # cbow500_name = 'DB2Vec_cbow_500_classic_100_8_no_reverse_window5'
    # model_cbow500.train(sentences=sentences, total_examples=model_cbow500.corpus_count, epochs=model_cbow500.iter)
    # print('SG 500 trained')
    # model_cbow500.save(cbow500_name)
    # rewrite_model_for_java_gzipped(path_to_model=cbow500_name, path_to_output_file=(cbow500_name + "_java.gz"))
    # del model_cbow500

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
