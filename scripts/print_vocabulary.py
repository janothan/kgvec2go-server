import gensim
from gensim.models import KeyedVectors


vectors = KeyedVectors.load("/Users/janportisch/Documents/Language_Models/dbpedia/sg200_dbpedia_500_8_df_vectors.kv")

limit = 0
for word in vectors.vocab:
    if "dbr:" in word:
        print(word)
        limit += 1
        if limit > 100:
            break

#model = gensim.models.Word2Vec.load("/work/jportisc/Training_BabelNet_100_8_df/sg200_babelnet_100_8_df_mc1_updated")
#vectors = model.wv
#print("loaded")
#i = 0

#print("Vocabulary size: " + str(len(model.wv.vocab)))

#path_to_lemma_file = "/work/jportisc/EmbeddingServer/babelnet/babelnet_entities_en.txt"

error_counter = 0
success_counter = 0

#with open(path_to_lemma_file, errors='ignore') as lemma_file:
#    for lemma in lemma_file:
#        lemma = lemma.replace("\n", "")
#        lemma = lemma.replace("\r", "")
#        if lemma in vectors.vocab:
#            #print(lemma + " in vocabulary.")
#            success_counter += 1
#        else:
#            print(lemma)
#            error_counter += 1
#print("Errors " + str(error_counter))
#print("Success " + str(success_counter))
#
#with open("./new_entities_to_file.txt", "w", encoding="utf-8") as file_to_write:
#    for word in model.wv.vocab:
#        file_to_write.write(word + "\n")


#for word in model.wv.vocab:
#    i += 1
#    print(word)
#    if i == 20:
#        break