from flask import Flask, render_template, request
from ast import literal_eval
import logging

from dbnary.dbnary_query_service import DbnaryQueryService
from alod.alod_query_service import AlodQueryService
from dbpedia.dbpedia_query_service import DBpediaQueryService
from wordnet.wordnet_query_service import WordnetQueryService

logging.basicConfig(handlers=[logging.FileHandler(__file__ + '.log', 'w', 'utf-8'), logging.StreamHandler()], format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)

app = Flask(__name__)

logging.info("Initiating Server...")

@app.route('/index.html')
@app.route('/about.html')
@app.route("/")
def show_start_page():
    return render_template("about.html")

@app.route('/query.html')
def show_query_page():
    return render_template("query.html")

@app.route('/licenses.html')
def show_licenses_page():
    return render_template("licenses.html")

@app.route('/download.html')
def show_download_page():
    return render_template("download.html")

@app.route('/api.html')
def show_api_page():
    return render_template("api.html")

@app.route('/contact.html')
def show_about_page():
    return render_template("contact.html")

@app.route("/robots.txt")
def robots_txt():
    return render_template("robots.txt")


on_local = True


if on_local:
    logging.info("Using local environment.")

    logging.info("Init DBpediaQueryService")
    path_to_dbpedia_vectors = "/Users/janportisch/Documents/Data/KGvec2go_DBpedia_Optimized/sg200_dbpedia_500_8_df_vectors_reduced.kv"
    #path_to_dbpedia_entities = "/Users/janportisch/Documents/PhD/LREC_2020/Language_Models/dbpedia/dbpedia_entities.txt"
    path_to_dbpedia_redirects = "/Users/janportisch/Documents/PhD/LREC_2020/Language_Models/dbpedia/redirects_en.ttl"
    dbpedia_service = DBpediaQueryService(vector_file=path_to_dbpedia_vectors, redirect_file=path_to_dbpedia_redirects)
    logging.info("DBpediaQueryService Initialized.")

    #dbpedia_service = DBpediaQueryService(entity_file=path_to_dbpedia_entities, vector_file=path_to_dbpedia_vectors, redirect_file=path_to_dbpedia_redirects)
    alod_service = 0
    wordnet_service = 0

    logging.info("Init WordnetQueryService")
    path_to_wordnet_vectors = "/Users/janportisch/Documents/PhD/LREC_2020/Language_Models/wordnet/sg200_wordnet_500_8_df_mc1_it3_reduced_vectors.kv"
    path_to_wordnet_entities = "/Users/janportisch/Documents/PhD/LREC_2020/Language_Models/wordnet/wordnet_entities.txt"
    wordnet_service = WordnetQueryService(entity_file=path_to_wordnet_entities, vector_file=path_to_wordnet_vectors,
                                          is_reduced_vector_file=True)
    logging.info("WordnetQueryService initialized.")

    dbnary_service = 0
    #rdf_2_vec = jRDF2Vec()

    logging.info("KGvec2go Operational")

else:
    logging.info("Using server environment.")

    # DBpedia linux
    path_to_dbpedia_vectors = "/disk/dbpedia/sg200_dbpedia_500_8_df_vectors_reduced.kv"
    path_to_dbpedia_redirects = "/disk/dbpedia/redirects_en.ttl"
    dbpedia_service = DBpediaQueryService(vector_file=path_to_dbpedia_vectors, redirect_file=path_to_dbpedia_redirects)
    logging.info("DBpedia service initiated.")

    # ALOD
    path_to_alod_vectors = "/disk/alod/sg200_alod_100_8_df_mc1_it3_vectors.kv"

    #alod_service = 0
    alod_service = AlodQueryService(vector_file=path_to_alod_vectors)
    logging.info("ALOD service initiated.")


    # DBnary / Wiktionary
    path_to_dbnary_vectors = "/disk/dbnary/sg200_dbnary_100_8_df_mc1_it3_vectors.kv"
    path_to_dbnary_entities = "/disk/dbnary/dbnary_entities.txt"

    #dbnary_service = 0
    dbnary_service = DbnaryQueryService(entity_file=path_to_dbnary_entities, vector_file=path_to_dbnary_vectors)
    logging.info("Wiktionary service initiated.")

    # WordNet
    #path_to_wordnet_vectors = "/disk/wordnet/sg200_wordnet_500_8_df_mc1_it3_vectors.kv"
    #path_to_wordnet_vectors = "/disk/wordnet/sg200_dbnary_500_8_df_mc1_it3_reduced_vectors.kv"
    path_to_wordnet_model = "/disk/wordnet/sg200_wordnet_100_8_df_mc1_it3"
    path_to_wordnet_entities = "/disk/wordnet/wordnet_entities.txt"

    #wordnet_service = 0
    wordnet_service = WordnetQueryService(entity_file=path_to_wordnet_entities, model_file=path_to_wordnet_model, is_reduced_vector_file=False)
    logging.info("WordNet service initiated.")

    #rdf_2_vec = jRDF2Vec(jrdf_2_vec_directory="/mnt/disk/server/EmbeddingServer/jRDF2Vec/")
    #print("RDF2Vec Service initiated")

    logging.info("KGvec2go Operational")

