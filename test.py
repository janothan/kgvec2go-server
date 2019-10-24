from gensim.models import KeyedVectors
import gensim

#model = gensim.models.Word2Vec.load("./wordnet/wordnet_500_8/sg200_wordnet_500_8")
#model.wv.save("./wordnet/wordnet_500_8/sg200_wordnet_500_8_vector_file")

word_vectors = KeyedVectors.load("./wordnet/wordnet_500_8/sg200_wordnet_500_8_vector_file", mmap='r')
print(word_vectors.similarity("wn-lemma:object#object-n", "wn-lemma:exemption#exemption-n"))


