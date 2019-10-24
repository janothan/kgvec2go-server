import gensim

model = gensim.models.Word2Vec.load('./sg200_dbnary_100_8')
all_lemmas = []

def main():
    print("Start")
    read_lemmas("./dbnary_entities.txt")

    find_closest_lemmas('http://kaiko.getalp.org/dbnary/eng/famous__Adjective__1', 10)
    print("End")

def read_lemmas(path_to_lemma_file):
    with open(path_to_lemma_file, errors='ignore') as lemma_file:
        for lemma in lemma_file:
            all_lemmas.append(lemma.replace("\n", ""))
    return all_lemmas


def find_closest_lemmas(lemma, top):
    result = []
    for concept in all_lemmas:
        result.append((concept, model.wv.similarity(lemma, concept)))
    result.sort(key=take_second, reverse=True)
    print(result[:10])

def take_second(element):
    return element[1]

main()