#wordnet_service = WordnetQueryService(entity_file='./wordnet/wordnet_500_8/wordnet_entities.txt',
#                                         model_file='./wordnet/wordnet_500_8/sg200_wordnet_500_8')
#
#

# initialize jRDF2Vec

logging.info("Server Initiated.")



@app.route('/rest/rdf2vec-light/<data_set>/<walks>/<mode>/<dimension>', methods=['GET'])
def rdf2vec_light(data_set, walks, mode, dimension):
    # sanity check:
    if data_set.lower() != "dbpedia":
        print("Only DBpedia allowed")
        return None
    if request is None:
        print("none")
    entities = request.headers.get('entities')
    if entities is None:
        print("ERROR: Entities are missing in header.")
        return None
    entities = literal_eval(entities)
    result = rdf_2_vec.train_light(entities=entities, number_of_walks=walks, mode=mode, dimension=dimension)
    return result



@app.route('/rest/closest-concepts/<data_set>/<top_n>/<concept_name>', methods=['GET'])
def closest_concepts(data_set, top_n, concept_name):
    data_sets = ["wordnet", "wiktionary", "babelnet", "alod", "dbpedia"]
    data_set = data_set.lower()
    if data_set not in data_sets:
        return None
    if data_set == 'wiktionary':
        print("Wiktionary closest-concepts query fired.")
        result = dbnary_service.find_closest_lemmas(concept_name, top_n)
        print(result)
        return result
    elif data_set == 'wordnet':
        print("Wordnet closest-concepts query fired.")
        result = wordnet_service.find_closest_lemmas(concept_name, top_n)
        print(result)
        return result
    elif data_set == "alod":
        print("ALOD Classic closest-concepts query fired.")
        result = alod_service.find_closest_lemmas(concept_name, top_n)
        print(result)
        return result
    elif data_set == 'dbpedia':
        print("DBpedia closts-concepts query fired.")
        result = dbpedia_service.find_closest_lemmas(concept_name, top_n)
        print(result)
        return result
    return None


@app.route('/rest/get-vector/<data_set>/<concept_name>', methods=['GET'])
def get_vector(data_set, concept_name):
    data_sets = ["wordnet", "wiktionary", "babelnet", "alod", "dbpedia"]
    data_set = data_set.lower()
    if data_set not in data_sets:
        return None
    if data_set == 'wiktionary':
        print("Wiktionary get-vector query fired.")
        result = dbnary_service.get_vector(concept_name)
        print(result)
        return result
    elif data_set == 'wordnet':
        print("Wordnet get-vector query fired.")
        result = wordnet_service.get_vector(concept_name)
        print(result)
        return result
    elif data_set == 'alod':
        print("ALOD Classic get-vector query fired.")
        result = alod_service.get_vector(concept_name)
        print(result)
        return result
    elif data_set == 'dbpedia':
        print("DBpedia get-vector query fired.")
        result = dbpedia_service.get_vector(concept_name)
        print(result)
        return result
    return None


@app.route('/rest/get-similarity/<data_set>/<concept_name_1>/<concept_name_2>', methods=['GET'])
def get_similarity(data_set, concept_name_1, concept_name_2):
    data_sets = ["wordnet", "wiktionary", "babelnet", "alod", "dbpedia"]
    data_set = data_set.lower()
    if data_set not in data_sets:
        return None
    if data_set == 'wiktionary':
        print("Wiktionary get-vector query fired.")
        result = dbnary_service.get_similarity_json(concept_name_1, concept_name_2)
        print(result)
        return result
    elif data_set == 'wordnet':
       print("Wordnet get-vector query fired.")
       result = wordnet_service.get_similarity_json(concept_name_1, concept_name_2)
       print(result)
       return result
    elif data_set == 'alod':
        print("ALOD Classic get-similarity query fired.")
        result = alod_service.get_similarity_json(concept_name_1, concept_name_2)
        print(result)
        return result
    elif data_set == 'dbpedia':
        print("DBpedia get-similarity query fired.")
        result = dbpedia_service.get_similarity_json(concept_name_1, concept_name_2)
        print(result)
        return result


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)