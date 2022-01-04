import gensim
import numpy as np
from gensim.models import KeyedVectors


def shrink_vectors_new(vectors, path_to_concept_file, file_to_write):
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


# def shrink_vectors_old(vectors, path_to_concept_file, file_to_write):
#    concepts_to_be_kept = read_concept_file(path_to_concept_file)
#    print("File with concepts that shall be kept read.")
#
#    # determine ids that shall be deleted
#    ids_to_trim = [vectors.vocab[w].index for w in vectors.vocab if w not in concepts_to_be_kept]
#    print("IDs that have to be trimmed determined.")
#
#    # determine words that shall be deleted
#    to_delete = [w for w in vectors.vocab if w not in concepts_to_be_kept]
#    print("Words that have to be deleted from the vocabulary determined.")
#
#    for w in to_delete:
#        del vectors.vocab[w]
#    print("Words delted.")
#
#    vectors.vectors = np.delete(vectors.vectors, ids_to_trim, axis=0)
#    print("Vectors deleted.")
#    #word_vectors.init_sims(replace=True)
#
#    for i in sorted(ids_to_trim, reverse=True):
#        del (vectors.index2word[i])
#
#    print("Writing new vector file.")
#    vectors.save(file_to_write)
#    print("New (shrinked) vector file written.")
#    return vectors


def read_concept_file(path_to_concept_file):
    result = []
    with open(path_to_concept_file, errors="ignore") as concept_file:
        for lemma in concept_file:
            lemma = lemma.replace("\n", "").replace("\r", "")
            result.append(lemma)
    print("File read.")
    return result


def test(vector_file):
    vectors_new = shrink_vectors_new(
        vectors=KeyedVectors.load(vector_file, mmap="r"),
        path_to_concept_file="./test_keep.txt",
        file_to_write="./model_shrinked.kv",
    )
    vectors_old = KeyedVectors.load(vector_file, mmap="r")
    print("Length of old vectors: " + str(len(vectors_old.vocab)))
    print("Length of new vectors: " + str(len(vectors_new.vocab)))
    print()
    print(
        "Europe vector same value: "
        + str(np.all(vectors_new["Europe"] == vectors_old["Europe"]))
    )
    print(
        "United vector same value: "
        + str(np.all(vectors_new["united"] == vectors_old["united"]))
    )
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
    old_vector_file_path = "./sg200_dbpedia_100_8_df_mc1_updated_vectors.kv"
    concepts_to_keep_file_path = (
        "/work/jportisc/Walk_Generation_dbpedia_100_8_df/cache/dbpedia_entities.txt"
    )
    file_to_write_file_path = "./sg200_dbpedia_100_8_df_mc1_updated__reduced_vectors.kv"

    # optional
    model_file_path = "./sg200_dbpedia_100_8_df_mc1_updated"
    save_vector_file(model_file_path, old_vector_file_path)

    shrink_vectors_new(
        vectors=KeyedVectors.load(old_vector_file_path, mmap="r"),
        path_to_concept_file=concepts_to_keep_file_path,
        file_to_write=file_to_write_file_path,
    )
    # test("./test_model_vectors.kv")
    print("Done")


if __name__ == "__main__":
    main()
