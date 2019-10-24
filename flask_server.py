from flask import Flask, render_template

from dbnary.dbnary_query_service import DbnaryQueryService
from alod.alod_query_service import AlodQueryService
from wordnet.wordnet_query_service import WordnetQueryService

app = Flask(__name__)

@app.route('/index.html')
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

dbnary_service = DbnaryQueryService(entity_file="./dbnary/dbnary_500_8_pages/dbnary_entities.txt",
                             model_file="./dbnary/dbnary_500_8_pages/sg200_dbnary_500_8_pages")

wordnet_service = WordnetQueryService(entity_file='./wordnet/wordnet_500_8/wordnet_entities.txt',
                                         model_file='./wordnet/wordnet_500_8/sg200_wordnet_500_8')

alod_service = AlodQueryService(model_file="./alod/alod_500_4/sg200_alod_500_4")

@app.route('/rest/closest-concepts/<data_set>/<top_n>/<concept_name>', methods=['GET'])
def closest_concepts(data_set, top_n, concept_name):
    data_sets = ["wordnet", "wiktionary", "babelnet", "alod"]
    data_set = data_set.lower()
    if data_set not in data_sets:
        return None
    if data_set == 'wiktionary':
        print("Wiktionary query fired.")
        result = dbnary_service.find_closest_lemmas(concept_name, top_n)
        print(result)
        return result
    elif data_set == 'wordnet':
        print("Wordnet query fired.")
        result = wordnet_service.find_closest_lemmas(concept_name, top_n)
        print(result)
        return result
    elif data_set =="alod":
        print("ALOD Classic query fired.")
        result = alod_service.find_closest_lemmas(concept_name, top_n)
        print(result)
        return result
    return None

@app.route('/rest/get-vector/<data_set>/<concept_name>', methods=['GET'])
def get_vector(data_set, concept_name):
    data_sets = ["wordnet", "wiktionary", "babelnet", "alod"]
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
    return None

@app.route('/rest/get-similarity/<data_set>/<concept_name_1>/<concept_name_2>', methods=['GET'])
def get_similarity(data_set, concept_name_1, concept_name_2):
    data_sets = ["wordnet", "wiktionary", "babelnet", "alod"]
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
