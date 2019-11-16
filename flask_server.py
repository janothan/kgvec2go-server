from flask import Flask, render_template

from dbnary.dbnary_query_service import DbnaryQueryService
from alod.alod_query_service import AlodQueryService
from dbpedia.dbpedia_query_service import DBpediaQueryService
from wordnet.wordnet_query_service import WordnetQueryService

app = Flask(__name__)

print("Initiating Server...")

@app.route('/index.html')
@app.route("/")
def show_start_page():
    return render_template("query.html")

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

@app.route('/about.html')
def show_about_page():
    return render_template("about.html")

@app.route("/robots.txt")
def robots_txt():
    return render_template("robots.txt")


on_local = True


if on_local:
    print("Using local environment.")
    path_to_dbpedia_vectors = "/Users/janportisch/Documents/Language_Models/dbpedia/sg200_dbpedia_500_8_df_vectors.kv"
    path_to_dbpedia_entities = "/Users/janportisch/Documents/Language_Models/dbpedia/dbpedia_entities.txt"
    #dbpedia_service = DBpediaQueryService(entity_file=path_to_dbpedia_entities, vector_file=path_to_dbpedia_vectors)
    dbpedia_service = 0
    alod_service = 0
    wordnet_service = 0
    dbnary_service = 0
else:
    print("Using server environment.")

    # DBpedia linux
    #path_to_dbpedia_vectors = "/disk/dbpedia/sg200_dbpedia_500_8_df_vectors.kv"
    #path_to_dbpedia_entities = "/disk/dbpedia/dbpedia_entities.txt"

    # ALOD
    path_to_alod_vectors = "/disk/alod/sg200_alod_100_8_df_mc1_it3_vectors.kv"
    alod_service = AlodQueryService(vector_file=path_to_alod_vectors)

    # DBnary / Wiktionary
    path_to_dbnary_vectors = "/disk/dbnary/sg200_dbnary_100_8_df_mc1_it3_vectors.kv"
    path_to_dbnary_entities = "/disk/dbnary/dbnary_entities.txt"
    dbnary_service = DbnaryQueryService(entity_file=path_to_dbnary_entities, vector_file=path_to_dbnary_vectors)

    # WordNet
    #path_to_wordnet_vectors = "/disk/wordnet/sg200_wordnet_500_8_df_mc1_it3_vectors.kv"
    path_to_wordnet_vectors = "/disk/wordnet/sg200_dbnary_500_8_df_mc1_it3_reduced_vectors.kv"
    path_to_wordnet_entities = "/disk/wordnet/wordnet_entities.txt"
    wordnet_service = WordnetQueryService(entity_file=path_to_wordnet_entities, vector_file=path_to_wordnet_vectors, is_reduced_vector_file=True)


#wordnet_service = WordnetQueryService(entity_file='./wordnet/wordnet_500_8/wordnet_entities.txt',
#                                         model_file='./wordnet/wordnet_500_8/sg200_wordnet_500_8')
#
#

print("Server Initiated.")




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
        #print("Wiktionary get-vector query fired.")
        #result = dbnary_service.get_vector(concept_name)
        #print(result)
        #return result
        return None
    elif data_set == 'wordnet':
       #print("Wordnet get-vector query fired.")
       #result = wordnet_service.get_vector(concept_name)
       #print(result)
       #return result
       return None
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