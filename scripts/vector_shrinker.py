import gensim
import numpy as np
from gensim.models import KeyedVectors


def shrink_vectors(vectors, path_to_concept_file, file_to_write):
    concepts_to_be_kept = read_concept_file(path_to_concept_file)

    # determine ids that shall be deleted
    ids_to_trim = [vectors.vocab[w].index for w in vectors.vocab if w not in concepts_to_be_kept]

    # determine words that shall be deleted
    to_delete = [w for w in vectors.vocab if w not in concepts_to_be_kept]

    for w in to_delete:
        del vectors.vocab[w]

    vectors.vectors = np.delete(vectors.vectors, ids_to_trim, axis=0)
    #word_vectors.init_sims(replace=True)

    for i in sorted(ids_to_trim, reverse=True):
        del (vectors.index2word[i])

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

def test(vector_file):
    vectors_new = shrink_vectors(vectors=KeyedVectors.load(vector_file, mmap='r'), path_to_concept_file="./test_keep.txt", file_to_write="./model_shrinked.kv")
    vectors_old = KeyedVectors.load(vector_file, mmap='r')
    print("Length of old vectors: " + str(len(vectors_old.vocab)))
    print("Length of new vectors: " + str(len(vectors_new.vocab)))
    print()
    print("Europe vector same value: " + str(np.all(vectors_new["Europe"] == vectors_old["Europe"])))
    print("United vector same value: " + str(np.all(vectors_new["united"] == vectors_old["united"])))
    print()
    print("Vocabulary old vectors:")
    for w in vectors_old.vocab:
        print("\t" + w)
    print("Vocabulary new vectors:")
    for w in vectors_new.vocab:
        print("\t" + w)


def save_vector_file(path_to_model, path_to_vector_file):
    print("Parsing: " + path_to_model)
    model = gensim.models.Word2Vec.load(path_to_model)
    print("Model parsed. Writing vector file: " + path_to_vector_file)
    model.wv.save(path_to_vector_file)
    print("Vector file written.")


def main():
    old_vector_file_path = ''
    concepts_to_keep_file_path = ''
    file_to_write_file_path = ''

    # optional
    model_file_path = ''
    save_vector_file(model_file_path, old_vector_file_path)

    shrink_vectors(vectors=KeyedVectors.load(old_vector_file_path, mmap='r'), path_to_concept_file=concepts_to_keep_file_path, file_to_write=file_to_write_file_path)
    print("Done")


if __name__ == "__main__":
    main()